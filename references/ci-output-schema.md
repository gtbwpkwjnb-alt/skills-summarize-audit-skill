# CI Output Schema — Skills-Summarize-Audit v8.0.0

> CI 模式 JSON 输出格式定义。`$CI_MODE=true` 时使用此 schema。

## 顶层结构

```json
{
  "version": "8.0.0",
  "timestamp": "2026-06-28T23:59:00Z",
  "mode": "ci",
  "report_status": "partial",
  "evidence_coverage": {"observed": 0, "inferred": 0, "estimated": 0, "unavailable": 0},
  "summary": { ... },
  "skills": [ ... ],
  "recommendations": [ ... ],
  "alerts": [ ... ],
  "capacity_analysis": { ... },
  "exit_code": 0,
  "token_usage": { ... }
}
```

## 字段详解

### summary

```json
{
  "total_skills": 12,
  "health": "🟡",
  "avg_score": 3.2,
  "active_count": 9,
  "t3_count": 3,
  "t3_ratio": 0.25,
  "actions_required": 3,
  "fact_status": "observed",
  "evidence": ["config.yaml:health_thresholds"],
  "trend": {
    "score": "+0.3",
    "active": "+1",
    "redundant": "-2"
  }
}
```

### skills[]

```json
{
  "name": "skills-summarize-audit",
  "score": "A",
  "composite": 4.1,
  "tier": "T1",
  "dimensions": {
    "fit": "A",
    "value": "S",
    "fresh": "A",
    "community": "B",
    "roi": "A",
    "novelty": "B",
    "contamination": "A",
    "forma": "A"
  },
  "reason": "核心技能，项目画像完美匹配",
  "fact_status": "inferred",
  "evidence": ["project-profile.md", "capability-dimensions.yaml"],
  "action": "keep"
}
```

### recommendations[]

```json
{
  "skill": "skill-spector",
  "layer": "B",
  "confidence": 8,
  "roi_estimate": "+1500t/run",
  "fact_status": "estimated",
  "evidence": ["capacity formula inputs"],
  "reason": "安全扫描缺失，建议安装",
  "install_scope": "project",
  "target_path": ".agents/skills/skill-spector",
  "evidence_urls": ["https://github.com/example/skill-spector"],
  "confirmation_required": true
}
```

### alerts[]

```json
{
  "level": "warning",
  "type": "t3_ratio",
  "message": "T3占比37%超过30%阈值",
  "affected_skills": ["legacy-helper", "old-formatter"]
}
```

### capacity_analysis

```json
{
  "agent": "CodeBuddy",
  "context_limit": 16000,
  "fixed_cost": {
    "system_prompt": 2800,
    "user_input_reserve": 500,
    "history_reserve": 3000,
    "total_fixed": 6300
  },
  "available_for_skills": 9700,
  "installed_skills": [
    {
      "name": "skills-summarize-audit",
      "size_kb": 11.74,
      "estimated_tokens": 3000,
      "type": "on_demand"
    }
  ],
  "skill_stats": {
    "total_installed": 2,
    "total_potential_inject": 8800,
    "largest_skill": "summarize (5800t)",
    "average_skill_size": 4400
  },
  "mcp_tools": [
    {"server": "github", "tools": 8, "est_listing_tokens": 240}
  ],
  "mcp_stats": {
    "total_servers": 2,
    "total_tools": 11,
    "total_listing_tokens": 330
  },
  "capacity_verdict": {
    "max_skills_in_one_session": 2,
    "current_usage_pct": 91,
    "remaining_capacity": "可再装 1-2 个小 skill（<2000t），或 0 个大 skill",
    "risk_level": "🟡 临界"
  }
}
```

### exit_code

| 值 | 含义 |
|:---:|:---|
| 0 | 通过，健康度正常 |
| 1 | 🔴 健康度红色预警 |
| 2 | 需操作项超过 actions_max |
| 3 | T3 占比超过 t3_ratio_max |

### token_usage

```json
{
  "input": 8420,
  "output": 2150,
  "total": 10570
}
```
