# Actions JSON Schema — Skills Audit v5.9.1

> 对接 Skills Manager（xingkongliang 桌面应用）的桥梁格式。
> 步骤⑦执行时输出，Skills Manager 读取并执行操作。

## Schema

```json
{
  "source": "skills-audit v5.9.1",
  "timestamp": "2026-06-28T23:59:00Z",
  "project": "ZCodeProject",
  "actions": [
    {
      "skill": "legacy-helper",
      "action": "archive",
      "reason": "T3技能，与画像零匹配",
      "confidence": 9,
      "priority": "high"
    },
    {
      "skill": "skill-spector",
      "action": "install",
      "source": "npm",
      "package": "@nvidia/skillspector",
      "reason": "安全扫描缺失，26.1%技能含漏洞",
      "confidence": 8,
      "priority": "high"
    },
    {
      "skill": "caveman",
      "action": "install",
      "source": "github",
      "repo": "gtbwpkwjnb-alt/caveman-skill",
      "reason": "输出压缩节省65-75% token",
      "confidence": 7,
      "priority": "medium"
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `source` | string | 生成来源标识 |
| `timestamp` | ISO8601 | 审计时间 |
| `project` | string | 项目名称 |
| `actions[].skill` | string | 技能名称 |
| `actions[].action` | enum | `archive` / `install` / `update` / `fix_description` |
| `actions[].reason` | string | 操作原因 |
| `actions[].confidence` | int 0-10 | 信心指数 |
| `actions[].priority` | enum | `high` / `medium` / `low` |
| `actions[].source` | string | (install时) 安装来源: `npm` / `github` / `pip` / `url` |
| `actions[].package` | string | (install时) 包名 |
| `actions[].repo` | string | (install时) GitHub 仓库 |
