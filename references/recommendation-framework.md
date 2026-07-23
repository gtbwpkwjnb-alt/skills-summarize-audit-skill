# 推荐引擎决策框架 v2.0

> 大脑加强：把 v7.1.0 的"四档建议"升级为"证据链 + 互补分析 + 组合套餐 + 可达性反推"。
> 业界参考：npm 的 dep graph、Safeguard 的 reachability、Hacker News 的推荐协同过滤。
> 本文件是推荐引擎的大脑；抓取市场/评分计算由 agent 按 mcp-marketplaces.md / skill-marketplaces.md 模板执行。

## 一、推荐输出五档（取代 v7.1.0 的四档）

| 档位 | 触发条件 | 输出内容 |
|:-:|---|---|
| **保留** | 健康分 ≥ 8 + 使用证据 ≥ 1 | 直接保留 + 简短理由 |
| **升级** | 已安装但版本过期/有更新 | 升级到 X.Y.Z + 指令 |
| **替换** | 已装但社区有更优替代 | A→B 迁移方案 |
| **引入** | 能力缺口且社区有候选 | 安装 X + 作用域 + 风险 |
| **共存**（新） | 与现有工具互补不重叠 | 并存方案 + 分工边界 |
| **归档** | 健康分 <4 或僵尸 | 归档原因 + 恢复路径 |

> 五档输出取代原"保留/观察/考虑引入/不建议"，更具体可执行。

## 二、推荐决策五步法

### Step 1：定位"用户真实需求"

> 不只看项目画像，更看用户最近会话上下文

```python
def infer_real_need():
    needs = []
    
    # 来源 A：项目画像（tech-fingerprints 识别的技术栈）
    needs += infer_from_project_profile()
    
    # 来源 B：结构化 Codex session/tool-call 事件（排除 prompt 文本提及）
    needs += infer_from_structured_session_events(days=14, provenance_required=True)
    
    # 来源 C：用户画像（user-profile.md 兴趣领域）
    needs += infer_from_user_profile()
    
    # 来源 D：当前对话上下文（用户正在做的任务）
    needs += infer_from_current_conversation()
    
    # 加权去重
    return weighted_deduplicate(needs)
```

**输出示例**：
```yaml
real_needs:
  - need: "深度抓取 JS 渲染页面"
    weight: 0.9
    sources: ["最近会话提到'爬取小红书'", "项目用 agent-reach 但 web-search 仅 5/10"]
  
  - need: "PDF 报告生成"
    weight: 0.7
    sources: ["项目画像显示有报告需求", "user-profile 兴趣含'写作'"]
```

### Step 2：能力缺口分析（联动 capability-dimensions）

```python
def analyze_capability_gaps(needs, current_capabilities):
    gaps = []
    for need in needs:
        required_caps = map_need_to_capabilities(need)
        for cap in required_caps:
            current_level = current_capabilities.get(cap, 0)
            required_level = need.weight * 10  # 期望分
            
            if current_level < required_level - 2:  # 缺口 ≥ 2 档
                gaps.append({
                    "capability": cap,
                    "current": current_level,
                    "required": required_level,
                    "gap": required_level - current_level,
                    "need": need,
                })
    return sorted(gaps, key=lambda g: -g["gap"])
```

### Step 3：候选发现（让 agent 抓市场）

> Audit 输出"该抓什么、怎么抓"，agent 按指令执行

```text
[对 agent 说]

我检测到能力缺口：
- web-scrape: 当前 0/10，需要 8/10
- deep-crawl: 当前 0/10，需要 7/10

请按 references/mcp-marketplaces.md 评估以下候选：
1. firecrawl (https://glama.ai/mcp/servers/firecrawl)
2. scrapling (https://github.com/D4Vinci/Scrapling)
3. browserbase (https://glama.ai/mcp/servers/browserbase)

对每个候选计算六维健康分，输出对比表。
```

### Step 4：互补性分析（取代简单"替代/补充"）

```python
def analyze_relationship(existing_tool, candidate_tool):
    existing_caps = existing_tool.capabilities
    candidate_caps = candidate_tool.capabilities
    
    overlap = set(existing_caps) & set(candidate_caps)
    only_existing = set(existing_caps) - set(candidate_caps)
    only_candidate = set(candidate_caps) - set(existing_caps)
    
    # 重叠度
    overlap_ratio = len(overlap) / len(set(existing_caps) | set(candidate_caps))
    
    # 领先度（候选在重叠项上的平均优势）
    if overlap:
        avg_lead = sum(
            candidate_caps[c].level - existing_caps[c].level
            for c in overlap
        ) / len(overlap)
    else:
        avg_lead = 0
    
    # 判定
    if overlap_ratio >= 0.7 and avg_lead >= 2:
        return "supersede"  # 🔴 替代：候选全面领先
    elif overlap_ratio <= 0.3 and only_candidate:
        return "complement"  # 🟢 共存：能力互补
    elif 0.3 < overlap_ratio < 0.7 and avg_lead >= 1:
        return "supplement"  # 🟡 补充：候选补强薄弱项
    else:
        return "irrelevant"  # ⚪ 无关
```

