# Agent 调用歧义检测 v1.0

> v9.0.0 新增。服务能力四「生态综合评估」的 4.2 子能力。
> 检测 11 种 sub-agent 之间的能力重叠、调用频率分布、误派单风险。

## 一、为什么需要 Agent 调用歧义检测

主模型派单时基于「任务特征 → sub-agent 能力」的映射。当多个 agent 能力高度重叠时：
1. **误派单**：任务被分给次优 agent，浪费 token 和时间
2. **责任模糊**：任务失败时不知道是哪个 agent 的问题
3. **冗余配置**：多个 agent 做同一件事，增加 context 压力

ZCode 当前提供 11 种 sub-agent（见主 system prompt），它们的能力描述存在自然重叠（如 research-worker 与 Explore 都做调研）。

## 二、Agent 能力维度提取

### 2.1 输入数据源

每个 sub-agent 的能力信息来自：
- **`profileSnapshot.description`**：角色描述文本（从 `metadata.json` 提取）
- **`profileSnapshot.tools`**：该 agent 可用的工具列表
- **`profileSnapshot.model`**：使用的模型（决定能力上限）

### 2.2 能力维度映射算法

从 description 提取能力关键词，映射到 `capability-dimensions.yaml` 的 14 维度：

```python
def extract_agent_capabilities(profile_snapshot: dict) -> dict[str, int]:
    """
    返回 {dimension_id: level}。
    level 来自关键词命中数和工具类型推断。
    """
    desc = (profile_snapshot.get("description") or "").lower()
    tools = profile_snapshot.get("tools", [])
    
    capabilities = {}
    for dim in load_capability_dimensions():
        # 命中关键词得 +5
        keyword_hits = sum(1 for kw in dim["keywords"] if kw in desc)
        # 工具类型推断得 +3
        tool_match = infer_tools_to_dimension(tools, dim["id"])
        level = min(10, keyword_hits * 5 + tool_match * 3)
        if level > 0:
            capabilities[dim["id"]] = level
    return capabilities
```

### 2.3 ZCode 11 种 sub-agent 的能力基线（基于描述推断）

| Agent | 主要能力维度 | 推断 level |
|---|---|---|
| **general-purpose** | 通用全维度 | 多维 5-7 |
| **Explore** | research, file-ops, web-search | 8/7/6 |
| **data-worker** | file-ops, integration | 8/6 |
| **docs-worker** | file-ops | 7 |
| **implementation-worker** | code-analysis, file-ops | 8/7 |
| **test-worker** | code-analysis, file-ops | 7/6 |
| **quality-expert** | skill-audit, code-analysis | 8/7 |
| **security-expert** | skill-audit | 7 |
| **solution-architect** | reasoning, code-analysis | 9/7 |
| **research-worker** | research, web-search | 9/8 |
| **glm-adversarial-reviewer** | reasoning, skill-audit | 8/7 |

## 三、两两 Overlap 计算

### 3.1 Jaccard 系数（能力维度层）

```python
def agent_capability_overlap(a: dict, b: dict) -> float:
    """返回 0-1 的 Jaccard 系数：共享维度 / 并集维度。"""
    dims_a = set(a.keys())
    dims_b = set(b.keys())
    if not dims_a and not dims_b:
        return 0.0
    intersection = dims_a & dims_b
    union = dims_a | dims_b
    return len(intersection) / len(union) if union else 0.0
```

### 3.2 加权 Overlap（考虑 level 强度）

```python
def weighted_overlap(a: dict, b: dict) -> float:
    """同时考虑维度重叠和 level 相似度。"""
    common = set(a.keys()) & set(b.keys())
    if not common:
        return 0.0
    # 共享维度上的 level 差异越小越冲突
    diffs = [abs(a[d] - b[d]) for d in common]
    avg_diff = sum(diffs) / len(diffs)
    similarity = 1 - (avg_diff / 10)  # 0-1
    return (len(common) / len(set(a) | set(b))) * similarity
```

## 四、调用频率分布（从 transcript 提取）

数据源：`extract_usage_signals.py` 的 `agent_dispatch_stats`。

