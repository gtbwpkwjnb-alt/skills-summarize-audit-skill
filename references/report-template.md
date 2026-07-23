# Report Template — Skills-Summarize-Audit v8.1.0

只输出本次请求涉及的区块。每个结论标注 `observed`、`inferred` 或 `unavailable`；本轮默认只读。

```text
审查状态: complete | partial
写入状态: 本轮只读，未修改文件

🎯 当前用户作用
| 发现 | 对当前工作的影响 | 证据 | 状态 |
| <发现> | <作用或限制> | <绝对路径/命令/已获同意的 URL> | observed/inferred/unavailable |

🧪 技能/插件问题审查（请求问题审查或全量技能审查时）
扫描范围：<installed / visible> · 已安装技能/插件：<n> · 证据状态：<observed/inferred/unavailable>
| 技能/插件 | 版本状态 | 健康分 | 画像匹配 | 问题代码/严重度 | 证据 | 处理方案 |
| <id> | <observed/unavailable> | <0-10> | <score/unavailable> | <code / severity> | <path/命令> | <只读建议或需确认动作> |

🔀 冲突与互补
| 技能 A | 技能 B | 关系 | 重叠分 | 判断理由 | 建议 |
| <id> | <id> | conflict / complementary | <0-1> | <证据> | <边界限定/共存/冲突处理> |

📋 中文翻译候选（仅请求翻译精炼时）
可见性证据：<用户截图/用户提供 ID 列表/已验收导出；缺失则 unavailable>
| 标识 | 展示位置 | 命令栏/侧边栏原文 | 中文触发词与简介 | 绝对来源 | 质量 | 可编辑性 |
| <id> | 侧栏/命令栏/两者 | <原文> | <候选> | <path> | ready/needs_agent_refinement | true/false |

未显示项不列入本区块。可见性证据不完整时，将审查状态标为 `partial` 并说明需要补充的截图或 ID。

✅ 完整性回测（应用候选后）
| 可见项期望数 | 实际回读数 | 英文遗留项 | 客户端验收 | 状态 |
| <n> | <n> | <id 列表或无> | 刷新后的两页截图 / unavailable | complete/partial |

🧹 命令栏精简提示（仅在中文化完成后）
| 分类 | 可见技能 | 建议 | 用户决定 |
| 常用 / 偶尔 / 建议隐藏 | <仅当前可见项> | 保留 / 可隐藏 | 待询问 / 已确认 |

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
