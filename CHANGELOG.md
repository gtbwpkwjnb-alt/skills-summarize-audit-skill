# Changelog

All notable changes to the skills-audit skill.

---

## [5.9.3] - 2026-07-05

### Changed
- **技能改名**：`skills-audit` → `skills-summarize-audit`（全平台同步）
- **新增触发词**：`技能总结`（联动 summarize 品牌，触发技能审计模式）
- **SKILL.md 联动说明**：触发词章节标注与 summarize 的联动关系
- **When to Use**：增加「run summarize → 发现技能堆积 → 建议 `技能总结`」场景

### 文件变更
- 所有文件中的 `skills-audit` 名称引用更新为 `skills-summarize-audit`
- install.sh/install.ps1 仓库 URL 更新为新仓库
- skill-registry.yaml tag 增加 summarize
- VERSION 5.9.2 → 5.9.3

---

## [5.9.2] - 2026-07-05

### 改进
- **前置条件重构**：去平台约束、去 skillfather/skill-creator 多余依赖，硬/软分离，工具标注安装引导，user-profile.md 改为缺失时自动创建
- **frontmatter 精简**：`requires.configs` 移除 user-profile.md（非硬性依赖，改为自动创建）
- **冗余文件清理**：
  - 删除旧备份 `.SKILL.md.v5.1.bak`、`.VERSION.v5.1.bak`（git 已存历史）
  - 删除意外文件 `nul`（Windows 保留名）
  - 删除历史重定向 `references/workflow-details.md`
  - 删除零引用笔记 `references/learned/skills-audit.md`
  - 删除 `.github/ISSUE_TEMPLATE/`（3 文件）+ 空 `.github/` 目录
- **缓存迁移**：`external-signals-cache.json` 从根目录移至 `.data/`，对齐 config.yaml 路径配置
- **文件结构图更新**：移除 workflow-details.md 行，.data/ 注释补全外部信号缓存

---

## [5.9.1] - 2026-07-05

### P0 - 版本同步与修复
- **版本号统一**：VERSION / SKILL.md / README.md / skill-registry.yaml 同步至 5.9.1
- **7维权重修正**：Novelty 10% → 7%、Contamination 5% → 3%、Fresh 17% → 15%、Community 18% → 15%，权重和恢复 100%
- **平台 YAML 修复**：移除 `platforms/zcode.yaml`、`claude.yaml`、`codex.yaml`、`cursor.yaml` 中未闭合的 `"`
- **config.yaml 缩进修复**：插件技能路径恢复为 `scan_paths` 同级项
- **project-types.yaml 缩进修复**：`requirements.txt` 模式条目结构正确