```python
def dispatch_distribution(signals: dict) -> dict[str, dict]:
    """返回每个 profile 的调用次数、占比、平均 token。"""
    stats = signals.get("agent_dispatch_stats", [])
    total = sum(s["dispatch_count"] for s in stats)
    return {
        s["profile_id"]: {
            "count": s["dispatch_count"],
            "share": s["dispatch_count"] / total if total else 0,
            "avg_tokens": s["avg_tokens"],
        }
        for s in stats
    }
```

## 五、误派单风险等级

### 5.1 风险计算

```python
def dispatch_risk(overlap: float, freq_a: float, freq_b: float) -> tuple[str, str]:
    """
    返回 (risk_level, reason)。
    高 overlap + 调用频次差异大 = 高风险（高频 agent 可能错派给低频 agent）。
    """
    freq_diff = abs(freq_a - freq_b)
    if overlap >= 0.7 and freq_diff >= 0.3:
        return ("critical", f"能力重叠 {overlap:.0%}，但调用频次差异 {freq_diff:.0%}，存在误派单风险")
    if overlap >= 0.5 and freq_diff >= 0.2:
        return ("warning", f"能力部分重叠 {overlap:.0%}，建议明确边界")
    return ("ok", "")
```

### 5.2 风险等级

| 等级 | 触发条件 | 处置 |
|---|---|---|
| 🔴 致命 | overlap ≥ 0.7 AND 频次差 ≥ 0.3 | 必须合并或拆分 |
| 🟡 严重 | overlap ≥ 0.5 AND 频次差 ≥ 0.2 | 明确边界或重命名 |
| 🟢 正常 | 其他 | 无需干预 |

## 六、合并/拆分建议模板

### 6.1 合并建议（A 类）

当两个 agent 高 overlap 且调用频次相近：
```
建议合并：{agent_a} 和 {agent_b}
理由：能力重叠 {overlap:.0%}，调用频次相近（{freq_a:.0%} vs {freq_b:.0%}）
合并后角色名：<建议名>
合并后职责：<合并后的描述>
执行：用户应修改 .zcode/agents/<profile>.md 合并职责描述
```

### 6.2 边界澄清建议（B 类）

当两个 agent 中等 overlap：
```
建议明确边界：{agent_a} 和 {agent_b}
重叠维度：<列出共享维度>
建议分工：
  - {agent_a} 负责 <独占维度>
  - {agent_b} 负责 <独占维度>
执行：在两个 profile.md 的「核心职责」段中增加边界说明
```

### 6.3 归档建议（C 类）

当 agent 调用频次极低（< 2 次/30 天）且与其他 agent 有重叠：
```
建议归档：{agent_id}
理由：30 天内仅调用 {count} 次，能力可由 {alternative_agent} 覆盖
执行：将 profile.md 移动到 .zcode/agents/.archived/
```

## 七、输出格式

```json
{
  "agent_dispatch_analysis": {
    "capability_matrix": [
      {"profile_id": "research-worker", "capabilities": {"research": 9, "web-search": 8}},
      {"profile_id": "Explore", "capabilities": {"research": 8, "file-ops": 7, "web-search": 6}}
    ],
    "overlap_pairs": [
      {
        "agent_a": "research-worker",
        "agent_b": "Explore",
        "overlap": 0.75,
        "weighted_overlap": 0.68,
        "shared_dimensions": ["research", "web-search", "file-ops"],
        "risk_level": "critical",
        "risk_reason": "能力重叠 75%，但 research-worker 调用 3 次 vs Explore 88 次",
        "suggestion": "明确边界或归档 research-worker"
      }
    ],
    "dispatch_distribution": {
      "Explore": {"count": 88, "share": 0.62, "avg_tokens": 342909},
      "general-purpose": {"count": 32, "share": 0.22, "avg_tokens": 437741}
    },
    "data_source": "extract_usage_signals.py + profileSnapshot"
  }
}
```

## 八、数据支撑契约

| 字段 | 状态来源 |
|---|---|
| `capabilities` | inferred（从 description + tools 推断） |
| `overlap` | inferred（算法计算） |
| `dispatch_count` | observed（从 transcript 计数） |
| `risk_level` | inferred（基于 overlap + 频次的规则） |
| `suggestion` | inferred（基于规则模板） |

## 九、维护

- 当 ZCode 新增 sub-agent 类型时，更新本文件的能力基线表
- 当 capability-dimensions.yaml 扩展时，自动反映到 overlap 计算
- 风险阈值可通过 `.data/agent-ambiguity-thresholds.json` 覆盖
