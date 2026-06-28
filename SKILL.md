---
name: skills-audit
version: "5.8.0"
description: 技能审查·项目审计 → 画像驱动·七维评分·逐技能优化 \| Skill Audit·Project Audit → profile·7dim·deep opt
category: "开发工具"
platforms: ["WorkBuddy", "ZCode", "Claude Code", "Cursor", "Codex CLI", "Windsurf"]
user-invocable: true
---

# Skills Audit v5.8.0 — 独立词触发 · 中英双语 · 容量分析引擎 · 7维评分

> **九大核心能力**: ①项目记忆驱动精准画像 ②五档评分+强制理由+健康管理 ③逐技能深度阅读+维护清单 ④先搜索后开发方法论 ⑤双模式（技能审计/项目审计）⑥条件输出报告 ⑦触发词中英翻译精炼 ⑧**容量分析引擎（计算灵活承载上限）** ⑨**CI/CD 无交互模式**
>
> **核心原则**: ⚠️ 黄金法则 — 先搜索验证再决策。涉及技能开发/修改/推荐时，必须先 agent-reach / web_fetch 检索，引用 ≥2 个独立来源。
>
> **记忆驱动**: 4层金字塔 L0 `~/.agents/AGENTS.md` > L1 `AGENTS.md` > L2 `memories/MEMORY.md` > L3 项目画像 `{project}/.agents/project-profile.md`。全局人物画像 `user-profile.md`。

---

## 触发方式

> **独立词触发**：触发词必须独立发送（可带子命令），句中不触发。参考 `summarize` 技能。

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

**子命令**: `深度`/`deep` · `推荐`/`recommend` · `画像`/`profile` · `健康`/`health`

---

## When to Use / 何时使用

- **技能审计模式**：定期维护技能库健康度（建议每2-4周一次），或技能库较大变更后
- **项目审计模式**：接手新项目时快速了解技术栈和工具链，或项目重构前评估环境健康度
- **触发词翻译精炼**（核心能力）：自动将技能 description 翻译为中文触发词+简介（或反向），方便跨语言用户快速了解技能功能

## When NOT to Use / 何时不使用

- 单次文件编辑、实时调试、极简项目（无技能依赖）、仅需安装单技能、低资源环境（审计消耗约5K-15K tokens/次）

---

## 执行流程

> 详细步骤（含完整表格、示例、输出格式）见 `references/workflow-details.md`。以下为流程概要+关键规则。

```text
⓪加载配置+项目记忆+模式检测(含CI模式) → ①项目画像 → ②已安装技能清单(含容量采集)
→ ②-bis容量分析引擎 → ③加载参考数据 → ④三级分层+七维评分
→ ④-bis逐技能深度阅读 → ⑤a外部信号获取 → ⑤b三层推荐引擎
→ ⑥生成报告(含容量报告块) → ⑥-bis审计验证 → ⑥-c报告输出检查
→ ⑦执行(用户确认后) → ⑧持久化
```

并行化阶段：`⓪ → (①+③) → ② → ②-bis → ⑤a → ④ → (④-bis+⑤b) → ⑥ → ⑥-bis → ⑦ → ⑧`

> **v5.8.0 变更**：步骤②新增容量采集（SKILL.md 大小/MCP工具数/描述长度）；新增步骤②-bis 容量分析引擎（计算灵活承载上限）；④评分从5维升级为7维（新增 Novelty + Contamination）；⑥报告新增 capacity_analysis 块。
>
> **串行化修正（v5.7.0）**：②→⑤a 必须串行（⑤a 依赖②输出的技能名列表）；④→④-bis 必须串行（④-bis 依赖④评分做分级）；④-bis 与 ⑤b 可并行（两者互不依赖）。
> 若⑤a因网络延迟未完成，Community 维度标注「⏸ 信号待获取」并跳过该维度评分（4维重算权重），禁止使用伪造默认值。

### ⓪ 前置：配置+记忆+模式

1. **前置目录检查**：确认当前目录存在、是项目根、深度合理
2. **加载 config.yaml**：scan_paths、project_scan、health_thresholds 等
3. **加载项目记忆**：`memories/MEMORY.md` 存在则读取，不存在则询问用户
4. **模式检测**：
   - 检查触发词是否含 `--ci` 或子命令 `ci` → 设置 `$CI_MODE=true`
   - CI 模式：无交互、JSON 输出、跳过 ④-bis、max_tokens 预算限制
   - 设置 `$AUDIT_MODE` = `"skill"`（全量）或 `"project"`（跳过深读+描述优化）
