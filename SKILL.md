---
name: skills-summarize-audit
version: "5.9.3"
description: >
  审计技能库健康度：项目画像→七维评分→容量预警→趋势对比→快照回滚。
  支持技能/项目双模式 + CI/CD。与 summarize 联动，定期检查技能库健康度。
  Capabilities: skill audit, project profiling,
  7-dim scoring, capacity analysis, liveness check, snapshot rollback, CI mode.
requires:
  tools:
    - codegraph
    - git
  configs:
    - config.yaml
---

# Skills-Summarize-Audit — 技能库与项目画像驱动审计（联动 summarize）

> 对技能库或当前项目做多维画像、七维评分、容量分析与优化推荐，最终输出可执行的审计报告。
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

### 触发词矩阵

| 模式 | 中文触发词 | 英文触发词 |
|:----|:----|:----|
| **技能审计** | `技能审查`, `技能审计`, `技能检查`, `能力审查`, `能力审计`, `工具审查`, `技能总结` | `skills-audit`, `skill-audit`, `skill-check`, `capability-audit`, `tool-audit`, `skills-summarize-audit` |
| **项目审计** | `项目审查`, `项目审计`, `项目诊断`, `项目画像`, `环境审查`, `环境审计` | `project-audit`, `project-check`, `project-diagnosis`, `project-profile`, `env-audit` |
| **回滚操作** | `回滚`, `撤销`, `恢复` | `undo-snapshot`, `rollback`, `revert` |

同义字词：审查=审计=检查=诊断、能力=技能=工具、环境=项目 → 自动归入对应模式。

### 触发行为

| 会触发 ✅ | 不会触发 ❌ |
|:---|:---|
| `技能审查`（独立发送） | `帮我做一次技能审查`（句中） |
| `skills-audit`（独立发送） | `run skills-audit on this`（句中） |
| `技能总结`（独立发送，联动 summarize 品牌） | `总结一下技能`（句中不触发） |
| `技能审计 深度`（独立词+子命令） | `这个项目需要能力审查吗`（句中） |

**语言自适应**：用户主语言为英文时（会话中英文>70%），触发词匹配优先英文，报告输出语言切换为 `en`。

---

## When to Use / 何时使用

- **技能审计模式**：定期维护技能库健康度（建议每2-4周一次），或技能库较大变更后。可与 `总结` 联动：run summarize → 发现技能堆积 → 建议 `技能总结`
- **项目审计模式**：接手新项目时快速了解技术栈和工具链，或项目重构前评估环境健康度
- **触发词翻译精炼**：自动将技能 description 翻译为中文触发词+简介（或反向），方便跨语言用户快速了解技能功能

## 前置条件 / Prerequisites

### 硬性要求（缺失时自动检测 + 安装引导）
- **codegraph** — 代码结构与符号查询，技能核心分析引擎。缺失时尝试自动安装。
- **git** — 版本对比、快照与回滚。缺失时尝试自动安装。
- **config.yaml** — 本技能目录下的唯一配置源。缺失时从模板生成。

### 软性要求（缺失时自动创建）
- **user-profile.md** — 用户画像。缺失时自动通过问答引导创建。

## 能力清单 / Capabilities

skills-audit 提供以下核心能力：

- 项目技术栈画像与项目类型识别
- 技能库全量扫描与增量清单
- 多因子有效容量分析与容量预警
- 6 项技能活性检测
- 七维 S/A/B/C/D 评分与强制理由
- T3 活性验证与误归档风险控制
- 逐技能深度阅读与外部来源验证
- 外部信号缓存与三层推荐引擎
- 30 秒摘要报告与趋势对比
- 快照备份与 `--undo` 回滚
- CI/CD 无交互模式与 JSON 门禁输出
- 触发词翻译精炼与描述质量检查

按执行阶段排列的详细能力表：

| 阶段 | 能力 | 说明 |
|:----|:----|:-----|
| ⓪ 配置 | 多平台自适应 | Codex/Claude/Cursor/Coze 平台自动检测 |
| ① 画像 | 项目技术栈扫描 | 自动识别 15+ 项目类型（Web/Rust/Python/Go/Java...） |
| ② 清单 | 技能库全量扫描 | 扫描 4 个路径下的所有已安装技能 |
| ②-bis | 容量分析 | 多因子有效容量计算（token + 冲突因子 + 认知容量） |
| ②-ter | 活性检测 | 6 项检查验证技能是否可用（Agent可达性/MCP/命令/触发/数据/使用证据） |
| ④ 评分 | 七维评分 | Fit·Value·Fresh·Community·ROI·Novelty·Contamination，每项附强制理由 |
| ④-a | T3 活性验证 | 归档前核实使用证据/修改时间/触发记录，降低误归档率 |
| ④-bis | 深度阅读 | S/A 全量深读、B(画像相关)全量、B(非相关)精简 |
| ⑤a | 外部信号 | GitHub⭐/npm📥 缓存采集 |
| ⑤b | 推荐引擎 | 三层推荐：内置映射 + 差距分析 + 网络搜索 |
| ⑥ | 报告生成 | 30 秒摘要 + 容量块 + 评分表 + 趋势列 |
| ⑦-a | 快照备份 | 执行前自动备份所有 editable 技能 |
| ⑦-d | 操作回滚 | `--undo` 撤销任意执行操作，保留 7 天快照 |
| CI | 无交互审计 | JSON 输出 + health/t3/actions 三门禁，集成 GitHub Actions |

