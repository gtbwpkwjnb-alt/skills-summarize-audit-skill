---
name: skills-summarize-audit
description: 技能管家 → 审计评分·活性检测·容量预警·归档回滚
---

# Skills-Summarize-Audit — 技能库与项目画像驱动审计（联动 summarize）

> Version: 6.4.0

> 对技能库或当前项目做多维画像、八维评分、容量分析与优化推荐，最终输出可执行的审计报告。
>
> **它能帮你**：
> - 了解技能库健康度（🟢/🟡/🔴）和变化趋势（📈 ↑/↓）
> - 发现僵尸技能和冗余重叠
> - 计算 Agent 还能装多少技能（多因子有效容量预警）
> - 获得可执行的归档/安装/更新操作清单
> - 误操作后可一键回滚（`--undo`）
> - 集成到 CI/CD 流水线（JSON 输出 + 门禁逻辑）

---

## 触发词 / Trigger Words

本技能采用**独立词触发**：触发词必须独立发送（可带子命令），句中不触发。与 `summarize` 技能联动设计，`技能总结` 可直接触发审计。

- **技能审计**：`技能审查`、`技能审计`、`技能检查`、`能力审查`、`能力审计`、`工具审查`、`技能总结`、`skills-audit`、`skill-audit`、`skill-check`、`capability-audit`、`tool-audit`、`skills-summarize-audit`
- **项目审计**：`项目审查`、`项目审计`、`项目诊断`、`项目画像`、`环境审查`、`环境审计`、`project-audit`、`project-check`、`project-diagnosis`、`project-profile`、`env-audit`
- **回滚操作**：`回滚`、`撤销`、`恢复`、`undo-snapshot`、`rollback`、`revert`
- **子命令**：`深度`/`deep`、`推荐`/`recommend`、`画像`/`profile`、`健康`/`health`、`轻量`/`quick`、`ci`/`--ci`、`回滚`/`undo`/`--undo`
- **描述精炼**：`精炼`、`翻译精炼`、`描述精炼`、`描述优化`、`精炼描述`/`refine`/`refine-desc`/`description-refine`/`translate-desc`

### 触发词矩阵

| 模式 | 中文触发词 | 英文触发词 |
|:----|:----|:----|
| **技能审计** | `技能审查`, `技能审计`, `技能检查`, `能力审查`, `能力审计`, `工具审查`, `技能总结` | `skills-audit`, `skill-audit`, `skill-check`, `capability-audit`, `tool-audit`, `skills-summarize-audit` |
| **项目审计** | `项目审查`, `项目审计`, `项目诊断`, `项目画像`, `环境审查`, `环境审计` | `project-audit`, `project-check`, `project-diagnosis`, `project-profile`, `env-audit` |
| **回滚操作** | `回滚`, `撤销`, `恢复` | `undo-snapshot`, `rollback`, `revert` |
| **描述精炼** | `精炼`, `翻译精炼`, `描述精炼`, `描述优化`, `精炼描述` | `refine`, `refine-desc`, `description-refine`, `translate-desc` |

同义字词：审查=审计=检查=诊断、能力=技能=工具、环境=项目 → 自动归入对应模式。

### 触发行为

| 会触发 ✅ | 不会触发 ❌ |
|:---|:---|
| `技能审查`（独立发送） | `帮我做一次技能审查`（句中） |
| `skills-audit` `skills-summarize-audit`（独立发送） | `run skills-audit on this`（句中） |
| `技能总结`（独立发送，联动 summarize 品牌） | `总结一下技能`（句中不触发） |
| `技能审计 深度`（独立词+子命令） | `这个项目需要能力审查吗`（句中） |

**为什么是独立词触发？**
独立词机制避免了日常对话中误触发（如"我们来审查一下这个方案"不会意外启动审计）。
如果习惯自然表达，可以发送 `技能审查` 先启动，再在后续对话中补充需求；或使用子命令组合如 `技能审计 深度`。

**语言自适应**：用户主语言为英文时（会话中英文>70%），触发词匹配优先英文，报告输出语言切换为 `en`。

---

## When to Use / 何时使用

- **技能审计模式**：定期维护技能库健康度（建议每2-4周一次），或技能库较大变更后。可与 `总结` 联动：run summarize → 发现技能堆积 → 建议 `技能总结`
- **项目审计模式**：接手新项目时快速了解技术栈和工具链，或项目重构前评估环境健康度
- **触发词翻译精炼**：自动将技能 description 翻译为中文触发词+简介（或反向），方便跨语言用户快速了解技能功能

## 快速上手 / Quick Start

