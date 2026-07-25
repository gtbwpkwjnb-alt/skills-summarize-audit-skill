# 生态优化与最佳配置 v1.0

> v9.0.0 新增。服务能力四「生态综合评估」的 4.4 子能力。
> 综合 Skill + MCP + Agent 三层，给出保留/隐藏/卸载分层建议。

## 一、设计哲学

**二八原则**：80% 的价值来自 20% 的工具。生态优化的目标是识别这 20% 并保留，其余按使用频率和画像匹配度分层处置。

**数据驱动**：所有建议必须基于可归因数据（usage signals）或市场证据，不主观赋值。

## 二、综合评分公式

每个已安装工具（skill/mcp/agent）的综合价值分：

```
value_score = (
    usage_frequency * 0.40 +    # 实际调用频次（最重要的客观证据）
    profile_alignment * 0.25 +  # 用户画像匹配度
    health_score * 0.20 +       # 健康状态（来源/元数据/版本）
    market_signal * 0.15        # 市场热度（社区维护活跃度）
)
```

各分项取值 0-10。

### 2.1 usage_frequency 归一化

```python
def normalize_usage(raw_count: int, max_count: int) -> float:
    """归一化到 0-10。"""
    if max_count == 0:
        return 0.0
    return min(10, (raw_count / max_count) * 10)
```

### 2.2 market_signal（联网补全）

当本地无使用证据时，Audit 输出 URL 模板与评分框架，由用户的 Agent 执行抓取（非 Audit 自动联网）：

```python
def fetch_market_signal(tool_name: str, tool_type: str) -> dict:
    """
    输出 URL 模板与评分框架，供用户的 Agent 执行联网查询。
    返回 {score, evidence_url, status}。
    """
    # Audit 仅构造查询模板，不实际调用 firecrawl/rival-search
    # 用户的 Agent 根据模板执行搜索
    return {
        "score": "<由用户 Agent 填充 0-10>",
        "evidence_url": "<由用户 Agent 填充来源 URL>",
        "status": "market_observed"
    }
```

## 三、三层建议分层

基于 `value_score` 分层：

| 层级 | 条件 | 建议 | 数据要求 |
|---|---|---|---|
| **保留** | value ≥ 7.0 | 当前配置合理，保持 | 高置信度（有本地使用证据） |
| **观察** | 4.0 ≤ value < 7.0 | 暂时保留，30 天后复查 | 中置信度（有市场证据） |
| **隐藏** | 2.0 ≤ value < 4.0 | 从命令栏隐藏但保留文件 | 低置信度（仅画像匹配） |
| **卸载** | value < 2.0 | 评估卸载 | 必须有明确证据（无使用 + 无匹配 + 无市场） |

### 3.1 隐藏 vs 卸载的边界

- **隐藏**：用户技能（`agents/skills/`），可通过配置 `enable: false` 隐藏
- **卸载**：插件 MCP（`plugins/cache/`），删除配置 + cache

**禁止**：在无使用证据且无市场证据时建议卸载，必须标 `[需确认]`。

## 四、组合套餐推荐

当多个工具组合使用更高效时，推荐「组合套餐」：

```python
def detect_synergy(signals: dict) -> list[dict]:
    """
    检测经常一起被调用的工具组合。
    基于 transcript 中的连续 tool_call 模式。
    """
    # 例如：firecrawl_search + Read 经常连续出现 = 调研套餐
    # 例如：codegraph_explore + Edit = 代码修改套餐
    return [
        {
            "combo": ["firecrawl_search", "Read", "Edit"],
            "co_occurrence": 12,
            "label": "调研-修改套餐",
            "advice": "保留，高协同"
        }
    ]
```

## 五、联网补全策略

### 5.1 何时触发联网

| 场景 | 触发条件 | 联网目的 |
|---|---|---|
| MCP 从未被本地调用 | `status == "configured_never_observed"` | 查市场热度判断是否值得保留 |
| Skill 无使用证据 | transcript 中无 Skill 调用记录 | 查 GitHub stars / 社区讨论 |
| Agent 调用频次极低 | 30 天内 < 2 次 | 查是否有替代方案 |

### 5.2 联网查询模板（用户 Agent 执行）

> **权限边界**：Audit 不自动调用 firecrawl/rival-search。以下伪代码标记了**用户 Agent 应执行的步骤**，Audit 仅输出 URL 模板与评分框架。

```python
# 以下为 用户 Agent 应执行的步骤，Audit 不自动联网
async def supplement_with_market_data(target: dict) -> dict:
    """用户 Agent 在得到授权后执行的联网补全。"""
    if target["local_evidence"] == "unavailable":
        # 1. 用户 Agent 通过 firecrawl 搜索 GitHub repo
        #    URL 模板由 Audit 提供
        result = await firecrawl_search(
            query=f"{target['name']} {target['type']} stars github",
            limit=3
        )
        # 2. 提取热度信号
        stars = extract_stars(result)
        last_commit = extract_last_commit(result)
        # 3. 计算市场分
        market_score = compute_market_score(stars, last_commit)
        target["market_evidence"] = {
            "score": market_score,
            "stars": stars,
            "last_commit": last_commit,
            "source_url": result[0]["url"] if result else None,
            "status": "market_observed"
        }
    return target
```

### 5.3 Confidence 等级

| 等级 | 条件 |
|---|---|
| **high** | 有本地使用证据 AND 健康分 ≥ 8 |
| **medium** | 有本地证据 OR 有市场证据 |
| **low** | 仅有画像匹配 OR 仅有估算 |

## 六、输出格式

```json
{
  "ecosystem_optimization": {
    "summary": {
      "total_tools": 30,
      "keep": 18,
      "watch": 7,
      "hide": 4,
      "uninstall_candidates": 1
    },
    "recommendations": [
      {
        "target": "agent-reach",
        "type": "skill",
        "value_score": 9.2,
        "layer": "keep",
        "breakdown": {
          "usage": 8.5,
          "alignment": 8.0,
          "health": 10.0,
          "market": 9.0
        },
        "confidence": "high",
        "evidence": "5 次本地调用 + GitHub stars >1000"
      },
      {
        "target": "playwright",
        "type": "mcp",
        "value_score": 2.1,
        "layer": "hide",
        "breakdown": {
          "usage": 0.0,
          "alignment": 5.0,
          "health": 7.5,
          "market": 9.5
        },
        "confidence": "medium",
        "evidence": "本地从未调用；市场高热度（Chrome 自动化主流工具）",
        "suggestion": "隐藏但保留，需要浏览器任务时手动启用"
      }
    ],
    "synergy_combos": [...],
    "data_gaps": [
      "MCP 调用频次来自 transcript 的 mcp__* 计数，可能遗漏通过其他路径的调用"
    ]
  }
}
```

## 七、与 v8 recommendation-framework 的关系

| 维度 | v8 recommendation-framework | v9 ecosystem-optimization |
|---|---|---|
| 范围 | 单工具推荐（保留/升级/替换/引入/共存/归档） | 全生态分层（保留/观察/隐藏/卸载） |
| 数据 | 缺口分析 + 候选市场评估 | 使用频次 + 画像 + 健康 + 市场 |
| 触发 | 用户明确请求推荐 | 生态评估时自动生成 |
| 输出 | 引入什么新工具 | 现有工具怎么分层 |

二者互补：v8 关注「该引入什么」，v9 关注「现有怎么优化」。

## 八、维护

- value_score 权重可通过 `.data/value-weights.json` 覆盖
- 联网查询的 firecrawl/rival-search 配置见主 SKILL.md 的工具链章节
- synergy 检测算法可基于更多 transcript 数据校准
