---
name: skills-audit
version: "3.1.0"
description: 审查技能 → 画像·评分·优化。多平台通用。
description_zh: 技能审查 → 画像·评分·优化。多平台通用。触发词：skills-audit / 技能审查。
description_en: Skills audit → profile · score · optimize. Multi-platform. Trigger: skills-audit.
user-invocable: true
---

# Skills Audit v3.0 — 画像 · 评分 · 优化（多平台通用）

> **设计目标**: 一键审查你的全部代理工具，找出短板、冗余和优化空间。
> **核心原则**: 先诊断后开方。不出无关数据。
> **平台**: ZCode / Claude Code / Codex / Cursor / Windsurf

---

## 触发方式

| 平台 | 触发 | 示例 |
|------|------|------|
| **ZCode** | 独立词 `skills-audit` 或 `技能审查` 或 `审查技能` | `> skills-audit` |
| **Claude Code** | `/skills-audit` | `> /skills-audit` |
| **Codex** | `skills-audit` 或 `审查技能` | `> skills-audit` |
| **Cursor** | 建议配置 `@skills-audit` | `> @skills-audit` |

> 只认独立词。在句子中不触发。

---

## 执行流程

### ⓪ 加载配置

读取同目录下 `config.yaml`，确定：
- 扫描路径（哪些目录包含你的工具/技能/插件）
- 数据目录（持久数据存放位置）
- 归档路径（低分工具移入）

**数据自包含**：所有持久数据存储在 `config.yaml` 的 `data_dir`（默认本技能目录）。

### ① 扫描

扫描配置中所有路径，提取各工具的：
`name`、`description`、路径、来源（user/system）、文件大小、可编辑性

输出："扫描到 N 个工具（用户 M + 系统 K）"

#### ①-A 语言检测

读取 `config.yaml` 的 `output_language`：
- `zh` / 系统语言为中文 → 优先使用 `description_zh`，回退 `description`
- `en` / 系统语言为英文 → 优先使用 `description_en`，回退 `description`
- `auto` → 自动检测：检查当前会话/系统语言环境，默认中文

扫描结果中展示的描述字段，始终使用当前语言匹配的版本。

### ② 用户画像

**首次** → 询问用户主要工作和常用工具（2个问题）。
**非首次** → 加载已有画像，输出：

```
**用户画像**（累计 N 次）：
- 主要工作：<类型>
- 高频工具：A(N次)、B(N次)、C(N次)
- 模式偏好：<语言偏好>
```

### ③ 项目画像

扫描工作目录 → 推断项目类型。输出：

```
**项目画像**（hash: X）：
- 类型：<推断类型>
- 文件特征：<文件类型>
- 工具数：N 个
```

### ④ 定位确认（**必须暂停等用户确认**）

```
**定位分析**：用户画像 + 项目画像
以上是否准确？回复"继续"→ 进入评分。
```

### ⑤ 多维评分

每工具 0-100，四维加权：

| 维度 | 权重 | 评分依据 |
|------|------|---------|
| **项目适配** | 35% | 工具功能与当前项目匹配度 |
| **留存趋势** | 30% | 历史使用频率 + 评分稳定性 |
| **描述质量** | 20% | 描述是否清晰、完整、双语（含当前语言版本）|
| **可维护性** | 15% | 用户可编辑 + 路径有效 + 格式完整 |

```
📊 评分总表
| # | 工具 | 描述 | 适配 | 留存 | 质量 | 维护 | 总分 | 建议 |
|---|------|------|------|------|------|------|------|------|
| 1 | xxx | xxx | 90 | 85 | 75 | 100 | 87 | 🟢 |
```

**分类**: ≥70 🟢保留 | 40-69 🟡观察 | <40 🔴归档

### ⑥ 优化建议

```
🔧 优化建议
### 描述修复
| 工具 | 当前 | 建议 |

### 双语描述补充（缺失 description_zh 或 description_en）
| 工具 | 缺失字段 | 建议补充 |

### 归档建议
| 工具 | 总分 | 原因 |

### 搭配建议
```
**描述语言规则**：
- 当前输出语言（从 `config.yaml` 读取）决定评分时展示哪个字段
- 若工具缺少当前语言的 `description_xx` 字段 → 在建议中提示补充
- 精炼建议始终基于当前匹配语言版本

