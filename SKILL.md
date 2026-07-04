---
name: skills-audit
version: "5.9.0"
description: 当用户提到技能审查、技能审计、能力审查、工具审查、项目审计、项目诊断、环境审计或技能库健康检查时，对技能库或当前项目进行画像驱动的七维审计，并给出可执行的优化/归档/安装建议。优先使用独立触发词 `技能审查`/`skills-audit` 或 `项目审计`/`project-audit`。
---

# Skills Audit — 技能库与项目画像驱动审计

> 对技能库或当前项目做多维画像、七维评分、容量分析与优化推荐，最终输出可执行的审计报告。

---

## 触发方式

**独立词触发**：触发词必须独立发送（可带子命令），句中不触发。参考 `summarize` 技能。

### 触发词矩阵

| 模式 | 中文触发词 | 英文触发词 |
|:---|:---|:---|
| **技能审计** | `技能审查` `技能审计` `技能检查` `能力审查` `能力审计` `工具审查` | `skills-audit` `skill-audit` `skill-check` `capability-audit` `tool-audit` |
| **项目审计** | `项目审查` `项目审计` `项目诊断` `项目画像` `环境审查` `环境审计` | `project-audit` `project-check` `project-diagnosis` `project-profile` `env-audit` |

同义字词：审查=审计=检查=诊断、能力=技能=工具、环境=项目 → 自动归入对应模式。

### 触发行为

| 会触发 ✅ | 不会触发 ❌ |
|:---|:---|
| `技能审查`（独立发送） | `帮我做一次技能审查`（句中） |
| `skills-audit`（独立发送） | `run skills-audit on this`（句中） |
| `技能审计 深度`（独立词+子命令） | `这个项目需要能力审查吗`（句中） |

**语言自适应**：用户主语言为英文时（会话中英文>70%），触发词匹配优先英文，报告输出语言切换为 `en`。

**子命令**: `深度`/`deep` · `推荐`/`recommend` · `画像`/`profile` · `健康`/`health` · `轻量`/`quick` · `ci`/`--ci`

---

## When to Use / 何时使用

- **技能审计模式**：定期维护技能库健康度（建议每2-4周一次），或技能库较大变更后
- **项目审计模式**：接手新项目时快速了解技术栈和工具链，或项目重构前评估环境健康度
- **触发词翻译精炼**：自动将技能 description 翻译为中文触发词+简介（或反向），方便跨语言用户快速了解技能功能

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

- **画像**：只扫描当前目录，痛点必须来自数据，禁止猜测；结果写入 `{project}/.agents/project-profile.md`
- **分层**：T1核心（命中核心活动）→ 保留；T2通用 → 保留；T3专业 → 建议归档
- **评分**：七维 S/A/B/C/D，每个技能必须附带1句理由；无理由 = 未评分
- **容量**：计算 Agent 可承载技能上限；可再装数量 ≤1 时 🔴，2-4 🟡，≥5 🟢
- **外部信号**：GitHub⭐缓存7天、npm📥缓存30天；网络不可用时跳过并标注，禁止伪造
- **推荐**：每项推荐附带信心指数(0-10)+ROI；<7 需明确标注评估，<5 需有数据支撑才推荐
- **执行**：仅用户层技能（editable=true）可修改；系统技能只读
- **黄金法则**：涉及技能开发/修改/推荐时，先搜索验证，引用 ≥2 独立来源
- **活性检测**：首次审计全量，后续增量（仅新安装技能）；`深度` 子命令强制全量；异常触发单技能活检

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
- **评分**：五档 S/A/B/C/D + 强制理由，无理由=未评分
- **深度分析**：必读全文正文，缺口须经工具验证
- **报告**：条件输出，空区无兜底
- **推荐**：每项附带信心指数 0-10 + ROI，<5 自动不推荐需数据支撑
- **确认执行**：操作需用户确认；系统技能只读
- **黄金法则**：先搜索验证，≥2 来源

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
│   ├── workflow-details.md     # 历史文件（重定向至 execution-flow.md）
│   ├── execution-flow.md       # 详细执行流程与评分表
│   ├── project-types.yaml      # 项目类型映射
│   ├── skill-registry.yaml     # 技能注册表
│   ├── deep-analysis-template.md
│   ├── description-quality.md
│   ├── report-template.md
│   ├── ci-output-schema.md
│   └── ci-github-actions.yml
├── install.ps1 / install.sh    # 安装脚本
└── CHANGELOG.md                # 变更日志
```

---

## 安装

一键安装与手动安装详见 `references/installation.md`（如不存在则参考 README.md）。

安装后输入 `技能审查` 或 `skills-audit` 即可触发。

---

## 反馈

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-audit/issues/new)

---

## License

MIT — see [LICENSE](LICENSE) file.
