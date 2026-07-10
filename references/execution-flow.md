# 执行流程（索引）

> 各阶段详细步骤已拆分为独立文件。引用方式：references/flow/XX-name.md
> v5.8.0 合并为单文件 | v5.9.1 拆分为多文件

## 流程图

⓪ → (①+③) → ②(含能力映射) → ②-bis → **②-ter** → ⑤a → ④(含质量信号) → ⑤-aa → ⑤-ab GitHub横向对比 → (④-a + ④-bis + ⑤b) → ⑤c作用域决策 → ⑥(含生态雷达) → ⑥-bis → ⑥-c → ⑦-b确认→⑦-a快照→⑦-c执行 → ⑧

## 阶段文件

| 阶段 | 文件 | 说明 |
|:----|:----|:-----|
| ⓪ | flow/00-config.md | 配置+记忆+模式检测 |
| ① | flow/01-profiling.md | 项目画像 |
| ② | flow/02-inventory.md | 技能清单+容量采集 |
| ②-bis | flow/02-bis-capacity.md | 多因子有效容量分析 |
| ②-ter | flow/02-ter-liveness.md | 7项活性检测（含 MCP 启动验证） |
| ③ | flow/03-reference.md | 参考数据加载 |
| ④ | flow/04-scoring.md | 三级分层+八维评分 |
| ④-a | flow/04-a-t3-validation.md | T3 活性验证 |
| ④-bis | flow/04-bis-deepread.md | 逐技能深度阅读 |
| ⑤a | flow/05-signals.md | 外部信号获取 |
| ⑤-aa | flow/05-aa-community-feed.md | **社区 Feed — 能力缺口搜索（v6.0.0）** |
| ⑤-ab | flow/05-ab-github-comparison.md | GitHub 同类候选横向比较与证据门槛 |
| ⑤b | flow/05-rec-engine.md | 三层推荐引擎 |
| ⑤c | flow/05-c-scope-decision.md | 项目级/全局级/插件级作用域决策 |
| ⑥ | flow/06-report.md | 报告生成(含趋势对比) |
| ⑥-bis | flow/06-bis-verify.md | 审计验证+self-audit |
| ⑥-c | flow/06-c-output-check.md | 报告输出检查 |
| ⑦-a | flow/07-a-snapshot.md | 快照备份 |
| ⑦-b | flow/07-b-confirm.md | 用户确认 |
| ⑦-c | flow/07-c-execute.md | 执行操作 |
| ⑦-d | flow/07-d-rollback.md | 回滚操作 |
| ⑧ | flow/08-persist.md | 持久化+GC |

## 参考数据

- project-types.yaml — 项目类型映射
- skill-registry.yaml — 技能注册表
- report-template.md — 报告模板
- deep-analysis-template.md — 深度阅读模板
- description-quality.md — 描述质量检查规则
- ci-output-schema.md — CI JSON 输出格式
- ci-github-actions.yml — CI 工作流模板
- actions-schema.md — Skills Manager 对接格式
- recommendation-examples.md — 推荐示例
- capability-dimensions.yaml — **能力维度定义与工具映射（v6.0.0）**
- release-checklist.md — 发布前静态门禁与人工确认项
