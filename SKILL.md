---
name: skills-audit
version: "4.2.0"
description: 项目技能审计 → 项目角色画像驱动。四维评分(含外部⭐+描述质量)，自动精炼技能描述为触发词→功能简介。5块报告，已安装≠网络推荐。支持 ZCode / Claude Code / Codex / Cursor / Windsurf。
           Project Skill Audit → role-profile driven. 4D scoring (external stars + description quality), auto-optimize descriptions. 5-block non-collapsing report. Multi-platform.
user-invocable: true
---

# Skills Audit v4.2 — 画像驱动 · 四维评分 · 描述精炼 · 5块报告

> **四大核心能力**: ①项目角色画像驱动 ②四维评分(含外部⭐+描述质量) ③自动精炼技能描述为触发词→功能简介 ④5块永不塌缩报告。
>
> **核心原则**: 画像驱动一切。有分才有据。描述必查。报告从不塌。

---

## 触发方式

| 平台 | 触发 | 示例 |
|------|------|------|
| **ZCode** | `skills-audit` 或 `技能审查` 或 `项目审计` | `> skills-audit ./my-project` |
| **Claude Code** | `/skills-audit` | `> /skills-audit ./my-project` |
| **Codex** | `skills-audit` 或 `项目审计` | `> skills-audit ./my-project` |
| **Cursor** | `@skills-audit` | `> @skills-audit ./my-project` |

**参数**: 项目路径可选。不传则用当前工作目录。
**只认独立词触发**。句子中不触发。

---

## 执行流程

### ⓪ 加载配置

读取同目录下 `config.yaml`，确定：
- `scan_paths` — 要扫描的技能/工具存放目录
- `project_scan` — 项目扫描配置（忽略模式、最大深度等）
- `version_check` — 版本检查源 URL
- `data_dir` — 持久数据目录

然后读取 `references/project-types.yaml` 加载项目类型→推荐技能映射表。
然后读取 `references/skill-registry.yaml` 加载已知技能注册表（含版本号和分类）。

> 找不到 references 文件时报 warning，继续执行（降级为仅靠 web 搜索推荐）。

### ① 项目扫描

扫描用户指定的项目目录（或当前工作目录），提取：

**基础信息:**
- 项目名称（从目录名或 `package.json` `name` 字段）
- 项目根路径