### Step 5：组合套餐推荐（业界首创）

> 单工具推荐局限大；推荐"组合套餐"更能解决用户问题

```python
def recommend_combo(needs, all_candidates):
    """从候选中找最优组合覆盖所有需求"""
    
    # 这是经典的集合覆盖问题（Set Cover）
    # 用贪心算法：每次选能覆盖最多未满足需求的候选
    
    uncovered = set(needs)
    selected = []
    
    while uncovered:
        best = max(all_candidates, key=lambda c: len(c.covers() & uncovered))
        newly_covered = best.covers() & uncovered
        if not newly_covered:
            break
        selected.append(best)
        uncovered -= newly_covered
    
    return selected
```

**输出示例**：
```text
🎁 组合套餐推荐：「完整调研流水线」

需求覆盖：
  ✅ 多平台社交搜索 → agent-reach (已装)
  ✅ 深度 JS 渲染抓取 → firecrawl (新引入，scope=global)
  ✅ 浏览器交互验证 → playwright (已装 MCP)
  ✅ 调研报告生成 → summarize + pdf (已装)

整体 ROI: +3200/run（节省跨工具切换时间）
协同增益: 1.4×（大于单工具之和）

📋 引入清单
  - firecrawl-mcp: scope=global, 复杂度=low
  - 配置: mcp.json 追加 firecrawl 服务器块
  
🤝 协同约束
  - agent-reach 触发词限定为"社交/多平台"
  - firecrawl 触发词限定为"深度抓取/JS 渲染"
  - 避免触发冲突（见 conflict-detection.md）
```

## 三、可达性反推（参考 Safeguard reachability）

> 不推荐"理论上需要"的，优先推荐"用户实际会用到"的

```python
def reachability_weighted_recommendation(user_history, candidates):
    """
    从用户最近 N 次会话历史中提取真实使用路径，
    给"用户已实际调用过类似能力"的候选加权。
    """
    used_paths = extract_user_paths(user_history)
    # 例：用户最近 14 天调用过：agent-reach (5 次) + summarize (3 次)
    # 暗示用户在做"调研 + 总结"工作流
    
    for candidate in candidates:
        # 候选与用户路径的关联度
        path_match = compute_path_similarity(candidate.capabilities, used_paths)
        candidate.reachability_bonus = path_match * 0.3  # 加权 30%
    
    return sorted(candidates, key=lambda c: -(c.health_score + c.reachability_bonus))
```

**对比示例**：
```text
传统推荐（基于项目画像）：
  "你的项目是 React，建议引入 jest"
  → 但用户实际从不写测试，引入也是僵尸

可达性反推：
  "你最近 14 天在调试 React 性能问题（5 次提到'优化渲染'），
   建议引入 react-performance-profiler MCP"
  → 与用户真实工作流高匹配
```

## 四、推荐去重与排序

### 去重规则

```python
def deduplicate_recommendations(recs):
    """相同需求只保留最优"""
    by_need = {}
    for rec in recs:
        need_key = frozenset(rec.needs)
        if need_key not in by_need or rec.score > by_need[need_key].score:
            by_need[need_key] = rec
    return list(by_need.values())
```

### 排序规则

```python
def sort_recommendations(recs):
    """按 (P0 → P1 → P2 → 互补) 排序"""
    priority_order = {
        "security_critical": 0,  # 安全紧急
        "p1_gap": 1,             # P1 能力缺口
        "p0_gap": 2,             # P0 能力缺口
        "supersede": 3,          # 替换过期工具
        "combo": 4,              # 组合套餐
        "complement": 5,         # 互补补充
        "irrelevant": 99,
    }
    return sorted(recs, key=lambda r: priority_order.get(r.kind, 99))
```

## 五、推荐报告输出模板

