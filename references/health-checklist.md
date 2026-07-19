# 健康度主动监测 Checklist v1.0

> 大脑加强：把 v7.1.0 的"被动响应"升级为"主动体检"。
> 业界参考：npm outdated / npm audit / Dependabot / Homebrew brew cleanup --prune。
> 本技能不动手；提供 checklist + 阈值 + 指导"如何让 agent 处理"。

## 一、触发词

| 触发词 | 含义 | 输出 |
|---|---|---|
| `技能体检` | 全量主动健康扫描 | 完整健康报告 + 处置建议清单 |
| `skill checkup` | 同上（英文） | 同上 |
| `僵尸技能` | 找出长期未使用的 | 归档候选清单 |
| `过期检查` | 找出版本过期 | 升级候选清单 |
| `技能体检 快速` | 跳过外部信号 | 仅本地信号 |
| `技能体检 深度` | 全维度 + 历史 | 完整 + 趋势 |

## 二、八大健康维度（参考 OpenSSF Scorecard 18 检查 + Skills Directory 安全规则）

| # | 维度 | 检测方法 | 健康阈值 | 不健康处置 |
|:-:|---|---|---|---|
| 1 | **存在性** | SKILL.md 存在且可解析 | 必有 | 标记 invalid |
| 2 | **元数据完整** | name + description 都有且符合 Forma | TQI ≥ 6 | 触发翻译精炼 |
| 3 | **依赖可达** | 引用的 MCP/命令/路径全部可达 | PASS 率 ≥ 80% | 标记 broken |
| 4 | **使用证据** | 最近 90 天在会话中有调用记录 | ≥1 次 | 标记 zombie |
| 5 | **版本新鲜** | VERSION / CHANGELOG 最新更新 ≤180 天 | <180 天 | 标记 stale |
| 6 | **触发词唯一** | 与其他技能冲突分 < 0.7 | <0.7 | 触发冲突流程 |
| 7 | **安全合规** | 通过 security-rules.yaml 全部规则 | 0 critical | 标记 risky |
| 8 | **跨平台一致** | 同名技能在多平台版本/description 一致 | 一致 | 标记 drift |

## 三、检测脚本规则（伪代码，让 agent 执行）

### 检测 1：存在性

```python
def check_existence(skill_path):
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {"status": "fail", "reason": "missing SKILL.md"}
    
    try:
        frontmatter = parse_frontmatter(skill_md.read_text())
    except Exception as e:
        return {"status": "fail", "reason": f"parse error: {e}"}
    
    if not frontmatter.get("name") or not frontmatter.get("description"):
        return {"status": "warn", "reason": "missing name or description"}
    
    return {"status": "pass"}
```

### 检测 2：元数据完整（联动 translation-quality.md）

```python
def check_metadata_quality(skill):
    tqi = calculate_tqi(skill.description)  # 见 translation-quality.md
    if tqi >= 8:
        return {"status": "pass", "tqi": tqi}
    elif tqi >= 6:
        return {"status": "warn", "tqi": tqi, "suggestion": "触发翻译精炼"}
    else:
        return {"status": "fail", "tqi": tqi, "suggestion": "重写 description"}
```

### 检测 3：依赖可达（联动 v7.1.0 的 liveness_check）

```python
def check_dependency_reachable(skill):
    # 见 config.yaml liveness_check 配置
    # 调用 collect_codex_display_candidates.py 等价的扫描逻辑
    results = {
        "mcp_servers": check_mcp(skill),        # MCP 启动验证
        "commands": check_commands(skill),      # command -v
        "scripts": check_scripts(skill),        # scripts/ 下的脚本可执行
        "references": check_references(skill),  # references/ 文件存在
    }
    
    pass_rate = sum(1 for r in results.values() if r["status"] == "pass") / len(results)
    return {
        "status": "pass" if pass_rate >= 0.8 else "warn",
        "pass_rate": pass_rate,
        "details": results,
    }
```

### 检测 4：使用证据（联动 summarize error-ledger）

```python
def check_usage_evidence(skill_name, days=90):
    # 从 summarize 错误账本提取使用记录
    ledger_path = "~/.agents/skills/summarize/harvests/error-ledger.md"
    if not ledger_path.exists():
        return {"status": "unavailable", "reason": "summarize 未安装"}
    
    recent_uses = count_skill_mentions_in_days(ledger_path, skill_name, days)
    
    if recent_uses >= 5:
        return {"status": "pass", "uses": recent_uses}
    elif recent_uses >= 1:
        return {"status": "warn", "uses": recent_uses, "note": "低频使用"}
    else:
        return {"status": "zombie", "uses": 0, "suggestion": "考虑归档"}
```

### 检测 5：版本新鲜