## When NOT to Use / 何时不使用

- 单次文件编辑、实时调试、极简项目（无技能依赖）、仅需安装单技能
- 低资源环境（审计消耗约5K-15K tokens/次）

---

## 执行流程

> 触发后，先读取 `references/execution-flow.md` 获取完整流程、评分表、容量计算、报告模板与 CI 规则。主文件仅保留入口与关键规则。

```text
⓪前置配置 → ①项目画像 → ②技能清单+容量采集 → **②-ter活性检测**
→ ③加载参考数据 → ④分层评分
→ ④-bis深度阅读 → ⑤外部信号+推荐 → ⑥生成报告 → ⑥-bis审计验证 → ⑦执行 → ⑧持久化
```

### 关键规则

- **画像**：只扫描当前目录。从数据源提取痛点，禁止猜测。结果写入 `{project}/.agents/project-profile.md`
- **分层**：T1（命中核心活动）→ 保留；T2（通用）→ 保留；T3（专业）→ 建议归档
- **评分**：七维 S/A/B/C/D。每个技能附带 1 句理由；无理由 = 未评分
- **容量**：计算 Agent 可承载上限。可再装 ≤1 → 🔴，2-4 → 🟡，≥5 → 🟢
- **外部信号**：GitHub⭐缓存7天，npm📥缓存30天。网络不可用时跳过并标注，禁止伪造
- **推荐**：每项附带信心指数(0-10)+ROI。<7 时明确标注"评估中"，<5 需有数据支撑才推荐
- **执行**：只修改用户层技能（editable=true）。系统技能只读。
- **黄金法则**：涉及技能开发/修改/推荐时，先搜索验证，引用 ≥2 独立来源
- **活性检测**：首次审计全量检测。后续仅检测新安装技能。`深度` 子命令强制全量。异常时触发单技能活检

---

## 输出示例

触发 `技能审查` 后，优先输出 30 秒摘要块：

```
🟢 技能库健康度：良好
🛠️ 关键操作：更新 1 个落后技能、归档 2 个 T3 技能
💰 预计节省：~3200 tokens/次（减少低价值 skill 注入）
```

随后输出评分表片段（示例）：

| 技能 | 综合 | Fit | Value | Fresh | Community | ROI | Novelty | Contamination | 建议 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| codegraph | S | 5 | 5 | 4 | 4 | 5 | 5 | 5 | 保留，核心工具 |
| old-linter | C | 2 | 2 | 2 | 3 | 2 | 2 | 4 | 建议归档 |

完整报告格式见 `references/report-template.md`。

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

**CI 模式**（`技能审查 --ci` 或 `skills-audit --ci`）：无交互、JSON 输出、跳过深度阅读，受 `config.yaml` 中 `ci.max_tokens` 预算限制。门禁逻辑：health=🔴 → exit_code=1 · actions_required>5 → exit_code=2 · t3_ratio>0.35 → exit_code=3。GitHub Actions 模板见 `references/ci-github-actions.yml`。

**SkillSpector 安全扫描**（可选）：`config.yaml` → `security_scan` 启用后，扫描结果融入 Value 维度（Critical→D, High→C, 通过→+0.5档）。SkillSpector 为外部进程，不消耗 Agent Token。

---

## 文件结构

```
skills-audit/
├── SKILL.md                    # 技能主文件
├── VERSION                     # 版本号
├── LICENSE                     # MIT
├── README.md                   # 概览与安装
├── config.yaml                 # 审计配置
├── platforms/                  # 平台适配配置
├── references/                 # 参考文档
│   ├── execution-flow.md       # 执行流程索引
│   ├── flow/                   # 各阶段详细步骤（19 个子文件）
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

安装后输入 `技能审查` 或 `skills-audit` 即可触发。

---

## 反馈

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-audit-skill/issues/new)

---

## License

MIT — see [LICENSE](LICENSE) file.
