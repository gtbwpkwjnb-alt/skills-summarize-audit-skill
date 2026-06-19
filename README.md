# Skills Audit v4.0 — 项目技能推荐引擎

> **Project Skill Audit** — 扫描项目文件夹，推荐最佳技能/插件/工具搭配，检测冗余、缺失和更新。每项建议附带三段解释：为什么做、有什么效果、用来干什么。
>
> **跨平台**: ZCode · Claude Code · Codex · Cursor · Windsurf

[![Version](https://img.shields.io/badge/version-4.0.0-blue)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-ZCode%20%7C%20Claude%20Code%20%7C%20Codex-lightgrey)]()

---

## Overview

**EN**: Scans your active project folder, analyzes its tech stack and project type, then generates a comprehensive skill/plugin/tool recommendation report. Each suggestion includes a 3-part explanation: **why** it's needed, **what effect** it has, and **how to use** it. Detects redundant skills, missing essentials, and available updates. Optionally searches the web for better alternatives.

**CN**: 扫描你的开发中项目，分析技术栈和项目类型，生成全面的技能/插件/工具推荐报告。每项建议附带三段解释：**为什么**做、**有什么效果**、**用来干什么**。检测冗余技能、缺失必备技能和可用更新，可选搜索网络寻找更优替代方案。

### Core Capabilities

| Feature | 功能 |
|---------|------|
| 📁 **Project Scan** | 项目扫描 — 识别语言、框架、构建系统、项目类型 |
| 🔍 **Skill Inventory** | 技能清单 — 列出所有已安装技能及其版本 |
| 🎯 **Smart Matching** | 智能匹配 — 基于项目类型推荐最佳技能组合 |
| ❌ **Redundancy Detection** | 冗余检测 — 标记与项目不匹配的技能 |
| ⚠️ **Gap Analysis** | 缺失分析 — 推荐但未安装的技能 |
| 🔄 **Version Check** | 版本检查 — 检测已安装技能的可用更新 |
| 🌐 **Web Alternatives** | 网络搜索 — 寻找评分更高的替代技能 |
| 📋 **Detailed Report** | 详细报告 — 每项建议含三段式解释 |

---

## Trigger / 触发

| Platform | Trigger | Example |
|----------|---------|---------|
| **ZCode** | `skills-audit` or `技能审查` or `项目审计` | `> skills-audit ./my-project` |
| **Claude Code** | `/skills-audit` | `> /skills-audit ./my-project` |
| **Codex** | `skills-audit` or `项目审计` | `> skills-audit ./my-project` |
| **Cursor** | `@skills-audit` | `> @skills-audit ./my-project` |

**Parameter**: Optional project path. Defaults to current working directory.

---

## How It Works / 工作流程

```
⓪ Load config → ① Scan project → ② List installed skills
③ Match project→skills → ④ Gap analysis (redundant/missing/outdated)
⑤ Web search for alternatives → ⑥ Generate report
⑦ User confirms → Execute actions → ⑧ Persist data
```

### Report Format / 报告格式

Each recommendation includes three sections:

| Section | Label | What it tells you |
|---------|-------|-------------------|
| 🔍 **Why** | 为什么 | Causal logic: why this suggestion applies to YOUR project |
| 💡 **Effect** | 有什么效果 | Quantifiable improvement: what changes after you act |
| 🎯 **Use Case** | 用来干什么 | Concrete scenario: when in your workflow you'll use this |

---

## Config / 配置

Edit `config.yaml` to customize scan paths, project scan settings, and version check behavior.

```yaml
scan_paths:
  - name: "用户技能 (.agents)"
    path: "~/.agents/skills/*/"
    type: user

project_scan:
  max_depth: 10
  max_files: 2000
  ignore_patterns: ["node_modules", ".git", ".venv"]

version_check:
  enabled: true
```

See [SKILL.md](SKILL.md) for full config reference.

---

## Installation / 安装

```bash
curl -sL https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-audit-skill/main/install.sh | bash
```

Windows PowerShell:
```powershell
iwr https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-audit-skill/main/install.ps1 | iex
```

### Manual

```bash
# ZCode
git clone git@github.com:gtbwpkwjnb-alt/skills-audit-skill.git ~/.agents/skills/skills-audit

# Claude Code
git clone git@github.com:gtbwpkwjnb-alt/skills-audit-skill.git ~/.claude/skills/skills-audit

# Codex
git clone git@github.com:gtbwpkwjnb-alt/skills-audit-skill.git ~/.codex/skills/skills-audit
```

---

## Changelog

### v4.0.0 (2026-06-19) — 项目技能推荐引擎

- 🎯 **New focus**: Project-based skill recommendation (was: skill quality audit)
- 📁 **Project scanning**: Auto-detect language, framework, build system, project type
- 🧠 **Smart matching**: 15+ project type patterns in `references/project-types.yaml`
- 📋 **3-part explanations**: Every recommendation has Why/Effect/Use Case
- ❌ **Redundancy detection**: Flags skills irrelevant to your project
- ⚠️ **Gap analysis**: Recommends missing but valuable skills
- 🔄 **Version check**: Compares installed vs registry versions in `references/skill-registry.yaml`
- 🌐 **Web search**: Finds better alternatives online
- 📚 **Reference files**: `references/project-types.yaml` + `references/skill-registry.yaml`
- 🔧 **Extended config**: `project_scan`, `version_check` sections

### v3.0.0 (2026-06-18) — 多平台通用化

- Multi-platform, configurable scan paths, generic 4D scoring

### v2.3.0 — ZCode 专用版 (原名 skill-manager)

- Profile, 4D scoring, optimization suggestions, auto-persistence

---

## Feedback

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-audit-skill/issues/new)

## License

MIT