```python
def check_version_freshness(skill_path):
    # 读 VERSION 文件或 CHANGELOG.md 最新日期
    version_file = skill_path / "VERSION"
    changelog = skill_path / "CHANGELOG.md"
    
    if changelog.exists():
        latest_date = parse_latest_changelog_date(changelog)
        days_since = (date.today() - latest_date).days
    elif version_file.exists():
        # 无 changelog，用文件 mtime
        days_since = (date.today() - date.fromtimestamp(version_file.stat().st_mtime)).days
    else:
        return {"status": "unavailable"}
    
    if days_since < 90:
        return {"status": "pass", "days": days_since}
    elif days_since < 180:
        return {"status": "warn", "days": days_since}
    else:
        return {"status": "stale", "days": days_since, "suggestion": "考虑升级或归档"}
```

### 检测 6：触发词唯一（联动 conflict-detection.md）

```python
def check_trigger_uniqueness(skill, all_skills):
    conflicts = []
    for other in all_skills:
        if other.name == skill.name:
            continue
        score = conflict_score(skill, other)  # 见 conflict-detection.md
        if score >= 0.7:
            conflicts.append((other.name, score))
    
    if not conflicts:
        return {"status": "pass"}
    elif max(s for _, s in conflicts) >= 0.85:
        return {"status": "fail", "conflicts": conflicts}
    else:
        return {"status": "warn", "conflicts": conflicts}
```

### 检测 7：安全合规（联动 security-rules.yaml）

```python
def check_security_compliance(skill_path):
    rules = load_yaml("references/security-rules.yaml")
    violations = []
    
    for rule in rules:
        result = apply_rule(rule, skill_path)
        if result["status"] == "fail":
            violations.append({"rule_id": rule["id"], "severity": rule["severity"]})
    
    critical = [v for v in violations if v["severity"] == "CRITICAL"]
    high = [v for v in violations if v["severity"] == "HIGH"]
    
    if critical:
        return {"status": "risky", "violations": violations}
    elif high:
        return {"status": "warn", "violations": violations}
    else:
        return {"status": "pass"}
```

### 检测 8：跨平台一致

```python
def check_cross_platform_consistency(skill_name):
    # 扫描所有平台路径（config.yaml scan_paths）
    occurrences = find_skill_across_platforms(skill_name)
    
    if len(occurrences) <= 1:
        return {"status": "pass", "note": "单平台，无漂移"}
    
    versions = set(o.version for o in occurrences)
    descriptions = set(o.description for o in occurrences)
    
    drift = []
    if len(versions) > 1:
        drift.append({"field": "version", "values": list(versions)})
    if len(descriptions) > 1:
        drift.append({"field": "description", "values": list(descriptions)})
    
    return {
        "status": "pass" if not drift else "drift",
        "occurrences": occurrences,
        "drift": drift,
    }
```

## 四、综合健康分计算

```python
WEIGHTS = {
    "existence": 0.15,         # 必须项
    "metadata": 0.10,
    "dependency": 0.20,        # 重要
    "usage": 0.15,
    "version": 0.10,
    "trigger": 0.10,
    "security": 0.15,          # 重要
    "consistency": 0.05,
}

STATUS_SCORES = {
    "pass": 10,
    "warn": 6,
    "fail": 2,
    "unavailable": None,  # 不计入
    "zombie": 1,
    "stale": 3,
    "risky": 0,
    "drift": 4,
    "invalid": 0,
}

def calculate_health(skill_results):
    total_weight = 0
    weighted_sum = 0
    for dim, result in skill_results.items():
        score = STATUS_SCORES.get(result["status"])
        if score is None:
            continue  # unavailable 不计入
        weighted_sum += score * WEIGHTS[dim]
        total_weight += WEIGHTS[dim]
    
    return round(weighted_sum / total_weight, 1) if total_weight else 0
```

### 健康分等级

| 分数 | 等级 | 处置 |
|:-:|:-:|---|
| ≥8.0 | 🟢 优秀 | 保留 |
| 6.0–7.9 | 🟡 良好 | 观察具体扣分项 |
| 4.0–5.9 | 🟠 待改进 | 触发修复建议 |
| <4.0 | 🔴 危险 | 强烈建议归档/重写 |

## 五、输出报告模板