**文件特征（尊重 `.gitignore`，不扫描 node_modules/.git/.venv 等）:**
- 语言文件：`.py`, `.js`, `.ts`, `.rs`, `.go`, `.java`, `.cs`, `.rb`, `.c`, `.cpp` 等
- 配置文件：`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `CMakeLists.txt`, `.csproj`, `Gemfile`, `Dockerfile`, `docker-compose.yml`, `.github/`, `.gitlab-ci.yml`
- 框架标识：在 `package.json` dependencies 中查找 React/Vue/Angular/Express/Nest/Next/Nuxt 等
- 测试文件：`*.test.*`, `*.spec.*`, `__tests__/`, `test/`

**推断项目类型并构建项目角色画像：**

依次匹配 `references/project-types.yaml`。然后根据文件特征充实为**项目角色画像**（这是后续所有分析的核心锚点）：

```
┌─ 项目角色画像 ─────────────────────────────────┐
│ 类型    <从 project-types.yaml 匹配>              │
│ 活动    <从文件特征推断的 3-5 个核心开发活动>      │
│ 产物    <主要文件类型和输出格式>                   │
│ 痛点    <从项目结构推断的 2-3 个潜在效率瓶颈>      │
└───────────────────────────────────────────────┘
```

画像示例（React 项目）：
```
类型   Web前端 (React + TypeScript)
活动   组件开发 · 状态管理 · 路由配置 · 构建优化 · 测试编写
产物   .tsx · .css · .test.tsx · dist/
痛点   状态管理复杂度 · 组件拆分粒度 · SSR 调试
```

画像示例（ZCode 技能开发项目）：
```
类型   ZCode 工作区配置 / 技能管理
活动   技能编写 · Agent 编排 · 工具链优化 · MCP 集成 · 规则维护
产物   SKILL.md · AGENTS.md · YAML · .mjs · 安装脚本
痛点   跨项目技能复用 · 版本追踪 · 冗余清理 · 新技能发现
```

> **画像即锚点**：后续所有步骤（分层、评分、搜索）都以此为尺度。

### ② 已安装技能清单

扫描 `config.yaml` 中所有 `scan_paths`，提取每个技能的：
- `name`、`description`、路径、来源（user/system）、版本号（从 SKILL.md frontmatter 或 VERSION 文件读取）、可编辑性

**分类**：
- **用户技能**（editable=true，用户可自行增删改）
- **系统/插件技能**（editable=false，来自插件缓存）

**输出:**
```
🔍 已安装技能: 用户 2 个 + 系统/插件 17 个
```

### ③ 项目→技能匹配与初始筛选

将项目角色画像与 `references/project-types.yaml` 交叉：
- 匹配到的技能记入 **T1 候选集**（项目类型直接推荐）
- 同时从 `references/skill-registry.yaml` 获取每个已安装技能的版本号和分类

> 此步为初筛。最终层级和评分由步骤④决定，不由 project-types.yaml 单方面裁决。

### ④ 三级分层 + 四维评分 + 描述检查

**第一步：三级分层（以项目角色画像的"活动"为尺子）。**

| 层级 | 规则 | 动作 |
|------|------|------|
| **T1 核心** | 技能的主要用途直接命中"核心活动"中的某一项 | 保留（自动） |
| **T2 通用** | 技能不局限于特定项目类型，当前项目可用，无负面影响 | 保留 |
| **T3 专业** | 技能为特定项目类型设计，与"核心活动"零交集 | 建议归档 |

> 判定密钥：把技能的 description 和项目画像的"活动"做交集。有交集 → T1；无交集但通用类别(debug/docs/review/管理/验证/设计等) → T2；明确服务其他类型(Android/iOS/特定迁移) → T3。

**第二步：四维评分（仅已安装技能，每技能 0-100）。**

| 维度 | 权重 | 计算方式 |
|------|------|---------|
| **Fit** 项目匹配 | 40% | T1 → 85–100；T2 → 50–84；T3 → 0–49。与"核心活动"重合项数每多 1 项 +3，无重合 −5 |
| **Value** 通用价值+描述质量 | 20% | ①类别分：debug/验证/审查/管理 → 80–100；设计/规划 → 70–89；文档/笔记 → 55–75；单一平台 → 30–55。②描述质量分：中文且格式合格 → +10；仅英文 → −10；超长/多行 → −10 |
| **Fresh** 版本时效 | 20% | 版本 = registry 最新 → 100；落后 1 大版本 → 60；registry 无记录 → 50；落后 2+ → 30 |
| **Community** 外部信号 | 20% | GitHub ⭐：≥1000 → 100，≥100 → 80，≥10 → 60，<10 → 30；npm 📥：≥1000/w → 100，≥100/w → 70，<100 → 40；最近更新：1月内 → 100，6月内 → 70，1年内 → 50，>1年 → 20。无公开 repo → 40 |

**总分 = Fit×0.4 + Value×0.2 + Fresh×0.2 + Community×0.2**

分数 → 建议：≥70 ✅保留 · 40–69 🟡保留(低频) · <40 ❌建议归档

**第三步：描述质量检查（每个已安装的用户可编辑技能）。**

检查项与优化规则：

| 检查项 | 规则 | 不合格的处理 |
|--------|------|-------------|
| 语言 | 中文优先。纯英文→优化为中文 | 自动生成中文化版本 |
| 格式 | 必须遵循 `触发词 → 功能简介` | 自动重排为规范格式 |
| 长度 | 单行，≤40 字符 | 截断并保留核心语义 |
| 双语 | 中英双语最佳 | 单语也接受，不扣分 |

> 系统/插件技能（editable=false）只标注问题，不自动修改。

**评分表行格式（已安装技能）：**
```
#N  技能名           分  层级  ⭐外部信号  简评(≤12字)
```

示例：
```
#1  skill-creator    89  T1    内置·官方   技能创作核心
#5  sub-agents       78  T1    ⭐44·6月新  跨LLM子代理
```

### ⑤ 画像驱动的网络搜索 + 外部信号

**搜索关键词从画像提取：**
```
从画像.活动 提取英文关键词 → 组合为搜索串
从画像.痛点 提取英文关键词 → 补充为第二搜索串
示例: "skill authoring, agent orchestration"
     → "AI coding agent skill management tool 2026"
```

**同时获取外部信号（与搜索并行）：**

对每个来自 GitHub/npm/PyPI 的技能，获取：
```
GitHub: WebFetch api.github.com/repos/{owner}/{repo}
        → stargazers_count, pushed_at, description
npm:    WebFetch api.npmjs.org/{package}/latest
        → version, weekly downloads
PyPI:   WebFetch pypi.org/pypi/{package}/json
        → info.version, downloads