5. 读取 `user-profile.md` 用于个性化判定
6. **CI 模式 Token 预算**（`$CI_MODE=true` 时）：`max_tokens` 取自 `config.yaml` 中 `ci.max_tokens`（默认 8000），超限时自动降级步骤（优先跳过 ④-bis → ⑤a → ⑤b）

### ① 项目画像

只扫描当前工作目录。提取：目录信息→关键文件→文件特征→构建多维画像（类型/用途/活动/技术栈/兴趣/痛点/入口）。**痛点必须来自数据源，禁止猜测**。画像强制持久化到 `{project}/.agents/project-profile.md`，设置 `$PROFILE_READY=true`。

### ② 已安装技能清单（v5.8.0 扩展容量采集）

扫描 `config.yaml` 中所有 `scan_paths`，提取每个技能的 name/description/路径/来源/版本号。同时扫描 MCP 服务器（`mcp_config.files`），提取服务器+工具列表。去重：同name优先 editable=true→版本高者。

**v5.8.0 新增容量采集**（同时执行，不额外增加轮次）：

| 采集项 | 采集方式 | 用途 |
|:---|:---|:---|
| SKILL.md 文件大小 | Read → 字节数 / 4 ≈ token 估算 | 计算注入成本 |
| MCP 工具数量 | 解析 mcp_config 配置 | 计算工具池 token 成本 |
| MCP 工具描述长度 | 读取每个工具的 description | 计算 tool listing 成本 |
| Agent 类型 | 从平台特征判定 | 选择计算模型 |

### ②-bis 容量分析引擎（v5.8.0 新增）

> 核心诊断能力：分析当前 agent 环境下每个已安装技能/工具的 token 成本，计算灵活承载上限。

**计算公式**：
```
灵活承载上限 = (上下文可用空间 - 固定消耗) / 单 skill 平均注入成本

上下文可用空间 = Agent 实际可用 Token（非原生窗口）
固定消耗 = SystemPrompt + 对话历史留存 + 用户输入预留
单 skill 平均注入成本 = 取决于 skill 加载机制
```

**各 Agent 计算模型差异**：

| Agent | 上限约束 | skill 成本计算 | 固定消耗估算 |
|:---|:---|:---|:---|
| **CodeBuddy** | 16K 硬限制 | 按 use_skill 调用叠加 | SystemPrompt 2800 + 历史 3000 + 用户输入 500 = 6300t |
| **Claude Code** | skillListingBudget=1%×200K=2000t | 全部 skill 描述计入 listing budget | SystemPrompt 3000 + 历史 8000 + 用户输入 1000 = 12000t |
| **Cursor** | 动态，无固定上限 | 按需加载，仅计当前 | SystemPrompt 2500 + 历史 3000 + 用户输入 500 = 6000t |

**容量分级判定**：
```
剩余空间 / 单 skill 平均成本 = 可再装数量

可再装 ≥ 5  → 🟢 充裕，放心扩展
可再装 2-4  → 🟡 注意，选择性扩展
可再装 1    → 🟠 临界，仅可装轻量 skill
可再装 0    → 🔴 已满，必须精简现有 skill 才能扩展
```

**容量报告输出**（写入步骤⑥报告的 capacity_analysis 块，JSON 格式见 `references/report-template.md`）。

### ③ 加载参考数据

读取 `references/project-types.yaml` 和 `references/skill-registry.yaml`。找不到则降级为内置规则+web搜索。

### ④ 三级分层+七维评分

**分层**：T1核心（命中核心活动）→保留 · T2通用 →保留 · T3专业 →建议归档

**七维评分（S/A/B/C/D + 强制理由）**：

| 维度 | 权重 | 评分标准概要 |
|:---|:---:|:---|
| Fit 项目匹配 | 30% | 命中≥2核心活动=S · 命中1=A · T2通用=B · T3=C · 零交集=D |
| Value 预期价值 | 20% | 命中≥2核心活动+高频场景=S · 命中1核心活动=A · T2通用可用=B · T3领域低频=C · 与画像零关联=D |
| Fresh 版本时效 | 17% | 版本≥registry=S · 落后≤1小版本=A · 无版本号=B · 落后大版本=C · 废弃=D |
| Community 外部信号 | 18% | ⭐≥100/近1月更新=S · ⭐≥10/近6月=A · 本地=B · 信号弱=C · 废弃=D |
| ROI 成本效益 | 10% | >+3000t/run=S · +1000~3000=A · 0~1000=B · -500~0=C · <-500=D |
| **Novelty 新颖性** | **10%** | 独特无替代=S · 有差异化=A · 标准实现/1-2竞品=B · ≥3竞品高度重叠=C · 完全冗余=D |
| **Contamination 污染** | **5%** | 纯目标语言=S · ≤10%混合=A · 10-30%混合=B · >30%混合/触发词不一致=C · 严重混合/触发失效=D |

