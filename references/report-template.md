# Report Template — Skills-Summarize-Audit v7.0.0

只输出本次请求涉及的区块。每个结论标注 `observed`、`inferred` 或 `unavailable`；本轮默认只读。

```text
审查状态: complete | partial
写入状态: 本轮只读，未修改文件

🎯 当前用户作用
| 发现 | 对当前工作的影响 | 证据 | 状态 |
| <发现> | <作用或限制> | <绝对路径/命令/已获同意的 URL> | observed/inferred/unavailable |

📋 中文翻译候选（仅请求翻译精炼时）
| 标识 | 命令栏/侧边栏原文 | 中文候选 | 绝对来源 | 质量 | 可编辑性 |
| <id> | <原文> | <候选> | <path> | ready/needs_agent_refinement | true/false |

🧭 项目画像（仅请求项目画像时）
| 项目事实 | 当前工作流或约束 | 证据 | 状态 |
| <技术栈/依赖/规则> | <影响> | <path> | observed/inferred/unavailable |

💡 推荐（仅请求推荐时）
| 结论 | 解决的具体缺口 | 证据与风险 | 状态 |
| 保留/观察/考虑引入/不建议 | <工作> | <本地依据或已同意联网证据> | observed/inferred/unavailable |

➡️ 下一步建议
| 需要的后续工作 | 建议直接调用 | 用户应提供的输入 |
| <例如发布、安装、配置、迁移或清理> | <对应 Agent/技能类型> | <目标、范围、确认条件> |
```

“下一步建议”不包含执行命令，也不将后续工作吸收进 Audit。