```

> 一次 WebFetch 拿齐 ⭐ + 最后更新 + 描述。信号填入 Community 维度和评分表的"外部信号"列。

**结果格式（分为两区）：**

网络推荐的备选技能（未安装）→ 单独 `🌐 网络推荐` 区域：
```
🆕 [来源] · 技能名  ⭐X · 更新状态
    <12字描述> · 当前项目适配理由
```

对外部技能的描述同样执行描述质量检查，不符合规范的在推荐时就给出优化版。

### ⑥ 生成报告

报告固定 5 块，每块必定输出。禁止宽表格。

```
════════════════════════════════════════════════
📋 项目角色画像
════════════════════════════════════════════════
类型   <画像.类型>
活动   <画像.活动>
产物   <画像.产物>
痛点   <画像.痛点>
════════════════════════════════════════════════
健康度  N个 · 均分XX · T1:X T2:X T3:X
════════════════════════════════════════════════

📊 已安装技能评分（仅已安装，按分降序）
#  技能              分  层级  ⭐外部信号    简评
 1 skill-creator    89  T1   内置·官方     技能创作核心
 2 summarize        75  T2   本地·无repo   会话精炼，日常高频
 3 docx             65  T2   内置·官方     文档工具，偶尔用
 ...
22 android-dev      36  T3   内置·官方     专为Android，无交集
════════════════════════════════════════════════

📝 描述优化（N个）—仅已安装且描述不符合规范
#  技能              问题              建议
 1 brainstorming     纯英文，格式不符   头脑风暴 → 需求澄清·创意发散·方案对比
 2 systematic-debug   纯英文             系统化调试 → 假设驱动·二分定位·根因分析
 ...
── 描述全部合格，无需优化 ── （无不合格项时的兜底）
════════════════════════════════════════════════

🌐 网络推荐备选（未安装，供评估）
🆕 AllAgents (npm)       v1.11.9 · 📥577/w   跨23客户端技能同步
🆕 Mega-Mind (pypi)      v0.4.0 · ⭐?          42技能+自进化工作流
 ...
── 本次未搜索到推荐备选 ── （无结果时的兜底）
════════════════════════════════════════════════

📌 操作
[1] 归档 android-dev       T3/36分  专为Android，无交集
[2] 优化描述 brainstorming   纯英文→中文化
[3] 评估 🆕 AllAgents        跨平台技能管理
 ...
── ✅ 无需调整，当前搭配合理 ──
════════════════════════════════════════════════
```

**规则**：
- 画像+健康度 → 必定输出。
- 📊 评分表 → 仅已安装技能，按分降序。每条含外部信号(⭐/📥/更新状态)。未安装的不在此列。
- 📝 描述优化 → 必定输出。检查语言/格式/长度。无不合格时显示兜底文本。
- 🌐 网络推荐 → 必定输出。未安装的外部推荐，每条 ≤1 行。无结果时显示兜底。
- 📌 操作 → 必定输出。有序号 [1][2]...，操作可以是归档/优化描述/安装/关注。

### ⑦ 执行（用户确认后）

只操作用户层技能（editable=true），不碰系统/插件层。

- **归档**：技能目录移入 `config.yaml` 的 `archive_dir`
- **安装**：给出安装命令示例（clone / 下载 / 安装脚本）
- **更新**：给出更新方式
- **搜索安装**：给出来源 URL

### ⑧ 持久化（始终执行）

1. 项目画像 → 合并写入 `project-profiles.json`
2. 运行统计 → 更新 `stats.json`
3. 审计日志 → 追加 `activity-log.jsonl`

**持久化失败不阻塞主流程**。

---

## 项目类型识别规则

详见 `references/project-types.yaml`。核心规则：

| 特征 | 推断类型 | 推荐优先级 |
|------|---------|-----------|
| package.json 含 react/react-dom | Web前端-React | 高 |
| package.json 含 vue/vue-router | Web前端-Vue | 高 |
| package.json 含 @angular/core | Web前端-Angular | 高 |
| package.json 含 express/koa/fastify | Node后端 | 高 |
| package.json 含 next | Web全栈-Next.js | 高 |
| Cargo.toml | Rust | 中 |
| pyproject.toml / requirements.txt | Python | 中 |
| go.mod | Go | 中 |
| pom.xml / build.gradle | Java | 中 |
| SKILL.md (多文件) | ZCode技能开发 | 高 |
| .csproj | C#/.NET | 中 |
| Gemfile | Ruby | 中 |
| Dockerfile | 容器化 | 低（辅助） |

多特征叠加时合并推断（如 package.json 含 react + express → "全栈: React+Express"）。

---

## 建议三段式解释规范

每条可操作建议（冗余/缺失/更新/备选）包含三段解释：

| 段落 | 标签 | 长度 | 要求 |
|------|------|------|------|
| 原因 | `🔍 原因:` | ≤1 行 | 基于项目具体特征的因果逻辑 |
| 效果 | `💡 效果:` | ≤1 行 | 可量化或可感知的预期改善 |
| 场景 | `🎯 场景:` | ≤1 行 | 日常工作流中的具体使用入口 |

**精炼规则**：
- 每句不超过 40 个字。超过则拆分，拆分仍超则删冗余词。
- 保留项（✅）不加三段解释——已知在用无需说服。
- 禁止空泛词（"提升开发效率"、"最佳实践"、"增强代码质量"）——必须说明**通过什么机制、达到什么效果、在什么场景用**。

---

## config.yaml 格式

```yaml
# skills-audit v4.0 配置
data_dir: "$SKILL_DIR"           # 数据存放目录
archive_dir: "$SKILL_DIR/../archived"  # 归档目录

