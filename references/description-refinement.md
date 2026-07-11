# Description Refinement — 描述精炼与翻译优化

> v1.0.0 | 联动 Forma 格式分（八维评分第 8 维）
>
> 一次执行即可发现所有描述问题位置、执行精炼翻译、清理残留、报告不可翻译项。

---

## 1. 精炼标准（Forma 规则）

| 检查项 | 合格标准 | 不合格示例 |
|:-------|:---------|:-----------|
| **格式规范** | `主题 → 功能1·功能2·功能3` 箭头短语 | 完整句子、纯段落 |
| **语言一致性** | 全中文（标准缩写除外：MCP/TDD/PR/TS/Python/API/Git） | 中英混搭、整段英文 |
| **长度合规** | 单侧 ≤40 字符 | 超长描述含使用说明 |
| **信息密度** | 纯功能短语，无杂质 | 含触发条件、使用说明、版本号 |

### 标准缩写白名单

```
MCP  TDD  PR  TS  Python  API  Git  JSON  CLI  IDE
ACP  DOCX  iOS  AI  URL  SSH  HTTP  SSL  SQL
```

---

## 2. 描述位置发现

### 2.1 用户自制技能

扫描以下路径下的 `SKILL.md`，读取 `description:` 字段：

```
~/.agents/skills/*/SKILL.md
~/.zcode/skills/*/SKILL.md           # 部分平台有此路径
~/.claude/skills/*/SKILL.md          # 部分平台有此路径
~/.codex/skills/*/SKILL.md           # Codex 用户技能
$CODEX_HOME/skills/*/SKILL.md        # Codex 全局技能（排除 .system/.archived）
```

**扫描命令**（跨平台）：
```bash
# Linux/macOS
find ~/.agents/skills ~/.zcode/skills ~/.claude/skills -name SKILL.md 2>/dev/null

# Windows PowerShell
Get-ChildItem "$env:USERPROFILE\.agents\skills\*\" -Filter SKILL.md -Recurse
```

### 2.2 Codex 展示源（插件与 runtime）

插件技能存放路径因平台而异，常见的模式：

```
~/.zcode/cli/plugins/cache/*/*/skills/*/SKILL.md
~/.cache/codex-runtimes/*/plugins/*/plugins/*/skills/*/SKILL.md
$CODEX_HOME/plugins/cache/*/*/skills/*/SKILL.md
$CODEX_HOME/cache/remote_plugin_catalog/*.json
```

### 1.1 中文候选生成顺序

1. 保留技术术语：`API`、`CLI`、`MCP`、`Codex`、`GitHub`、`YAML` 等不得意译或删除。
2. 优先匹配 `codex-ui-zh-glossary.json` 的精确短语；该结果可标 `ready`。
3. 未命中时，先根据英文原文翻译完整语义，再按 Forma 压缩为“对象 → 动作·范围·结果”。不得逐词拼接，不得丢失限定词。
4. 无法确认语义时标 `needs_agent_refinement`，保留英文原文和绝对来源路径，不输出“已完成翻译”。

GitHub 调研记录：Argos Translate（MIT）提供离线语言包机制，但其模型与运行时依赖较重；本技能不捆绑模型。未来仅在用户明确要求离线机翻并确认模型下载后，将其作为可选后端，而不替代本地术语表和语义复核。

对每个插件，读取 `SKILL.md`、可选 `agents/openai.yaml`、上级 `.codex-plugin/plugin.json`；remote catalog 的 `skills[].interface.display_name` 与 `short_description` 是命令栏/侧边栏展示候选来源。优先展示元数据，缺失时回退 `SKILL.md description`。

> Codex runtime、插件 cache、remote catalog 和 `$CODEX_HOME/skills/.system/` 为只读：只报告中文候选，不修改缓存、UI 或系统文件。

`remote_plugin_catalog` 是市场可发现元数据，不等于已安装或当前启用。审计统计必须使用采集器的 `--scope installed`：按技能 id 去重后计算健康度、容量和翻译积压；catalog-only 仅作为市场展示候选单列。

### 2.3 技能索引文档（人工维护的参考）

```
{project}/skills/SKILLS_INDEX.md     → "用途" 列
```

> ⚠️ 此文件是人工维护的参考文档，不是 `/` 菜单的数据源。
> 修改描述时应以 SKILL.md 为准，SKILLS_INDEX.md 同步更新即可。

### 2.4 平台内置项（不可修改）

| 项 | 不可修改原因 |
|:---|:-------------|
| 系统内置命令（/help, /clear 等） | 客户端硬编码，无对应 SKILL.md 文件 |
| 子智能体管理（如有） | 客户端硬编码，无对应 SKILL.md 文件 |
| MCP 服务器工具描述 | 由各 MCP 服务端源码定义 |

