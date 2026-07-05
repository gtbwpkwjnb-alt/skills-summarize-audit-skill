# Skills-Summarize-Audit v5.9.3 — 技能库审计 · summarize 联动 · 独立词触发 · 中英双语 · 容量分析 · 7维评分 · CI/CD · 回滚

> **Skills-Summarize-Audit** — 扫描项目文件夹，分析技术栈和项目类型，生成全面的技能/插件/工具推荐报告。画像驱动·七维评分·置信分析·自进化·容量分析引擎·CI/CD无交互模式。与 summarize 联动，`技能总结` 一键触发审计。
>
> **跨平台**: ZCode · Claude Code · Cursor · Codex · Windsurf · WorkBuddy

[![Version](https://img.shields.io/badge/version-5.9.3-blue)](VERSION)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-ZCode%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20WorkBuddy-lightgrey)]()

---

## Overview

**EN**: Scans your active project folder, profiles the tech stack, then scores installed skills on 7 dimensions (Fit/Value/Fresh/Community/ROI/Novelty/Contamination), recommends with confidence scores and cost-benefit analysis. **Core feature**: auto-translates skill descriptions into Chinese trigger words + summaries (and vice versa), making skills instantly discoverable for cross-language users.

**CN**: 扫描开发中项目，构建项目角色画像，七维评分已安装技能（适配度/价值/时效/社区/ROI/新颖性/污染度），检查描述规范，搜索网络备选。**核心能力**：自动将技能 description 翻译为中文触发词+简介（或反向翻译），方便中文区用户快速了解技能触发机制和主要功能。

---

## Trigger / 触发

> **独立词触发**：触发词必须独立发送（可带子命令），句中不触发。参考 `summarize` 技能机制。

| Platform | Trigger (中文) | Trigger (English) | Example |
|:----------|:---------|:---------|:---------|
| **ZCode** | `技能审查` `技能审计` `技能检查` `能力审查` `能力审计` `工具审查` `技能总结` | `skills-summarize-audit` `skills-audit` `skill-audit` `skill-check` `capability-audit` `tool-audit` | 独立发送 `技能审查` |
| **ZCode (项目模式)** | `项目审查` `项目审计` `项目诊断` `项目画像` `环境审查` `环境审计` | `project-audit` `project-check` `project-diagnosis` `project-profile` `env-audit` | 独立发送 `项目审计` |
| **Claude Code** | `/skills-summarize-audit` | `/skills-summarize-audit` | `> /skills-summarize-audit` |
| **Codex/Cursor** | 直接发送独立触发词 | 直接发送独立触发词 | `技能审查` |

**子命令**: `深度`/`deep` · `推荐`/`recommend` · `画像`/`profile` · `健康`/`health` · `轻量`/`quick` · `ci`/`--ci` · `回滚`/`undo`/`--undo`

**语言自适应**: 用户主语言为英文时，触发词匹配优先英文词条，报告输出语言自动切换为 `en`。

**Parameter**: Optional project path. Defaults to current working directory.

---

## How It Works / 工作流程

```
⓪ Load config+memory+mode(含CI检测) → (① Project profile + ③ Reference data)
→ ② Installed skills list(含容量采集) → ②-bis Capacity analysis(多因子有效容量)
→ **②-ter Liveness check**(6项,含Agent可达性) → ④ 3-tier + 7-dim scoring + health
→ (④-a T3活性验证 + ④-bis Deep read动态分级 + ⑤b Recommend)
→ ⑤a External signals(cached) → ⑥ Report(含趋势对比+capacity_analysis)
→ ⑥-bis Verify(含self-audit) → ⑥-c Output check
→ **⑦-a Snapshot backup** → **⑦-b Confirm** → **⑦-c Execute(editable only)**
→ ⑧ Persist + GC
```

> v5.9.1 新增：②-ter 6项活性检测（含Agent可达性）、④-a T3活性验证（降低误归档）、⑦-a 快照备份+⑦-d `--undo` 回滚、⑥报告趋势对比列、⑥-bis-b self-audit 自检、health_thresholds 多平台化、容量分析多因子有效容量模型。

---

## Config / 配置

Edit `config.yaml` (唯一配置源) to customize scan paths, project scan settings, and version check behavior.

See [SKILL.md](SKILL.md) for full reference.

---

## Installation / 安装

```bash
curl -sL https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-summarize-audit-skill/main/install.sh | bash
```

Windows PowerShell:
```powershell
iwr https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-summarize-audit-skill/main/install.ps1 | iex
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

### v5.9.1 (2026-07-05) — 快照回滚 · 活性增强 · 多平台阈值 · 趋势对比

- 🔄 **快照回滚机制**：⑦-a 执行前自动备份，⑦-d `--undo` 一键恢复，保留7天快照
- 🧪 **6项活性检测**：新增 Agent 可达性检查（#0），验证 scan_paths 可访问
- 📊 **多因子有效容量模型增强**：min(token预算, 技能上下文容量×冲突因子, 认知容量)
- 📈 **趋势对比**：30秒摘要新增趋势行，评分表新增趋势列（↑/↓/→）
- 🎯 **T3 活性验证**：④-a 归档前核实使用证据/修改时间/触发记录，降低误归档率
- 📚 **深度阅读动态化**：B档+画像相关技能升级为全量深读
- 🏢 **多平台阈值**：health_thresholds 按 platform 区分（CodeBuddy 20 / Claude 40 / Cursor 50）
- 🔍 **self-audit 自检**：⑥-bis-b 快速自检6项，输出 `🔍 审计者自检` 块
- 🇨🇳 **中文社区信号**（默认关闭）：支持知乎/掘金/CSDN 缓存采集
- 🗑️ **移除 custom_rules 死代码**：轻量规则引擎从未启用，清理 ~25 行
- 📝 **能力清单**：SKILL.md 新增14行能力阶段表格，优化 SkillFather 工作流匹配分
- 🐛 **修复**：config.yaml 依赖更新、版本号同步 v5.9.1
- 🗂️ **运行时数据治理**：新增 `.data/` 目录，统一存放 stats.json / project-profiles.json / activity-log.jsonl
- 🧹 **无用文件清理**：删除 `nul`、`.skill-order.json`
- 🤖 **自动化验证**：新增 `tests/validate.py` 与 4 个 Markdown 测试用例

### v5.8.0 (2026-06-28) — 容量分析引擎·CI/CD·7维评分·安全扫描

- 📦 **容量分析引擎**：计算灵活承载上限，输出"还能装几个"
- 🤖 **CI/CD 无交互模式**：`--ci` 触发，JSON 输出，门禁逻辑，GitHub Actions 模板
- 📊 **7维评分**：新增 Novelty（新颖性 10%）+ Contamination（跨语言污染 5%）
- 🛡️ **安全扫描**：SkillSpector 集成，结果融入 Value 维度
- 🔗 **Skills Manager 对接**：actions.json 输出格式
- 🏪 **WorkBuddy 上架准备**：frontmatter 补全 category + platforms 字段
- ⚙️ **config.yaml 扩展**：ci 块 + security_scan 块

### v5.7.0 (2026-06-28) — 自进化·并行修正·ROI精化·分级策略

- 🔧 **并行依赖修复**：②→⑤a 从并行改为串行（⑤a 依赖②输出的技能名列表）
- 🌐 **Community 离线策略**：网络不可用且无缓存时标注「⏸ 信号待获取」，跳过 Community 维度（4维重算权重），禁止伪造默认值
- 📊 **Value 维度重建**：从"项目价值"改为"预期价值（基于画像推断）"，5档基于命中核心活动数+场景频率
- 📈 **ROI 5档精化**：从3档→5档连续制（S:>+3000t, A:+1000~3000, B:0~1000, C:-500~0, D:<-500）
- 🔄 **版本自动回写**：④-bis 深度阅读时自动从 SKILL.md 提取 version，回写 skill-registry.yaml
- 🎯 **④-bis 分级策略**：S/A全量深读、B轻量检查、C/D跳过，token消耗降低 40-60%
- 🏗️ **复合项目类型识别**：检测多个独立类型时生成复合类型+合并推荐列表
- 🔗 **推荐去重合并**：A/B/C三层推荐后按技能名去重，优先保留A层（内置映射更可靠）
- 👤 **user-profile 深度映射**：8条显式映射规则（高频技能→Value+1档、工作模式→推荐权重等）
- 📋 **30秒摘要块**：报告最前面增加摘要块（健康度/关键操作/预估收益）
- 📊 **趋势对比行**：最近3次审计数据趋势行（均分/活跃/冗余变化）
- 🧹 **缓存GC**：步骤⑧持久化时清理不在当前技能列表中的缓存条目
- 🤖 **评分自进化基础**：⑥-bis 增加评分-决策一致性追踪，累积 ≥5 次偏差后触发权重微调建议
- 💬 **审计反馈收集**：⑦执行后增加1-4分反馈问卷，写入 .data/stats.json 用于长期优化
- 📦 **project-types.yaml 扩展**：新增 DevOps-多服务、CI/CD、游戏-Unity/Unreal、区块链-Hardhat/Solana、AI/深度学习/LLM部署 共8种项目类型
- 🏪 **多平台配置**：新增 platforms/claude.yaml、codex.yaml、cursor.yaml

### v5.6.0 (2026-06-28) — 独立词触发 · 中英双语 · 触发词翻译精炼

- 🎯 **独立词触发**：参考 `summarize` 技能机制，触发词必须独立发送（可带子命令），句中不触发，避免误触发
- 🌐 **中英双语触发词**：中文 6 词 + 英文 5 词（技能审计模式），中文 6 词 + 英文 5 词（项目审计模式），同义字词自动映射
- 🔄 **同义字词扩展**：审查=审计=检查=诊断、能力=技能=工具、环境=项目，自动归入对应模式
- 📝 **触发词翻译精炼**：升级为核心能力——自动翻译+精炼技能触发词和简介，中英双向互译
- 🌍 **语言自适应**：根据用户会话主语言（中/英/混合）自动切换翻译方向和报告语言
- 📖 **同义字词映射表**：10 个英文关键词→中文主词+2-4 个同义扩展，提升中文用户可发现性
- 🏗️ **子命令支持**：`深度`/`推荐`/`画像`/`健康` 四个子命令，按需执行特定步骤

### v5.5.0 (2026-06-27) — 五档评分 · 强制理由 · 前置目录检查

- 📊 **S/A/B/C/D 五档评分**：从连续 0-100 分改为五档定性制，减少 agent 间评分不一致
- 📝 **强制评分理由**：每个技能必须附带 1 句理由，无理由 = 未评分
- 🔍 **前置目录检查**：步骤⓪新增项目根检测，防止非项目目录运行

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

0. **自动化验证**：先运行 `python tests/validate.py`，确认 YAML/版本/权重/平台合规全部通过
1. **项目扫描**：在 2 个不同类型的项目上运行，确认类型推断正确
2. **匹配测试**：已知项目类型→检查推荐列表是否合理
3. **分层测试**：添加不匹配技能，确认归入 T3 且标注建议归档
4. **活性测试**：修改 scan_paths 中一个路径为无效值，确认 Agent 可达性检测触发 ❌
5. **快照测试**：执行 `--undo --list`，确认回滚机制正常工作
6. **趋势测试**：连续运行 2 次审计，确认第 2 次出现趋势列（↑/↓/→）
7. **持久化测试**：确认 `.data/activity-log.jsonl` 可写且格式正确

## Feedback

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-summarize-audit-skill/issues/new)

## License

MIT