```text
💡 推荐报告

🚨 P0 优先（必须处理）
  ⚠️ 安全风险: old-skill 含 SEC-009 CRITICAL（递归删除）
     建议: 立即归档 + 检查安装来源
     指令: 见 lifecycle-guidance.md 模板 A

🔄 P1 升级（建议本周完成）
  📦 scrapling: 当前 1.0.0 → 最新 1.2.3
     变更: 修复 typosquatting 检测
     建议: scope=project（仅当前仓库用）
     指令: 见 lifecycle-guidance.md 模板 B

🎁 P2 组合套餐（高 ROI 引入）
  「完整调研流水线」: agent-reach + firecrawl + playwright
     预期 ROI: +3200/run
     引入复杂度: low（仅 firecrawl 新增）
     指令: 见 lifecycle-guidance.md 模板 C

🔄 P2 替代（社区有更优）
  current: humanizer (2.0.0, 6 个月未更新)
  candidate: humanize-ai (3.1.0, 上周更新, ⭐1.2k)
  能力提升: de-AI 9/10 → 9.5/10, 多语种支持
  迁移成本: 中（API 略有差异）
  指令: 见 lifecycle-guidance.md 模板 D

✅ 保留（健康优秀，无需动作）
  - summarize (9.2)
  - agent-reach (8.8)
  - learn (8.5)

🤝 共存建议（不动作，仅提示分工）
  - agent-reach (社交) + firecrawl (深度) + scrapling (反反爬)
    明确触发词边界，避免冲突

📊 整体评估
  本次推荐共 8 项，按用户最近 14 天使用路径反推
  预计 ROI 提升: +4500/run
  引入复杂度: low-medium
  下次复审: 30 天后（或技能变动时）
```

## 六、信心指数计算（取代主观赋值）

```python
def calculate_confidence(recommendation):
    """综合信心 0-10"""
    factors = {
        "evidence_completeness": 0.25,  # 证据完整度（来源数）
        "market_data_freshness": 0.20,  # 市场数据新鲜度
        "user_history_match": 0.20,     # 与用户历史匹配度
        "capability_gap_severity": 0.15, # 缺口严重度
        "community_consensus": 0.10,    # 社区共识（多市场排名）
        "license_clarity": 0.10,        # 许可证明确度
    }
    
    score = 0
    for factor, weight in factors.items():
        score += recommendation.scores[factor] * weight
    
    return round(score, 1)
```

### 信心阈值

| 信心 | 行动 | 标签 |
|:-:|---|:-:|
| ≥8.0 | 直接给出安装指令 | `strongly_recommended` |
| 6.0–7.9 | 建议评估 + 给出试用方案 | `recommended` |
| 4.0–5.9 | 仅提示存在，由用户决定 | `consider` |
| <4.0 | 不主动推荐 | `not_recommended` |

## 七、推荐引擎与 v7.1.0 的兼容

### 保留 v7.1.0 已有

- capability-dimensions.yaml 的能力维度分类
- 05-rec-engine.md 的互补性分析（已升级为本文件第二节）
- recommendation-examples.md 的输出示例

### 升级内容

| v7.1.0 | v2.0（本文件） |
|---|---|
| 四档（保留/观察/考虑引入/不建议） | 五档 + 替换 + 共存 |
| 主观能力评分 | 联动 mcp-marketplaces.md 健康分 |
| 单工具推荐 | 组合套餐推荐 |
| 静态项目画像驱动 | 用户最近会话可达性反推 |
| 信心 0-10 含糊 | 六因子加权信心 |

## 八、用户 Agent 抓取指引

### 模板：完整推荐流程（让 agent 执行）

```
[用户对 agent 说]

请按 references/recommendation-framework.md 为我做一次完整推荐：

1. 从结构化 Codex session/tool-call 事件提取最近 14 天可归因的实际使用路径；忽略系统提示、skill catalog 和原始 prompt 中的名称提及
2. 用 references/tech-fingerprints.yaml 扫描项目
3. 列出能力缺口（参考 capability-dimensions.yaml）
4. 对每个缺口，按 references/mcp-marketplaces.md 评估候选
   （按需调用 WebFetch 抓取 Glama/Smithery 数据）
5. 输出按 P0/P1/P2 排序的推荐清单
6. 给出"组合套餐"建议（如有协同）
7. 每项推荐附"安装/升级指令模板"（按 references/lifecycle-guidance.md）
```

## 九、安全边界

- 推荐永远不直接安装，由用户确认后让 agent 执行
- 推荐的候选必须有：许可证 + 安全评级 + 来源 URL
- 推荐信心 <6 时必须显式标注 `consider`，不得给安装指令
- 涉及凭证/网络的工具，在指令模板中显式列出风险点

## 十、维护

- 五档定义：本文件第一节
- 互补分析算法：第二节 Step 4
- 组合套餐算法：第二节 Step 5
- 信心因子：第六节
- 业界对照：npm/Safeguard/Hacker News 在 _docs/recommendation-research.md（如有）