> 这些项在审计报告中标注为 `🛑 不可翻译` 并说明原因，跳过修改。

---

## 3. 清理项检测

### 3.1 残留配置引用

部分平台的配置文件中可能存在指向已删除技能的死引用。常见的检查位置：

```
# 扫描配置文件中的 skills 段，检查引用的 SKILL.md 是否仍存在
```

**检查逻辑**：
1. 找到当前平台的技能配置文件（如 `config.json`）
2. 读取配置中的 skills 引用列表
3. 对每个引用路径，检查文件是否存在
4. 不存在 → 标记为残留引用，建议清除

### 3.2 已归档技能

```
~/.agents/skills/archived/
```

**建议**：
- 确认不再需要的 → 永久删除
- 需要保留备份的 → 移出 `~/.agents/skills/` 扫描路径

### 3.3 已禁用插件

如果平台有插件系统且配置文件中存在已禁用的插件引用，
确认不再使用后，建议彻底卸载。

---

## 4. 执行流程

### 步骤 ①：全面发现

```
1. 扫描所有 SKILL.md → 提取 description 字段
2. 扫描 SKILLS_INDEX.md → 提取用途列（如有）
3. 扫描配置文件 skills 段 → 标记残留引用
4. 读取 archived 目录 → 标记待清理项
```

### 步骤 ②：分类评估

对每个 description 按 Forma 4 项规则评分：

| Forma 分 | 等级 | 处理方式 |
|:---------|:-----|:---------|
| 10/10 | ✅ 合格 | 跳过 |
| 6-9/10 | ⚠️ 微调 | 自动精炼 |
| 0-5/10 | 🔴 需重写 | 按标准重写 |

### 步骤 ③：生成候选

**转换规则**：

```
原始: "Use when the user wants to search the internet across multiple platforms..."
    → 精炼: "互联网调研 → 13渠道·多平台·信息获取"

原始: "当用户独立发送 `总结`/`summarize` 或相关子命令..."
    → 精炼: "会话精炼 → 进度追踪·错误收割·分层记忆写入"

原始: "DOCX document creation with support for revisions, comments..."
    → 精炼: "DOCX文档 → 创建·编辑·修订·格式保留·提取"
```

对于 Codex 官方插件、runtime 和 remote catalog，此步骤只生成清单，不提供写入命令。用户自制技能的 frontmatter 修改仍需单独确认。

### 步骤 ④：清理残留

```
1. 配置文件 skills 段 → 删除不存在的引用
2. archived/ 中确认废弃 → 永久删除
3. 已禁用插件 → 确认后删除
```

### 步骤 ⑤：报告不可翻译项

```
🛑 不可翻译（平台内置，无 SKILL.md）：
  - 系统内置命令：/help, /clear, /exit 等
  - 子智能体管理
  - MCP 工具描述（需修改服务端源码）
```

---

## 5. 输出报告格式

```
📋 描述精炼审计报告

=== A. 已精炼（X 项）===
| 技能 | 原始 | 精炼后 |
|------|------|--------|
| xxx  | ...  | ...    |

=== B. 已清理（X 项）===
| 清理项 | 类型 | 操作 |
|--------|------|------|
| skillfather | 归档残留 | 永久删除 |
| old-skill-ref | 配置残留 | 清除引用 |

=== C. Codex 命令栏与侧边栏中文翻译清单===
| 标识 | 命令栏原文 | 中文候选 | 侧边栏原文 | 中文候选 | 来源 | 状态 |
|------|-----------|----------|------------|----------|------|------|
| xxx | ... | ... | ... | ... | remote_plugin_catalog | observed / 只读 |

=== D. 不可翻译（X 项）===
| 项 | 原因 |
|---|------|
| /help 等命令 | 平台内置，无 SKILL.md |
| 子智能体 | 平台内置，无 SKILL.md |
```

---

## 6. 历史教训（防止重复踩坑）

| 教训 | 详情 |
|:-----|:------|
| ❌ 别改 SKILLS_INDEX.md 作为菜单源 | 它是人工参考文档，不是 `/` 菜单数据源 |
| ❌ 别改 plugin cache 或 remote catalog | 不存在已验证的安全 UI 覆盖接口；缓存可能被更新覆盖 |
| ✅ `SKILL.md` 只负责技能触发元数据 | 插件 UI 展示还可能来自 `agents/openai.yaml` 与 remote catalog `interface` |
| ✅ 使用只读候选清单 | 通过绝对来源路径和事实状态帮助用户理解英文条目 |
| ✅ 插件技能只标注不修改 | 官方插件、runtime、catalog 仅出候选，不提供写入动作 |