### P1 - 文档对齐
- **七维评分替换**：移除 `workbuddy.yaml`、`description-quality.md`、`report-template.md`、`recommendation-examples.md` 中残留的"五维"与数值分示例
- **flow/*.md 转义修复**：修正反斜杠丢失、单引号代码块、换行符污染
- **仓库名统一**：`SKILL.md` 与 `install.sh` / `install.ps1` 统一使用 `skills-audit-skill`
- **自检清单更新**：`self-audit-issues.json` 记录本轮修复

### P2 - 运行时治理与测试工程化
- **运行时数据目录 `.data/`**：迁移 `stats.json`、`project-profiles.json`、`activity-log.jsonl` 至 `.data/`，避免与源码混排
- **config.yaml 路径更新**：`data_dir` 指向 `.data/`，所有缓存/统计/日志文件路径统一
- **无用文件清理**：删除 `nul`、`.skill-order.json`
- **旧数据格式重置**：`stats.json` / `project-profiles.json` 从数值分制重置为 S/A/B/C/D 格式
- **自动化验证脚本**：新增 `tests/validate.py`，覆盖 YAML 解析、版本同步、权重和、平台合规、flow 格式、数据目录检查
- **扩展测试用例**：新增 `test-weight-sum.md`、`test-yaml-parse.md`、`test-version-sync.md`、`test-platform-yaml.md`
- **SKILL.md 文件结构**：补全 `tests/`、`references/flow/`、`.data/` 说明

---

## [5.8.0] - 2026-06-28

### P0 - 容量分析引擎
- **容量分析引擎**：新增步骤②-bis，分析当前 agent 环境下每个已安装技能/工具的 token 成本
- **灵活上限计算公式**：`(上下文可用空间 - 固定消耗) / 单 skill 平均注入成本`
- **容量报告输出**：步骤⑥新增 `capacity_analysis` 块（JSON 格式），含 agent 类型、固定消耗明细、容量判定（🟢/🟡/🟠/🔴 + 可再装数量）
- **步骤②扩展**：新增容量采集项（SKILL.md 大小/MCP工具数/描述长度/Agent类型）
- **多 Agent 计算模型**：CodeBuddy(16K硬限制) / Claude Code(listingBudget=1%) / Cursor(动态)

### P0 - CI/CD 无交互模式
- **--ci 模式入口**：触发词 `技能审查 --ci` 或 `skills-audit --ci`
- **CI 模式特征**：无交互、JSON 输出、跳过 ④-bis、max_tokens 预算限制（默认 8000）
- **门禁逻辑**：health=🔴→exit_code=1 / actions>5→exit_code=2 / t3_ratio>0.35→exit_code=3
- **CI 输出 schema**：新增 `references/ci-output-schema.md`
- **GitHub Actions 模板**：新增 `references/ci-github-actions.yml`
- **config.yaml 更新**：新增 `ci` 配置块（max_tokens/skip_steps/gates）

### P1 - Novelty + Contamination 7维评分
- **评分从 5维→7维**：新增 Novelty(10%) + Contamination(5%)
- **权重重分配**：Fit 35%→30%, Fresh 15%→17%, Community 20%→18%, 其余不变
- **Novelty 检测**：WebSearch 竞品对比 + skill-registry.yaml 交叉比对（仅 S/A 档执行）
- **Contamination 检测**：正则语言混合检测 + 触发词矩阵一致性校验（本地计算，零 token 成本）
- **CI 降维**：CI 模式自动降为 5 维（跳过 Novelty + Contamination）

### P2 - SkillSpector 集成 + 生态合作
- **安全扫描配置**：`config.yaml` 新增 `security_scan` 块（skillspector/builtin）
- **安全子项融入 Value 维度**：通过→+0.5档 / Critical→D / High→C
- **actions.json 输出**：新增 `references/actions-schema.md`，对接 Skills Manager
- **WorkBuddy 上架准备**：SKILL.md frontmatter 新增 `category: "开发工具"` + `platforms` 字段

### 文件变更汇总
- SKILL.md: v5.7.0→5.8.0，frontmatter +category/platforms，7维评分表，CI模式入口，容量分析引擎，安全子项
- workflow-details.md: 全量同步所有变更，新增 ②-bis 容量分析章节，7维评分详细标准
- config.yaml: 新增 ci 块 + security_scan 块
- report-template.md: 新增容量分析报告块，评分表头更新为7维
- skill-registry.yaml: 版本 5.7.0→5.8.0
- VERSION: 5.7.0→5.8.0
- 新增: references/ci-output-schema.md, references/ci-github-actions.yml, references/actions-schema.md
- CHANGELOG.md: v5.8.0 条目

---

## [5.7.0] - 2026-06-28

### P0 - 阻塞修复
- **P0-1: 并行依赖修复**：②→⑤a 从并行改为串行（⑤a 依赖②输出的技能名列表）
- **P0-1: Community 离线策略**：网络不可用且无缓存时标注「⏸ 信号待获取」，跳过 Community 维度（4维重算权重），禁止使用伪造默认值25
- ⑤a 增加重试机制：最多2次重试，每次10s超时
- **P0-2: Value 维度重建**：从"项目价值(依赖usage)"改为"预期价值(基于画像推断)"，5档基于命中核心活动数+场景频率
- **P0-2: 痛点推导去usage化**：所有依赖 usage 数据的痛点改为基于画像推断（核心活动覆盖/技能分布/零匹配）
- **P0-2: 健康阈值更新**：`low_usage_warn` → `zero_match_warn`（调用次数=0 → 与画像零匹配）
- **P0-3: 版本自动回写**：④-bis 深度阅读时自动从 SKILL.md 提取 version，回写 `skill-registry.yaml`
- **P0-3: skill-registry.yaml 更新**：skills-audit 版本 5.5.0→5.7.0，注释说明自动回写规则

### P1 - 实用性增强
- **P1-1: 30秒摘要块**：报告最前面增加摘要块（健康度/关键操作/预估收益）
- **P1-2: 趋势对比行**：最近3次审计数据趋势行（均分/活跃/冗余变化）
- **P1-3: ROI 5档精化**：从3档（高/正向/净消耗）→5档连续制（S:>+3000t, A:+1000~3000, B:0~1000, C:-500~0, D:<-500），ROI计算基于加载成本+预期节约
- **P1-4: project-types.yaml 扩展**：新增 DevOps-多服务、CI/CD、游戏-Unity、游戏-Unreal、区块链-Hardhat、区块链-Solana、AI/深度学习、AI-LLM部署 共8种项目类型
- **P1-5: 推荐去重合并**：A/B/C三层推荐后按技能名去重，优先保留A层（内置映射更可靠），C层仅补充未命中技能

### P2 - 普适性/自进化增强
- **P2-1: 多平台配置补全**：新增 `platforms/claude.yaml`、`platforms/codex.yaml`、`platforms/cursor.yaml`
- **P2-2: 复合项目类型识别**：检测多个独立类型时生成复合类型+合并推荐列表
- **P2-3: custom_rules 轻量实现**：支持 add_skill/remove_skill/suggest 三种动作，在B层之后执行
- **P2-4: 缓存GC**：步骤⑧持久化时清理不在当前技能列表中的缓存条目
- **P2-5: 离线降级标注**：references 缺失时标注「⚠️ 离线模式」，禁止伪造默认数据
- **P2-6: 评分自进化基础**：⑥-bis 增加评分-决策一致性追踪，累积 ≥5 次偏差后触发权重微调建议
- **P2-7: user-profile 深度映射**：建立高频技能→Value+1档、工作模式→推荐权重、技术兴趣→搜索关键词等8条显式映射
- **P2-8: 审计反馈收集**：⑦执行后增加1-4分反馈问卷，写入 stats.json 用于长期优化
- **P2-9: ④-bis 分级策略**：S/A全量深读、B轻量检查、C/D跳过，token消耗降低 40-60%
- **P2-10: 描述检查位置调整**：从④步骤移至⑥报告阶段，减少不必要消耗
- **P2-11: 评分快照即时持久化**：报告输出前持久化评分快照，用户中断可增量恢复

### 文件变更汇总
- SKILL.md: 版本5.6.0→5.7.0，并行化修正、Value重建、ROI精化、分级策略、反馈收集等
- workflow-details.md: 全量同步所有19项变更
- config.yaml: low_usage_warn→zero_match_warn，custom_rules轻量实现
- project-types.yaml: +8种项目类型（游戏/区块链/DevOps/AI）
- skill-registry.yaml: 版本更新+自动回写规则注释
- report-template.md: +30秒摘要块+趋势对比行
- platforms/: 新增 claude.yaml/codex.yaml/cursor.yaml
- CHANGELOG.md: 完整19项变更记录

---

## [5.6.0] - 2026-06-28

### Added
- **独立词触发机制**：参考 `summarize` 技能，触发词必须独立发送（可带子命令），句中不触发，避免误触发
- **中英双语触发词矩阵**：22个词条（中文12+英文10），覆盖技能审计/项目审计双模式
- **同义字词自动映射**：审查=审计=检查=诊断、能力=技能=工具、环境=项目
- **语言自适应**：根据用户会话主语言（中/英/混合）自动切换翻译方向和报告语言
- **触发词翻译精炼**升级为核心能力：自动翻译+精炼技能触发词和简介，中英双向互译
- **同义字词映射表**：10个英文关键词→中文主词+2-4个同义扩展
- **子命令支持**：`深度`/`推荐`/`画像`/`健康` 四个子命令，按需执行特定步骤
- `platforms/workbuddy.yaml`：WorkBuddy 技能市场平台配置

### Changed
- **SKILL.md 精简**：从852行精简到176行（-79%），执行流程细节外移到 `references/workflow-details.md`
- frontmatter description 双语化：`技能审查·项目审计 → 画像驱动·五维评分·逐技能优化 | Skill Audit·Project Audit → profile·5dim·deep opt`
- `references/description-quality.md` 升级：新增语言自适应规则、同义字词映射表、翻译精炼示例
- `platforms/zcode.yaml`：触发词从5个扩展到22个
- `user-profile.md`：通用模板化，添加注释引导新用户填写
- `README.md`：更新触发章节、v5.6.0 changelog

---

## [5.5.0] - 2026-06-27

### Added
- **S/A/B/C/D 五档评分**：从连续0-100分改为五档定性制，减少agent间评分不一致
- **强制评分理由**：每个技能必须附带1句理由，无理由=未评分
- **前置目录检查**：步骤⓪新增项目根检测，防止非项目目录运行

### Changed
- 评分规则：逐维判定→定性选档→计算综合→映射最终档位

---

## [5.4.0] - 2026-06-26

### Added
- **画像强制持久化**：画像构建完成后必须写入磁盘，不持久化则阻止后续评分
- **报告输出强制检查**（⑥-c）：防止agent跳过报告直接执行
- **操作清单格式规则**：[!N]/[N]/[AUTO]/[SKIP] 四类标记，减少执行模糊性
- **自检缺陷追踪**：持久化阶段写入 `self-audit-issues.json`，下次审计回测修复情况

### Changed
- 执行前确认模板：展示自动/需确认/依赖暂停三类操作

---

## [5.3.0] - 2026-06-25

### Added
- **MCP跨层扫描**：步骤②新增第二阶段，扫描MCP服务器和工具列表
- **技能-MCP跨层重叠检测**：互补关系判定（方法型+执行型→✅互补）
- `mcp_config` 配置项

### Changed
- 能力来源从"技能"扩展到"技能+MCP"

---

## [5.2.0] - 2026-06-24

### Added
- **五维评分**：Fit/Value/Fresh/Community/ROI，从三维扩展到五维
- **置信推荐**：信心指数(0-10) + ROI + 证据链
- **不推荐清单**：5种数据驱动判定规则
- **并行编排**：6阶段化并行，减少35-40% tool call轮次
- **条件报告**：按需输出，无内容不兜底
- **审计验证**（⑥-bis）：数据一致性检查 + 抽样交叉验证
- When to Use / When NOT to Use 章节

### Changed
- 报告模板外移至 `references/report-template.md`
- 深度分析模板外移至 `references/deep-analysis-template.md`
- 推荐示例外移至 `references/recommendation-examples.md`
- 描述规则外移至 `references/description-quality.md`

---

## [5.0.0] - 2026-06-23

### Added
- **④-bis 逐技能深度阅读与分析**：不读技能正文的审计=盲评
- 六维分析框架：作用·适配·缺口·建议·维护·参考
- 外部参考验证（agent-reach/web_fetch ≥2来源）
- 自指校验

---

## [4.3.0] - 2026-06-22

### Added
- Community回填机制
- Value维度重构
- undo/回滚机制
- 外部信号增量缓存（GitHub⭐缓存7天，npm📥缓存30天）

---

## [4.2.0] - 2026-06-21

### Added
- 触发词优化
- `output_language` 三态（auto/zh/en）
- 自检锚点

---

## [4.0.0] - 2026-06-19

### Added
- 项目角色画像驱动
- 五维评分体系（初版）
- 15+ 项目类型支持
- 三级分层（T1/T2/T3）
- 描述质量检查
- 三层推荐引擎

---

## [3.0.0] - 2026-06-17

### Added
- 项目记忆驱动
- 双模式（技能审计/项目审计）
- 持久化机制

---

## [1.0.0] - 2026-06-15

### Added
- Initial release
- 基础技能扫描
- 简易评分
- 内置推荐映射