scan_paths:
  - name: "用户技能"
    path: "~/.zcode/skills/*/"
    type: user
    editable: true
  - name: "用户技能(.agents)"
    path: "~/.agents/skills/*/"
    type: user
    editable: true
  - name: "插件工具"
    path: "~/.zcode/cli/plugins/cache/*/*/skills/*/"
    type: system
    editable: false

# 项目扫描配置
project_scan:
  max_depth: 10                  # 最大扫描深度
  max_files: 1000                # 最多扫描文件数
  ignore_patterns:               # 忽略模式（默认值，不可覆盖 .gitignore）
    - "node_modules"
    - ".git"
    - ".venv"
    - "__pycache__"
    - "dist"
    - "build"
    - ".next"
    - "target"
    - "vendor"

# 版本检查
version_check:
  enabled: true
  # registry_url 为空时仅依赖本地 skill-registry.yaml
  registry_url: ""
  # 搜索关键词模板（用于 web 搜索补充）
  search_template: "{skill_name} ZCode skill latest version"

# 输出语言
output_language: "auto"  # auto / zh / en
```

---

## 自测验证

每次修改后验证：

1. **项目扫描测试**：在 2 个不同类型的项目上运行步骤①，确认类型推断正确
2. **匹配测试**：已知项目类型→检查推荐技能列表是否合理
3. **冗余检测测试**：添加一个不匹配的技能，确认被标记为冗余
4. **持久化测试**：确认 `activity-log.jsonl` 可写且格式正确

---

## 边界规则

- **触发**：仅 `skills-audit` / `技能审查` / `项目审计` 独立打出
- **路径参数**：支持绝对路径和相对路径；路径不存在时报错终止
- **三级分层**：T1/T2/T3 判定以项目角色画像的"核心活动"为唯一尺度，禁止退回全局/领域二分
- **评分必出**：每个已安装技能必须有分数+层级+外部信号+简评。未安装技能不进评分表
- **描述优化必出**：每个已安装技能的 description 必须检查语言/格式/长度，不合格的自动生成优化版。系统插件仅标注不修改
- **报告 5 块永不塌缩**：画像·评分·描述优化·网络推荐·操作，每块必定输出。空区显示兜底文本
- **已安装≠网络推荐**：评分表仅限已安装技能。网络推荐独立区域，不加分号，标 🆕
- **外部信号必取**：对有公开仓库的技能，搜索时并行获取 GitHub⭐/npm📥/更新时间
- **确认**：步骤⑦必须等用户确认后才执行操作
- **不自动执行**：归档/安装/更新/描述修改必须用户确认
- **不碰系统工具**：系统工具只评分+标注，不自动修改
- **Web 搜索降级**：网络不可用时跳过步骤⑤，不影响其他步骤。外部信号用 registry 缓存值兜底
- **references 文件缺失降级**：使用内置默认规则，不阻塞
- **始终持久化**：⑧ 在每次运行末尾执行，不依赖⑦
- **输出精炼**：禁用 >60 字符宽的表格；评分表每条 ≤1 行；同类栏目不分散

### 内置默认规则（references 文件缺失时使用）

```yaml
# 硬编码的极简规则，仅当 references/project-types.yaml 不存在时生效
project_types:
  - pattern: "package.json"
    type: "Node.js/JavaScript"
    recommended: ["test-driven-development", "systematic-debugging"]
  - pattern: ".py"
    type: "Python"
    recommended: []
  - pattern: "Cargo.toml"
    type: "Rust"
    recommended: []
  - pattern: "SKILL.md"
    type: "ZCode Skill"
    recommended: ["skill-creator"]
```

---

## 平台配置

参见 `platforms/zcode.yaml` 和 `platforms/default.yaml`（维持 v3.0 格式不变）。