发送独立触发词即可启动，常用组合：

| 场景 | 命令 | 说明 |
|:-----|:-----|:-----|
| 常规技能审计 | `技能审查` 或 `技能总结` | 全量扫描 + 八维评分 + 30秒摘要 |
| 快速健康检查 | `技能审查 轻量` | 跳过高耗步骤，1分钟出结果 |
| 深度分析 | `技能审计 深度` | 全量活性检测 + 逐技能深度阅读 + 社区Feed |
| 项目画像 | `项目审计` 或 `项目画像` | 扫描当前目录，识别技术栈与环境健康度 |
| 描述精炼 | `精炼` 或 `描述优化` | 批量检查并优化所有技能的 description 格式 |
| 回滚操作 | `回滚` 或 `撤销` | 撤销上一次审计执行的归档/修改操作 |
| CI 无交互模式 | `技能审查 --ci` | JSON 输出 + 三门禁逻辑，适合接入流水线 |

> 💡 **提示**：触发词必须独立发送一条消息。先发 `技能审查` 启动，再补充具体需求即可。

## 前置条件 / Prerequisites

### 硬性要求（缺失时自动检测 + 安装引导）
- **codegraph** — 代码结构与符号查询，项目画像模式的核心分析引擎。
  - 用途：项目技术栈深度扫描、依赖分析、调用链识别
  - 安装：`npm install -g @codegraph/cli` 或 `pip install codegraph`
  - 降级：命令缺失或 `codegraph --help` 非零时，项目画像模式降级为文件特征识别；报告标记 `unavailable`，不声称已完成深度代码分析
- **git** — 版本对比、快照与回滚。缺失时报告降级与安装指引，绝不自动安装。
- **config.yaml** — 本技能目录下的唯一配置源。缺失时停止审计并报告缺失配置，绝不自动生成。

### 软性要求（缺失时只读降级）
- **user-profile.md** — 用户画像。缺失时标记个性化数据 `unavailable`；仅在用户确认后才可创建。

## 能力清单 / Capabilities

skills-summarize-audit 提供以下核心能力（v6.0.0 新增能力矩阵+质量信号+社区Feed+生态雷达）：

- 项目技术栈画像与项目类型识别
- 技能库全量扫描与增量清单
- **能力维度矩阵构建（~12 能力维度，v6.0.0）**
- **质量信号读取（联动 summarize 错误账本，v6.0.0）**
- 多因子有效容量分析与容量预警
- 7 项技能活性检测（含 MCP 启动验证）
- 八维 S/A/B/C/D 评分与强制理由（含 Forma 格式分）
- T3 活性验证与误归档风险控制
- **社区 Feed 搜索（能力缺口驱动的 GitHub 搜索，v6.0.0）**
- **GitHub 同类项目横向对比**（许可证、活跃度、兼容性、安全、成本与证据链）
- **基于能力互补性的工具推荐（替代/互补/补充/无关，v6.0.0）**
- **项目级/全局级/插件级安装作用域决策**（目标路径与确认门禁）
- **生态雷达区块（条件输出，有问题才显示，v6.0.0）**
- 逐技能深度阅读与外部来源验证
- 外部信号缓存与三层推荐引擎
- 30 秒摘要报告与趋势对比
- 快照备份与 `--undo` 回滚
- CI/CD 无交互模式与 JSON 门禁输出
- 触发词翻译精炼与描述质量检查（含 Forma 格式分检测）
- **描述精炼翻译**（v6.2.0 新增 — 联动 description-refinement.md）
  - 全量发现：扫描所有 SKILL.md 的 description 字段、SKILLS_INDEX.md 用途列、配置文件残留引用
  - 路径自适应：~/.agents/skills（通用）+ 平台特有路径自动发现
  - 四维检查：格式规范·语言一致性·长度合规·信息密度
  - 自动精炼：不合格描述→箭头格式短语（≤40字符·全中文·无杂质）
  - 清理残留：配置死引用 + archived 废弃技能 + 已禁用插件
  - 不可翻译报告：内置命令/子智能体/MCP 工具→标注原因跳过

按执行阶段排列的详细能力表：

