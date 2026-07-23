# 用户画像（Skills-Summarize-Audit）

> 关联: L0=~/.agents/AGENTS.md（全局底线）｜L2=各项目 memories/MEMORY.md（事实库）｜项目画像=各项目 .agents/project-profile.md
> 本文件只保留跨项目、可复查的稳定偏好。技能使用次数必须来自可归因的结构化 Codex session/tool-call 事件；当前提取器未实现时标记 `unavailable`，不得沿用旧 error-ledger 统计。

## 基本信息

- **主要工作**：AI Agent/Codex 技能与配置治理、知识资产加工、Web/桌面原型开发
- **常用环境**：Codex、Windows、PowerShell；ZCode/Claude 作为历史兼容环境
- **偏好语言**：中文

## 技能使用特征

- **结构化技能调用次数**：`unavailable`（当前无可执行的 session/tool-call 使用统计提取器）
- **高频工作流**：Codex 配置/skill/MCP/plugin 治理；多源调研与 GitHub 核验；视频/网页转 Markdown；项目实现、回测与安全审查
- **工作模式**：先定边界与验收，再最小执行、独立复核和回测
- **偏好**：中文界面、证据优先、明确推断边界、低噪声触发词与可回滚变更

## 领域兴趣

- **技术兴趣**：AI Agent、Codex、MCP、Python/TypeScript/Rust、知识图谱、记忆与自进化系统
- **非技术兴趣**：写作、玄学（八字/紫微/奇门）、投资研究、游戏开发

## 证据状态

- **当前事实源**：结构化 Codex sessions、实际项目 manifest、当前 loaded config 与运行时回测
- **历史辅助源**：MEMORY.md 与 rollout summaries；使用前需按漂移风险回查
- **禁用统计源**：旧版 summarize `harvests/`、`error-ledger.md` 和仅出现在 prompt/catalog 的技能名称
