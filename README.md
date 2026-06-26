# Skills Audit v5.2.0 — 置信量化 · 五维评分 · 并行编排 · 条件报告

> **Project Skill Audit** — 扫描项目文件夹，分析技术栈和项目类型，生成全面的技能/插件/工具推荐报告。画像驱动·五维评分·置信分析。新增不推荐清单、ROI成本效益分析、并行化执行流程。
>
> **跨平台**: ZCode · Claude Code · Codex · Cursor · Windsurf

[![Version](https://img.shields.io/badge/version-5.2.0-blue)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-ZCode%20%7C%20Claude%20Code%20%7C%20Codex-lightgrey)]()

---

## Overview

**EN**: Scans your active project folder, profiles the tech stack, then scores installed skills on 5 dimensions (Fit/Value/Fresh/Community/ROI), recommends with confidence scores and cost-benefit analysis. Includes negative recommendations and conditional report output.

**CN**: 扫描开发中项目，构建项目角色画像，五维评分已安装技能，检查描述规范，搜索网络备选。每项建议附带三段解释：**原因**、**效果**、**场景**。

---

## Trigger / 触发

| Platform | Trigger | Example |
|----------|---------|---------|
| **ZCode** | `技能审查`（主）/ `技能审计` `项目审查` `项目审计` / `skills-audit` | `> 技能审查 ./my-project` |
| **Claude Code** | `/skills-audit` | `> /skills-audit ./my-project` |
| **Codex** | `技能审查` / `skills-audit` | `> skills-audit ./my-project` |
| **Cursor** | `@skills-audit` | `> @skills-audit ./my-project` |

**Parameter**: Optional project path. Defaults to current working directory.

---

## How It Works / 工作流程

```
⓪ Load config → ① Scan project → ② List installed skills
③ Load reference maps → ④ 3-tier + 3-dim scoring + desc check
⑤ Web search + external signals → ⑥ Fill Community + final report
⑦ User confirms → Execute actions → ⑧ Persist data
```

---

## Config / 配置

Edit `config.yaml` (唯一配置源) to customize scan paths, project scan settings, and version check behavior.

See [SKILL.md](SKILL.md) for full reference.

---

## Installation / 安装

```bash
curl -sL https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-audit-skill/main/install.sh | bash
```

Windows PowerShell:
```powershell
iwr https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-audit-skill/main/install.ps1 | iex
```

---

## Before vs After（技能库健康度对比）

| 指标 | 审计前 | 审计后 |
|------|--------|--------|
| 技能总数 | 23（10 个 0 次调用） | 13（全部活跃） |
| 每次启动 token 消耗 | ~8,000 tokens | ~4,500 tokens（-44%） |
| T3/不相关技能 | 8 个（34%） | 0 个（已归档） |
| 描述合格率 | 8/23 不合格（35%） | 23/23 合格（100%） |
| 功能重叠 | 3 对⚠️ | 0 对 |
| 推荐依据 | agent 猜测 | 信心指数+ROI+证据链 |

---

## Changelog

### v5.2.0 (2026-06-26) — 置信量化 · 五维评分 · 并行编排 · 条件报告

- 🔢 **五维评分**：Fit 连续计分制 + ROI 维度(10%) + Fresh 降权至15%
- 🎯 **置信推荐**：信心指数(0-10) + ROI + 证据链，≥7强烈推荐/＜5自动不推荐
- ❌ **不推荐清单**：5种数据驱动判定规则
- ⚡ **并行编排**：6阶段化并行，减少35-40% tool call轮次
- 📋 **条件报告**：无空区兜底，典型报告3-5块
- ✅ **审计验证**：数据一致性检查 + 抽样交叉验证
- 📌 **使用指导**：When to Use / When NOT to Use
- 🗂️ **文档瘦身**：报告模板+深度分析+推荐示例+描述规则 → references/
- 🧹 **去重精简**：边界规则压缩58%，并行图压缩50%，项目类型表压缩75%

### v4.x (2026-06-19~06-22) — 历史版本

- v4.3.0: Community回填、Value重构、undo机制、增量缓存
- v4.2.0: 触发词优化、output_language三态、自检锚点
- v4.0.0: 项目角色画像驱动 · 五维评分 · 15+项目类型

---

## Development Self-Test / 开发自测

每次修改后验证：

1. **项目扫描**：在 2 个不同类型的项目上运行，确认类型推断正确
2. **匹配测试**：已知项目类型→检查推荐列表是否合理
3. **分层测试**：添加不匹配技能，确认归入 T3 且标注建议归档
4. **持久化测试**：确认 `activity-log.jsonl` 可写且格式正确

## Feedback

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-audit-skill/issues/new)

## License

MIT