| 阶段 | 能力 | 说明 |
|:----|:----|:-----|
| ⓪ 配置 | 多平台自适应 | Codex/Claude/Cursor/Coze 平台自动检测 |
| ① 画像 | 项目技术栈扫描 | 自动识别 15+ 项目类型（Web/Rust/Python/Go/Java...） |
| ② 清单 | 技能库全量扫描 + 能力映射 | 扫描 4 个路径 + capability-dimensions.yaml 映射（v6.0.0） |
| ②-bis | 容量分析 | 多因子有效容量计算（token + 冲突因子 + 认知容量） |
| ②-ter | 活性检测 | 7 项检查验证技能是否可用（Agent可达性/MCP配置/MCP启动/命令/触发/数据/使用证据） |
| ④ 评分 | 八维评分 + 质量信号 + Forma 格式分 | 8维评分 + 读取 summarize 错误账本 + 描述格式检查（v6.2.0） |
| ④-a | T3 活性验证 | 归档前核实使用证据/修改时间/触发记录，降低误归档率 |
| ④-bis | 深度阅读 | S/A 全量深读、B(画像相关)全量、B(非相关)精简 |
| ⑤a | 外部信号 | GitHub⭐/npm📥 缓存采集 |
| **⑤-aa** | **社区 Feed** | **能力缺口驱动的 GitHub 搜索（v6.0.0）** |
| **⑤-ab** | **同类横向比较** | **候选证据、许可证、活跃度、兼容性与安全对比（v6.4.0）** |
| ⑤b | **能力矩阵推荐引擎** | **基于能力互补性的推荐（替代/互补/补充/无关，v6.0.0）** |
| ⑤c | **作用域决策** | 项目级/全局级/插件级/延后安装建议（v6.4.0） |
| ⑥ | 报告生成 + **生态雷达** | 30 秒摘要 + 容量块 + 评分表 + **条件生态雷达区块（v6.0.0）** |
| ⑦-a | 快照备份 | 执行前自动备份所有 editable 技能 |
| ⑦-d | 操作回滚 | `--undo` 撤销任意执行操作，保留 7 天快照 |
| CI | 无交互审计 | JSON 输出 + health/t3/actions 三门禁，集成 GitHub Actions |
| **⑨ 精炼** | **描述精炼翻译（v6.2.0）** | **全量发现→Forma 评分→精炼执行→残留清理→不可翻译报告** |

## When NOT to Use / 何时不使用

- 单次文件编辑、实时调试、极简项目（无技能依赖）、仅需安装单技能
- 低资源环境（审计消耗约5K-15K tokens/次）

---

## 执行流程

> 触发后，先读取 `references/execution-flow.md` 获取完整流程、评分表、容量计算、报告模板与 CI 规则。主文件仅保留入口与关键规则。

```text
⓪前置配置 → ①项目画像 + ③加载参考数据 → ②技能清单+能力映射+容量采集 → ②-bis容量分析
→ **②-ter活性检测** → ⑤a外部信号 → ④分层评分(含质量信号)
→ ⑤-aa社区Feed(获得联网同意后) → ⑤-ab GitHub同类横向比较 → ④-a T3验证 + ④-bis深度阅读 + ⑤b能力矩阵推荐 → ⑤c作用域决策
→ ⑥生成报告(含生态雷达) → ⑥-bis审计验证 → ⑥-c输出检查
→ ⑦-b用户确认 → ⑦-a快照备份 → ⑦-c执行 → ⑧持久化
```

### 关键规则

- **只读默认**：阶段⓪至⑥只读。画像、缓存、日志、快照和任何修改均在逐项确认后执行。
- **画像**：只扫描当前目录。从数据源提取痛点，禁止猜测。默认只输出报告；确认后才可写入 `{project}/.agents/project-profile.md`
- **分层**：T1（命中核心活动）→ 保留；T2（通用）→ 保留；T3（专业）→ 建议归档
- **评分**：八维 S/A/B/C/D（含 Forma 格式分）。每个技能附带 1 句理由；无理由 = 未评分
- **容量**：仅输出带公式和输入的 `estimated` 结果；上下文或加载策略未知时标记 `unavailable`。
- **外部信号**：GitHub⭐缓存7天，npm📥缓存30天。网络不可用时跳过并标注，禁止伪造
- **推荐**：每项附带信心指数(0-10)+ROI、比较证据、安装作用域与目标路径。<7 时明确标注"评估中"，<5 不推荐
- **联网比较**：默认关闭；仅在用户明确同意本次查询后执行。候选必须比较许可证、活跃度、兼容性、安全与成本，不能只按 stars 决策
- **执行**：只修改已确认的用户层技能（editable=true）。系统技能只读。
- **事实输出**：报告遵循 `references/output-contract.md`，每项结论标记 observed/inferred/estimated/unavailable；未知不得回填默认分数。
- **黄金法则**：涉及技能开发/修改/推荐时，先搜索验证，引用 ≥2 独立来源
- **活性检测**：首次审计全量检测。后续仅检测新安装技能。`深度` 子命令强制全量。异常时触发单技能活检。MCP 启动验证通过 `command --help` 或模块导入判断。

