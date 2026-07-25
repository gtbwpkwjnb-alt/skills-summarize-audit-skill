# 上下文压力评估 v1.0

> v9.0.0 新增。服务能力四「生态综合评估」的 4.3 子能力。
> 估算已安装 skill + MCP + agent 对 LLM context window 的占用，给出精简建议。

## 一、为什么需要上下文压力评估

LLM 的 context window 是有限资源（典型 200K tokens）。已安装的工具会通过多种方式占用 context：
1. **Skill description 注入**：每个 skill 的 frontmatter description 进入 system prompt
2. **MCP tool schema 注入**：每个 MCP 暴露的 tool schema 进入 system prompt
3. **Agent profile 注入**：每个 sub-agent 的 description 进入主模型可选项
4. **Tool list 注入**：所有可用工具的名称和参数定义

过多已安装但未使用的工具会：
- **挤占有效 context**：留给实际任务的 token 减少
- **增加选择噪声**：LLM 在众多工具中选择困难
- **降低响应质量**：context 中充斥无关信息

## 二、Token 估算公式

### 2.1 Skill description 注入估算

> **注入策略（observed，2026-07-25 实测）**：从 ZCode transcript 的 `model_request` 事件中确认，ZCode 注入的是 **frontmatter description 字段**（不是完整 SKILL.md），格式为 `- <name>: <description> (file: <path>)`。实测 8 个 skill 的注入块总大小 4184 chars / ~1138 tokens，与下述公式估算一致。

```python
def estimate_skill_description_tokens(skills_dir: Path) -> dict:
    """
    每个 skill 的注入大小估算。
    ZCode 注入策略（observed，从 transcript 实测）：仅 frontmatter description 字段。
    格式：'- <name>: <description> (file: <path>)'
    不注入完整 SKILL.md（按需 Read）。
    """
    total = 0
    per_skill = {}
    for skill_md in skills_dir.glob("*/SKILL.md"):
        # 提取 frontmatter description
        text = skill_md.read_text(encoding="utf-8")
        frontmatter = extract_frontmatter(text)
        desc = frontmatter.get("description", "")
        # 注入格式开销：'- name: desc (file: path)\n' 约 +30 chars
        name = skill_md.parent.name
        injected_text = f"- {name}: {desc} (file: {skill_md})"
        # 中文按 chars/1.8，英文按 chars/4 估算 token
        zh_chars = len(re.findall(r"[\u4e00-\u9fa5]", injected_text))
        en_chars = len(injected_text) - zh_chars
        tokens = int(zh_chars / 1.8 + en_chars / 4)
        per_skill[skill_md.parent.name] = tokens
        total += tokens
    return {"total": total, "per_skill": per_skill}
```

### 2.2 MCP tool schema 注入估算

```python
def estimate_mcp_schema_tokens(mcp_config: dict, mcp_specs: dict) -> dict:
    """
    每个 MCP 的 schema 大小估算。
    数据源：mcp-marketplaces.md 提供的工具计数 + Reasonix mcp/*.json 的实际 schema 缓存。
    """
    total = 0
    per_server = {}
    for server in mcp_config.get("mcpServers", {}):
        # 每个 tool 的 schema 约 200-500 token（包含参数定义）
        tool_count = mcp_specs.get(server, {}).get("tool_count", 10)
        avg_tokens_per_tool = 300
        server_tokens = tool_count * avg_tokens_per_tool
        per_server[server] = {"tools": tool_count, "tokens": server_tokens}
        total += server_tokens
    return {"total": total, "per_server": per_server}
```

### 2.3 Agent profile 注入估算

```python
def estimate_agent_profile_tokens(agents_dir: Path) -> dict:
    """每个 sub-agent profile 的注入大小。"""
    total = 0
    per_agent = {}
    for profile_md in agents_dir.glob("*.md"):
        # profile.md 全文注入（描述 + 职责 + 技能优先）
        text = profile_md.read_text(encoding="utf-8")
        zh_chars = len(re.findall(r"[\u4e00-\u9fa5]", text))
        en_chars = len(text) - zh_chars
        tokens = int(zh_chars / 1.8 + en_chars / 4)
        per_agent[profile_md.stem] = tokens
        total += tokens
    return {"total": total, "per_agent": per_agent}
```