```text
🏥 技能体检报告 (2026-07-19)

📊 整体健康度
  扫描: 15 个技能
  🟢 优秀 (≥8): 8 个 (53%)
  🟡 良好 (6-7.9): 4 个 (27%)
  🟠 待改进 (4-5.9): 2 个 (13%)
  🔴 危险 (<4): 1 个 (7%)

🚨 优先处理（按风险降序）

| 技能 | 健康分 | 主要问题 | 建议动作 |
|---|:-:|---|---|
| old-skill | 2.5 | 🚫 安全 CRITICAL + 🚫 僵尸 90 天 | 立即归档 |
| scrapling | 4.8 | ⚠️ 触发词冲突 + ⚠️ 版本过期 200 天 | 升级 + 重命名 |
| learn | 5.5 | ⚠️ 元数据 TQI=5 + ⚠️ 低频使用 | 翻译精炼 |

✅ 健康技能（前 5）
| 技能 | 健康分 | 状态 |
|---|:-:|---|
| summarize | 9.2 | 全维度 pass |
| agent-reach | 8.8 | 仅 trigger warn |
| skills-summarize-audit | 8.5 | 自检通过 |

🛠 处置建议（指导 agent）

1. 立即归档 old-skill:
   [详细指令模板见 lifecycle-guidance.md 模板 A]

2. 升级 scrapling:
   [详细指令模板见 lifecycle-guidance.md 模板 B]

3. 翻译精炼 learn:
   [触发 references/translation-quality.md 自学习]

📈 趋势（与上次体检对比）
  整体健康度: 7.2 → 7.5 (↑0.3)
  僵尸技能数: 3 → 1 (↓2)
  下次建议体检时间: 2026-08-19（30 天后）
```

## 六、增量 vs 全量

```yaml
modes:
  
  full:
    trigger: ["技能体检", "技能体检 深度"]
    scope: all_visible_skills
    cost: high
  
  quick:
    trigger: ["技能体检 快速"]
    skip_checks: [usage, version, security]  # 只跑 existence/metadata/dependency/trigger
    cost: low
  
  incremental:
    trigger: 新增/修改技能后自动
    scope: 仅受影响技能
    cost: minimal
  
  targeted:
    trigger: ["体检 <skill-name>"]
    scope: 单个技能
    cost: minimal
```

## 七、用户 Agent 指导模板

### 模板：让 agent 修复某个不健康技能

```
[用户对 agent 说]

我接受了体检报告，请帮我修复 "learn" 技能的元数据 TQI 问题：

1. 读取 ~/.agents/skills/learn/SKILL.md
2. 当前 description: {old}
3. 按 TQI 规则重新翻译为: {new_candidate}
4. 计算 TQI 分数应 ≥ 8
5. 修改后用 collect_codex_display_candidates.py --scope visible --visible-id learn --require-chinese 验证
6. 报告：修改前/后 diff、TQI 评分变化、客户端刷新确认
```

### 模板：批量归档僵尸技能

```
[用户对 agent 说]

请归档以下僵尸技能（90 天未使用 + 安全 warn）：

1. old-skill (~/.agents/skills/old-skill/)
2. deprecated-tool (~/.agents/skills/deprecated-tool/)

步骤：
1. 在 ~/.agents/skills/archived/ 创建归档目录
2. mv 每个技能到 archived/，保留 mtime
3. 在 archived/README.md 追加"归档原因: 僵尸 + 安全 warn"
4. 检查 ~/.zcode/cli/config.json 是否引用，引用则移除
5. 输出归档清单 + 可恢复指令
```

## 八、定时检查（参考 Dependabot）

```yaml
# 建议：用户在 AGENTS.md 中追加定时任务
scheduled_checkup:
  
  schedule: "monthly"  # weekly/biweekly/monthly
  
  trigger_on:
    - 显式触发词（技能体检）
    - 项目启动时（如果距离上次 >30 天）
    - 用户长会话中提到技能但不确定时
  
  notify_channels:
    - 会话内报告
    - 追加到 ~/.agents/skills/.audit-snapshots/checkup-history.jsonl
  
  escalation:
    - critical 安全问题: 立即通知
    - 僵尸率 >30%: 下次会话开头提醒
    - 整体健康分 <6: 主动建议全量审计
```

## 九、与现有 v7.1.0 的关系

| v7.1.0 已有 | 本文件加强 |
|---|---|
| liveness_check（7 项检测） | 扩展到 8 维，加上元数据/触发词/跨平台 |
| quality_signals（读 error-ledger） | 用作"使用证据"维度 |
| security_scan（10 条 SEC 规则） | 作为"安全合规"维度输入 |
| project_profiles.auto_refresh_days | 借鉴思路做"健康度过期提醒" |

**不重复**：本文件只是把上述 v7.1.0 的零散检查整合成统一 checklist，外加"使用证据"和"跨平台一致"两个新维度。

## 十、维护

- 检测规则更新：本文件第三节
- 权重调整：第四节 WEIGHTS
- 等级阈值：第四节"健康分等级"
- 业界对照：OpenSSF Scorecard / npm audit / Skills Directory