**搭配建议规则表**（以下为通用规则，用户可在 `config.yaml` 中覆盖）：

| 条件 | 建议 | 理由 |
|------|------|------|
| 有审查工具无精炼工具 | 添加总结工具 | 审查+精炼互补 |
| 有计划工具无执行工具 | 添加执行工具 | 计划→执行闭环 |
| 有测试工具无调试工具 | 添加调试工具 | 测试→调试互补 |
| 工具 ≥ 10 | 运行审查清理 | 工具过多需定期整理 |
| 用户工具 < 3 | 添加创作类工具 | 工具生态起步需要创作工具 |

```
待确认操作：
  [ ] 修复 N 个描述
  [ ] 归档 N 个低分工具
回复"执行"开始操作，回复"跳过"仅保存评分数据。
```

### ⑦ 执行

- 描述修复：修改工具定义文件的 `description` 字段
- 双语补充：为缺少 `description_zh` 或 `description_en` 的工具添加对应字段
- 归档：移入 `config.yaml` 中的 `archive_dir`
- 只操作用户工具，不碰系统级

### ⑧ 持久化（**始终执行**）

1. 用户画像 → 写入 `data_dir/user-profile.md`
2. 项目画像 → 更新 `project-profiles.json`
3. 留存统计 → 每工具更新 `usage-<name>.json`
4. 运行统计 → 更新 `stats.json`
5. 活动日志 → 追加 `activity-log.jsonl`

**持久化失败不阻塞**。

---

## config.yaml 格式

```yaml
# skills-audit 配置
data_dir: "$SKILL_DIR"           # 数据存放目录（默认本技能目录）
archive_dir: "$SKILL_DIR/../archived"  # 归档目录

scan_paths:
  - name: "用户工具"
    path: "~/.zcode/skills/*/"
    type: user
    editable: true
  - name: "插件工具"
    path: "~/.zcode/cli/plugins/cache/*/*/skills/*/"
    type: system
    editable: false

# 可选：自定义搭配规则
custom_rules:
  - condition: "有 A 无 B"
    suggest: "添加 B"
    reason: "A+B 互补"

# 可选：描述质量检查维度
quality_checks:
  - name: "中文描述"
    weight: 20
  - name: "触发词清晰"
    weight: 20
  - name: "≤40字符"
    weight: 20
  - name: "单行无换行"
    weight: 20
  - name: "双语字段完整(description_zh+_en)"
    weight: 20

output_language: "auto"  # auto / zh / en
```

---

## 平台配置示例

### `platforms/zcode.yaml`

```yaml
platform: zcode
scan_paths:
  user: "~/.zcode/skills/*/"
  plugin: "~/.zcode/cli/plugins/cache/*/*/skills/*/"
archive_dir: "~/.zcode/skills-archived/"
trigger_words: ["skills-audit", "技能审查", "审查技能"]
```

### `platforms/default.yaml`

```yaml
platform: generic
scan_paths:
  user: "~/.agent-skills/*/"
  plugin: ""
archive_dir: "~/.agent-skills-archived/"
trigger_words: ["skills-audit"]
```

---

## 自测验证

每次修改后验证：

1. **日志写入测试**：向 `activity-log.jsonl` 追加一条测试事件，确认可写、格式正确
2. **usage 更新测试**：读取 `usage-*.json`，递增 `timesSeen`，写回确认
3. **评分计算测试**：取一个工具按四维公式手工计算，确认与 SKILL.md 规则一致
4. **配置加载测试**：读取 `config.yaml`，确认所有路径可访问

测试通过条件：4 项全部无报错。

---

## 反馈

🐛 [GitHub Issues](https://github.com/gtbwpkwjnb-alt/skills-audit-skill/issues/new)

---

## 边界规则

- **触发**：仅 `skills-audit` / `技能审查` / `审查技能` 独立打出
- **首次画像**：不允许推测，必须询问用户
- **确认**：步骤④必须暂停等用户确认
- **不自动执行**：修改/删除必须用户说"执行"
- **不碰系统工具**：系统工具只评分不修改
- **评分上限 15**：输出评分表最多 15 行
- **始终持久化**：⑧ 在每次运行末尾执行，不依赖⑦