## 三、压力四级阈值

基于 200K context window（典型 LLM）：

| 等级 | 工具注入占比 | 留给任务 | 标识 | 处置 |
|---|---|---|---|---|
| 🟢 绿 | < 5% (< 10K tok) | 充足 | `low_pressure` | 无需干预 |
| 🟡 黄 | 5-10% (10-20K tok) | 良好 | `moderate_pressure` | 关注，定期清理 |
| 🟠 橙 | 10-20% (20-40K tok) | 偏紧 | `high_pressure` | 建议精简 |
| 🔴 红 | > 20% (> 40K tok) | 不足 | `critical_pressure` | 必须精简 |

## 四、精简优先级算法

当压力达到橙或红时，按以下优先级精简：

```python
def prioritize_pruning(
    skill_usage: dict,        # 从 extract_usage_signals.py
    mcp_usage: dict,
    profile_alignment: dict,  # 从 audit 的 skill_scores
    injection_sizes: dict     # 各工具的 token 占用
) -> list[dict]:
    """
    返回精简候选清单，按"低使用 × 低匹配 × 高占用"排序。
    """
    candidates = []
    for skill_id, tokens in injection_sizes.get("per_skill", {}).items():
        usage = skill_usage.get(skill_id, {"invocations": 0})
        alignment = profile_alignment.get(skill_id, 0)
        # 精简价值 = 低使用 + 低匹配 + 高占用
        prune_value = (
            (1 - min(1, usage["invocations"] / 10)) * 0.4 +  # 使用越少越该精简
            (1 - alignment / 10) * 0.3 +                     # 匹配越低越该精简
            (tokens / 1000) * 0.3                             # 占用越大越该精简
        )
        candidates.append({
            "target": skill_id,
            "type": "skill",
            "tokens": tokens,
            "usage": usage["invocations"],
            "alignment": alignment,
            "prune_value": round(prune_value, 2),
            "suggestion": "hide" if prune_value > 0.5 else "review"
        })
    return sorted(candidates, key=lambda x: x["prune_value"], reverse=True)
```

## 五、输出格式

```json
{
  "context_pressure_assessment": {
    "total_injection_tokens": 18450,
    "context_window_assumed": 200000,
    "pressure_percent": 9.2,
    "grade": "moderate_pressure",
    "breakdown": {
      "skills": {"total_tokens": 4500, "count": 13},
      "mcp": {"total_tokens": 12500, "count": 7, "per_server": {...}},
      "agents": {"total_tokens": 1450, "count": 11}
    },
    "pruning_candidates": [
      {
        "target": "grill-with-docs",
        "type": "skill",
        "tokens": 280,
        "usage": 0,
        "alignment": 0,
        "prune_value": 0.84,
        "suggestion": "hide"
      }
    ],
    "data_source": {
      "skills": "observed (SKILL.md frontmatter)",
      "mcp": "estimated (tool_count * 300)",
      "agents": "observed (profile.md size)",
      "context_window": "assumed (200K, not measured)"
    }
  }
}
```

## 六、数据支撑契约

| 字段 | 状态 | 说明 |
|---|---|---|
| `total_injection_tokens` | estimated | 基于公式的粗估，非实测 |
| `pressure_percent` | estimated | 基于 assumed context_window |
| `grade` | inferred | 基于阈值的分级 |
| `pruning_candidates` | inferred | 基于使用+匹配+占用的加权 |
| `usage` | observed | 来自 transcript 提取 |
| `alignment` | observed | 来自画像匹配 |

## 七、与 v8 inventory_analysis 的关系

v8 的 `inventory_analysis` 仅按安装项数量推断压力（>=12 高）。本文件用真实 token 估算替代，更准确：
- v8: `context_pressure = "高" if items >= 12`（粗略）
- v9: `context_pressure = "high" if estimated_tokens > 20000`（基于占用）

## 八、维护

- 当 ZCode 公布实际注入策略时，更新估算公式
- context_window 假设值可通过 `.data/context-window.json` 覆盖
- tool schema 平均 token 可通过实测校准（采样真实 system prompt）
