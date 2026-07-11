# Agent 展示文案来源地图

审计“命令栏/输入框”和“侧边栏”时，先区分**展示位置**与**本地元数据来源**。只有标记为 `observed` 的映射才能作为精炼候选来源；客户端 UI 未直接验证时不得声称修改某文件即可改变该 UI。

## Codex（本机已验证）

| 展示对象 | 首选来源 | 回退来源 | 审计分类 | 可写性 |
|---|---|---|---|---|
| 技能命令栏名称 | `<skill>/agents/openai.yaml` → `interface.display_name` | `SKILL.md` frontmatter `name` | `codex_global_skill` / `codex_system_skill` | 用户技能可写；`.system` 只读 |
| 技能侧边栏短说明 | `<skill>/agents/openai.yaml` → `interface.short_description` | `SKILL.md` frontmatter `description` | 同上 | 同上 |
| 插件卡片/侧边栏名称与说明 | `<plugin>/.codex-plugin/plugin.json` → `interface.displayName` / `shortDescription` / `longDescription` | manifest `name` / `description` | `codex_plugin_manifest` | 只读 cache |
| 已安装插件技能 | `<plugin>/skills/<skill>/agents/openai.yaml` | 对应 `SKILL.md` | `codex_plugin_cache` / `codex_runtime_plugin` | 只读 cache/runtime |
| 市场可发现技能 | `$CODEX_HOME/cache/remote_plugin_catalog/*.json` → `plugins[].release.skills[].interface` | catalog skill `description` | `remote_plugin_catalog` | 只读；`catalog_only`，不计入已安装统计 |

本机验证样本：`D:\codex\plugins\cache\openai-curated-remote\openai-templates\0.1.0\skills\artifact-template-minimal-letterhead\agents\openai.yaml` 与其上级 `.codex-plugin\plugin.json`。

## ZCode（本机已验证的发现层）

| 对象 | 本地来源 | 已验证事实 | UI 映射状态 |
|---|---|---|---|
| 用户/项目技能 | `<project>/.zcode/skills`、`<project>/.agents/skills`、`~/.zcode/skills`、`~/.agents/skills` 下 `SKILL.md` frontmatter | `name` / `description` 是发现和触发元数据；路径优先级由 ZCode skill-creator 说明 | 命令栏/侧边栏具体渲染位置 `unavailable` |
| 已启用插件 | `~/.zcode/cli/config.json` → `plugins.enabledPlugins` | 只记录启用状态，不是说明文字来源 | `unavailable` |
| 插件命令 | `<plugin>/commands/*.md` frontmatter `description` | 可作为命令说明候选 | 需实际客户端验收 |

## Claude Code（本机插件示例已验证）

| 展示对象 | 来源 | 已验证事实 |
|---|---|---|
| `/help` 中用户调用技能/命令说明 | `skills/<name>/SKILL.md` 或 legacy `commands/<name>.md` frontmatter `description` | 本机 example-plugin 明确说明该字段显示于 `/help` |
| 插件 UI 标签 | marketplace 或 manifest 的 `displayName` | 本机 marketplace README 说明可用 `displayName` 更新 UI 标签；不修改 immutable slug |

## 通用 `.agents` 技能

`~/.agents/skills/<name>/SKILL.md` 的 `name` 与 `description` 是可审计的技能元数据，但 `.agents` 本身不定义命令栏或侧边栏渲染器。Audit 必须将具体 Agent 标为 `unavailable`，不能擅自映射到 Codex、ZCode 或 Claude UI。

## Audit 操作规则

1. 翻译精炼先取得侧栏和命令栏的可见性证据，再以 `collect_codex_display_candidates.py --scope visible --visible-id <id>` 逐项解析；绝不以 `installed`、`catalog` 或缓存发现结果替代可见性。
2. 输出中必须给出 `visibility_evidence`、`source_paths`、`source_type`、`inventory_scope` 与 `editable`；未显示项不输出。
3. official plugin cache、runtime、manifest、remote catalog 一律只读，只生成候选；修改后可见 UI 的说法必须由实际客户端验收支持。
4. 只有用户自制且 `editable=true` 的技能才可在确认后修改 frontmatter；修改后重新解析并执行严格验证。
5. 若需要证明某客户端的实际命令栏或侧边栏位置，使用客户端自动化或人工截图验收；文件层证据不能替代 UI 验收。客户端自动化不可用时，要求用户提供截图或可复制 ID 列表。
6. 应用中文候选后，必须以同一可见 ID 集合执行 `--require-chinese --expect-visible-count <n>`；缺少项、仍英文项或未完成两页截图验收时，报告 `partial`。
