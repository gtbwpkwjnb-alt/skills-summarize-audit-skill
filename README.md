# Skills-Summarize-Audit v8.2.4

已安装技能与插件问题审查、版本/可用性核验、用户画像定位与评分、冲突/互补分析、技能翻译精炼、项目画像与工具推荐。默认只读，不负责安装、更新、发布、配置、迁移或历史清理。

## 核心能力

| 能力 | 输入 | 输出 |
|---|---|---|
| 已安装技能/插件问题审查 | 当前真实安装登记、技能和插件来源 | 问题严重度、证据、版本、可用性和处理方案 |
| 用户画像定位与评分 | 用户画像、结构化使用证据和技能元数据 | 画像命中词、健康维度、评分和证据状态 |
| 冲突与互补分析 | 可解释触发词、能力和画像关系 | 冲突/互补/无关关系、重叠度和理由 |
| 技能说明翻译精炼 | 侧栏与命令栏完整可见 ID 集合 | 保留英文名称的中文 `short_description` 候选、质量和来源门禁 |
| 项目画像 | 当前或指定项目目录 | 技术栈、项目类型、扫描覆盖和技能推荐 |
| 技能/插件推荐 | 翻译清单、项目画像或明确缺口 | 保留/升级/替换/引入/共存/归档建议及证据 |

## 触发

- `技能审查`：审查已安装技能/插件问题、版本、画像匹配、评分、冲突/互补，并按请求组合翻译、画像和推荐。
- `技能问题审查` / `插件问题审查`：运行本地只读问题检测，输出证据、严重度和处理方案。
- `技能翻译精炼` 或 `技能审查 精炼`：只生成翻译候选。
- `项目画像`：只生成当前项目的事实画像。
- `技能推荐` 或 `插件推荐`：只输出建议。

触发词应独立发送。详细规则见 [SKILL.md](SKILL.md)。

## 边界

- 不写入 Codex UI、插件缓存、系统技能、配置或项目文件。
- 不负责安装、更新、卸载、发布、CI/CD、回滚、桌面迁移、环境修复或历史清理；只输出可执行处理建议。
- 报告发现这类后续工作时，只建议用户直接调用对应 Agent，并说明所需输入与确认边界。
- 外部搜索需要用户明确同意；无证据时输出 `unavailable`。

## 验证

```powershell
python tests/validate.py --strict
python tests/test_collect_codex_display_candidates.py
```

## 环境依赖

- `scripts/analyze_project_profile.py` 需要 PyYAML：`pip install -r requirements.txt`。缺失时脚本不再直接崩溃，而是以退出码 2 输出 `unavailable` 降级信息，相关测试与 validate 的项目画像门禁自动跳过。
- `scripts/collect_codex_display_candidates.py` 与 `scripts/audit_skill_plugin_issues.py` 仅需标准库 + `tomllib`（要求 Python ≥ 3.11）；PyYAML 对 collect 脚本为可选依赖，缺失时自动降级。

## 脚本参数

三个脚本均为只读；完整参数以各脚本 `argparse` 定义为准（`-h` 查看）。

**`scripts/analyze_project_profile.py`**（项目画像，需 PyYAML）

| 参数 | 说明 |
|---|---|
| `project`（位置参数） | 待扫描项目目录 |
| `--max-files`（默认 2000） | 扫描文件数上限 |
| `--max-depth`（默认 10） | 目录遍历深度上限 |
| `--json` | 输出 JSON 画像 |

**`scripts/collect_codex_display_candidates.py`**（Codex 展示候选采集）

| 参数 | 说明 |
|---|---|
| `--root` / `--catalog-dir` / `--runtime-dir` / `--user-skill-dir` | 各来源目录覆盖（root 默认 `$CODEX_HOME` 或 `~/.codex`） |
| `--scope`（visible/installed/catalog/all） | 采集范围，默认 visible |
| `--visible-id`（可重复） | 当前 UI 可见技能 ID |
| `--expect-visible-count` / `--provided-visible-count` | 可见数量门禁 |
| `--batch-size` / `--offset` | 分批精炼输出（零基偏移） |
| `--require-chinese` / `--require-ready` / `--fail-on-source-conflict` / `--check-unchanged` | 质量与一致性门禁 |
| `--json` | 输出 JSON |

**`scripts/audit_skill_plugin_issues.py`**（技能/插件问题审查）

| 参数 | 说明 |
|---|---|
| `--root` / `--catalog-dir` / `--runtime-dir` / `--staging-dir` / `--user-skill-dir` | 各来源目录覆盖 |
| `--profile` | 用户画像文件；缺失时 profile_alignment=unavailable |
| `--scope`（installed/visible/all） | 审查范围，默认 installed |
| `--visible-id`（可重复） | 用户提供的可见技能 ID |
| `--fail-on`（none/info/warning/critical） | 严重度门禁 |
| `--detail` / `--json` | 逐项明细 / JSON 输出 |