综合 = Fit×0.30 + Value×0.20 + Fresh×0.17 + Community×0.18 + ROI×0.10 + Novelty×0.10 + Contamination×0.05（S=5,A=4,B=3,C=2,D=1）
≥4.0→S · ≥3.0→A · ≥2.0→B · ≥1.5→C · <1.5→D

**每个技能必须附带1句理由**，无理由=未评分。

**Novelty 检测方法**：WebSearch `"{skill_name} alternative AI agent skill"` → 对比已安装技能 + skill-registry.yaml 功能描述 → 与竞品数据库交叉比对。仅 S/A 档执行（④-bis 分级策略），CI 模式跳过。
**Contamination 检测方法**：正则检测中英文字符比例 → 触发词矩阵一致性校验（SKILL.md ↔ platforms/*.yaml）→ 描述质量检查时同步执行。

**冗余检测**：技能-技能重叠>60%→⚠️ · 技能-MCP跨层重叠→⚠️ · 互补关系→✅
**容量预警**：总数>30→🚨 · T3占比>30%→🚨 · 与画像零匹配→🟡

**安全子项**（融入 Value 维度，v5.8.0）：
- 技能通过 SkillSpector 扫描 → Value +0.5 档
- 技能含 Critical 漏洞 → Value 自动降为 D
- 技能含 High 漏洞 → Value 自动降为 C

### ④-bis 逐技能深度阅读

**分级策略（v5.7.0新增，节约token）**：

| 技能档位 | 深度阅读策略 | 外部验证 |
|:---:|:---|:---|
| **S/A** | 读全量 SKILL.md → 六维分析 → 完整维护清单 | ≥2来源 |
| **B** | 读 frontmatter+首段 → 精简维护清单 | 仅1次验证 |
| **C/D** | 跳过深度阅读（仅输出归档建议） | 跳过 |

读全量 SKILL.md → 六维分析（作用·适配·缺口·建议·维护·参考）→ 维护清单 → 外部验证 ≥2来源 → 自指校验。**自动提取各技能实际版本号，回写 `skill-registry.yaml`**（版本变更时更新）。模板见 `references/deep-analysis-template.md`。

> 子命令 `轻量`/`quick` 可跳过全部 ④-bis 步骤。项目审计模式自动跳过。

### ⑤a 外部信号获取

缓存优先：GitHub⭐缓存7天 · npm📥缓存30天。最多2次重试（每次10s超时）。获取后回填 Community 分。**必须输出强制摘要**。网络不可用且无缓存时标注「⏸ 信号待获取」，跳过 Community 维度（4维重算权重），禁止使用伪造默认值。

### ⑤b 三层推荐引擎

A层：内置映射匹配（project-types.yaml）→ B层：Gap分析（未覆盖活动）→ C层：网络搜索补充 → **去重合并**（v5.7.0新增）

去重规则：同名技能优先保留A层推荐（内置映射更可靠）。C层仅补充A层未命中的技能。信心指数取A层原始值，C层补充技能保留C层信心。

每项推荐附带信心指数(0-10)+ROI预估。信心≥7→强烈推荐 · 5-6.9→建议评估 · <5→自动不推荐。不推荐需可追溯的数据支撑。

### ⑥ 生成报告

**评分快照即时持久化（v5.7.0新增）**：报告输出前，立即持久化评分快照到 `stats.json`（均分/活跃数/T3占比/技能评分表）。若用户中断于⑦之前，下次审计仍可增量对比。

**30秒摘要块**（v5.7.0新增，始终最先输出）：3行核心信息——①技能库健康度（🟢/🟡/🔴）②关键操作（必须做的N项）③预计token节省。

**容量报告块**（v5.8.0新增，步骤②-bis 结果）：始终输出。含 agent 类型、上下文限制、固定消耗明细、已安装技能 token 成本表、MCP 工具池成本、容量判定（🟢/🟡/🟠/🔴 + 可再装数量）。CI 模式下以 JSON 格式输出 `capacity_analysis` 块。

**CI 模式输出**（v5.8.0新增，`$CI_MODE=true`）：全部输出为 JSON 格式，符合 `references/ci-output-schema.md` 定义。含 `summary`/`skills`/`recommendations`/`alerts`/`capacity_analysis`/`exit_code`/`token_usage`。门禁逻辑：health=🔴 → exit_code=1 · actions_required>5 → exit_code=2 · t3_ratio>0.35 → exit_code=3。

**描述质量检查**（v5.7.0移至此处）：报告输出前执行。详见 `references/description-quality.md`。语言自适应→格式检查→精炼→翻译→双语拼接。同义字词扩展。审计后自检 skills-audit 自身描述。仅在需要输出报告时才执行描述检查。

条件输出：有内容才输出，无内容不兜底。`$AUDIT_MODE="project"` 跳过深度分析+描述优化。模板见 `references/report-template.md`。

### ⑥-bis 审计验证

数据一致性检查（评分-画像一致、Community回填、理由完整、推荐无冲突、去重）+ 抽样交叉验证 + **评分-决策一致性追踪（v5.7.0新增）**。对比上次审计用户决策与本次评分的一致性，累积 ≥5 次偏差数据后触发权重微调建议。

### ⑥-c 报告输出强制检查

确认报告已输出、$PROFILE_READY=true、评分表已生成。未输出则强制终止先输出报告。

### ⑦ 执行

用户确认后执行。仅用户层技能（editable=true）可修改。系统技能只读。操作：归档、修改描述、安装、更新、回滚。

**审计反馈收集（v5.7.0新增）**：所有操作执行完成后，输出简短反馈问卷：

```
📊 本次审计效果如何？
  [1] 有帮助，会按建议执行
  [2] 部分有用，有些建议不适用
  [3] 帮助不大，评分/推荐不准确
  [4] 跳过反馈
```

反馈写入 `stats.json` 的 `user_feedback` 数组，长期用于优化评分权重和推荐策略。

### ⑧ 持久化

画像双写 · 统计 · 日志 · 缓存 · 快照 · 自检缺陷追踪。**缓存GC（v5.7.0新增）**：清理 `external-signals-cache.json` 中不在当前技能列表中的条目。失败不阻塞主流程。

---

## 项目类型识别规则

详见 `references/project-types.yaml`。核心推断规则：

- **主特征定类型**: `package.json`→Web/Node/全栈 · `Cargo.toml`→Rust · `pyproject.toml`→Python · `go.mod`→Go · `pom.xml`/`build.gradle`→Java · `.csproj`→C# · `pubspec.yaml`→Flutter · `CMakeLists.txt`→C/C++ · `Gemfile`→Ruby
- **AI Agent增强**: 多 `SKILL.md` + `MEMORY.md` → `⭐AI Agent 技能开发`
- **辅助识别**: `requirements.txt`含pandas/numpy→数据科学 · `Dockerfile`→容器化
- **多特征叠加**: 多类型共存时合并
- **复合类型识别（v5.7.0新增）**: 检测到多个独立类型时生成复合类型（如 `Web全栈-React+Express`），并为复合类型合并各子类型的推荐技能列表（取并集+去重）

---

## 边界规则（快速参考）

- **触发**：独立词触发，句中不触发。详见触发方式章节
- **分层**：T1/T2/T3 以画像"核心活动"为唯一尺度
- **评分**：五档 S/A/B/C/D + 强制理由，无理由=未评分
- **深度分析**：必读全文正文，缺口须经工具验证
- **报告**：条件输出，空区无兜底
- **推荐**：每项附带信心指数 0-10 + ROI，<5 自动不推荐
- **确认执行**：操作需用户确认；系统技能只读
- **黄金法则**：先搜索验证，≥2 来源

---

## 平台配置

支持平台：`platforms/zcode.yaml` · `platforms/workbuddy.yaml` · `platforms/claude.yaml` · `platforms/codex.yaml` · `platforms/cursor.yaml` · `platforms/default.yaml`。

### CI/CD 集成（v5.8.0 新增）

触发方式：`技能审查 --ci` 或 `skills-audit --ci`

| 配置项 | 默认值 | 说明 |
|:---|:---|:---|
| `ci.max_tokens` | 8000 | CI 模式 Token 预算上限 |
| `ci.skip_steps` | `["④-bis"]` | 跳过的步骤列表 |
| `ci.output_format` | `json` | 输出格式（json） |
| `ci.gates.health_min` | `🟡` | 健康度门禁 |
| `ci.gates.t3_ratio_max` | 0.35 | T3 占比上限 |
| `ci.gates.actions_max` | 5 | 最大操作数 |

GitHub Actions 模板见 `references/ci-github-actions.yml`。

### SkillSpector 安全扫描（v5.8.0 新增）

配置项 `config.yaml` → `security_scan`：
- `enabled: true` 启用，`tool: "skillspector"` 或 `"builtin"`（内置轻量规则）
- 扫描结果融入 Value 维度（Critical→D, High→C, 通过→+0.5档）
- SkillSpector 为外部进程，不消耗 Agent Token