---

## 输出示例

触发 `技能审查` 后，优先输出 30 秒摘要块：

```
审计状态：partial
证据覆盖：observed <N> / inferred <N> / estimated <N> / unavailable <N>
关键结论：<状态> <结论> · 证据：<路径或命令>
操作建议：[需确认] <N> 项；本轮未修改文件
```

随后输出评分表片段（示例）：

| 技能 | 综合 | Fit | Value | Fresh | Community | ROI | Novelty | Contamination | **Forma** | 建议 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| codegraph | S | 5 | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 保留，核心工具 |
| old-linter | C | 2 | 2 | 2 | 3 | 2 | 2 | 4 | 3 | 建议归档 |

完整报告格式与事实规则见 `references/report-template.md`、`references/output-contract.md`。

---

## 项目类型识别规则

核心推断规则（完整映射见 `references/project-types.yaml`）：

- `package.json` → Web/Node/全栈
- `Cargo.toml` → Rust · `pyproject.toml` → Python · `go.mod` → Go
- `pom.xml`/`build.gradle` → Java · `.csproj` → C# · `pubspec.yaml` → Flutter
- `CMakeLists.txt` → C/C++ · `Gemfile` → Ruby
- 多 `SKILL.md` + `MEMORY.md` → `AI Agent 技能开发`

---

## 边界规则（快速参考）

- **触发**：独立词触发，句中不触发
- **分层**：T1/T2/T3 以画像"核心活动"为唯一尺度
- **评分**：五档 S/A/B/C/D。附带强制理由，无理由=未评分
- **深度分析**：读全文正文。缺口须经工具验证。
- **报告**：有内容才输出。空区无兜底。
- **推荐**：附带信心指数 0-10 + ROI。<5 不推荐，需数据支撑。
- **确认执行**：操作需用户确认。系统技能只读。
- **黄金法则**：先搜索验证，≥2 来源。

---

## 平台配置与 CI/CD

支持平台：`platforms/zcode.yaml` · `platforms/workbuddy.yaml` · `platforms/claude.yaml` · `platforms/codex.yaml` · `platforms/cursor.yaml` · `platforms/default.yaml`。

**CI 模式**（`技能审查 --ci` 或 `skills-summarize-audit --ci` 或 `skills-audit --ci`）：无交互、JSON 输出、跳过深度阅读，受 `config.yaml` 中 `ci.max_tokens` 预算限制。门禁逻辑：health=🔴 → exit_code=1 · actions_required>5 → exit_code=2 · t3_ratio>0.35 → exit_code=3。GitHub Actions 模板见 `references/ci-github-actions.yml`。

**SkillSpector 安全扫描**（可选）：`config.yaml` → `security_scan` 启用后，扫描结果融入 Value 维度（Critical→D, High→C, 通过→+0.5档）。SkillSpector 为外部进程，不消耗 Agent Token。

---

## 文件结构

```
		skills-summarize-audit/
├── SKILL.md                    # 技能主文件
├── VERSION                     # 版本号
├── LICENSE                     # MIT
├── README.md                   # 概览与安装
├── config.yaml                 # 审计配置
├── platforms/                  # 平台适配配置
├── references/                 # 参考文档
│   ├── execution-flow.md       # 执行流程索引
│   ├── flow/                   # 各阶段详细步骤（20 个子文件）
│   │   ├── 05-aa-community-feed.md  # 社区Feed（v6.0.0 新增）
│   │   └── ...
│   ├── capability-dimensions.yaml  # 能力维度定义与工具映射（v6.0.0 新增）
│   ├── project-types.yaml      # 项目类型映射
│   ├── skill-registry.yaml     # 技能注册表
│   ├── deep-analysis-template.md
│   ├── description-quality.md
│   ├── report-template.md
│   ├── ci-output-schema.md
│   ├── ci-github-actions.yml
│   └── recommendation-examples.md
├── tests/                      # 测试套件与验证脚本
├── .data/                      # 运行时数据（日志/缓存/统计/画像/外部信号）
├── install.ps1 / install.sh    # 安装脚本
└── CHANGELOG.md                # 变更日志
```

---

## 安装

一键安装与手动安装详见 `references/installation.md`（如不存在则参考 README.md）。

安装后输入 `技能审查` 或 `技能总结` 或 `skills-summarize-audit` 即可触发（`skills-audit` 仍受支持）。

---

## 反馈

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-summarize-audit-skill/issues/new)

---

## License

MIT — see [LICENSE](LICENSE) file.
