# Report Template — Skills-Summarize-Audit v8.2.2

事实状态（observed/inferred/estimated/unavailable）遵循 `references/output-contract.md`。

只输出本次请求涉及的区块。报告采用“先结论、后行动、再证据”的阅读顺序：每个结论标注 `observed`、`inferred`、`estimated` 或 `unavailable`；默认只读。不要用全量技能表、逐项健康分或 `info` 提示占据首屏。

```text
# 技能/插件审查

状态: complete | partial
范围: <installed / visible> | 写入: 本轮只读，未修改文件
证据覆盖: observed <n> / inferred <n> / estimated <n> / unavailable <n>

## 一眼结论
扫描 <n> 项；需处理 <n> 项（critical <n> / warning <n>）。
决策: <可直接保留 / 先处理阻断项 / 证据不足，暂不变更>。

## 安装全景
| 来源组/外挂 | 项数 | 低适用项 | 上下文压力 | 建议 |
| --- | ---: | ---: | --- | --- |
| system / global / runtime / <plugin-name> | <n> | <n> | 高/中/低 [inferred] | 保留 / 按任务保留 / [需确认] 评估禁用或卸载 |

来源组说明：`system` 是内置技能，`global` 是用户全局技能，`runtime` 是运行时发现项，插件名为外挂。缓存或 manifest 项不等于当前 UI 可见项。

## 评分与证据边界
| 维度 | 解释 | 状态 |
| --- | --- | --- |
| 健康分 | 来源、元数据和版本可解析性；不代表常用或适用。 | observed/unavailable |
| 适用度 | 用户画像词命中；高/中/低。 | observed/unavailable |
| 使用频率 | 只接受可归因的 session/tool-call 事件。 | observed/unavailable |
| 上下文压力 | 按安装项数量推断发现/选择噪声，不等同于实际 prompt token。 | inferred |

## 需处理
### [CRITICAL|WARNING] <技能/插件> - <问题代码>
问题: <一条可理解的故障描述>
影响: <对当前使用、发布或可信度的实际影响> [observed/inferred]
证据: <绝对路径 / 命令 / 已获同意的 URL>
建议: <只读建议，或标记 [需确认] 的最小后续动作>

无 critical/warning 时明确写“无”；不以 `info` 凑数量。

## 边界与协同
| 对象 | 判断 | 依据 | 建议 |
| <技能 A + 技能 B> | conflict / complementary | <重叠分与理由> | <明确边界 / 共存分工> |

仅列 `conflict` 和 `complementary`；不输出 `unrelated` 的成对组合。

## 优化与卸载候选
| 对象 | 来源组 | 健康 | 适用度 | 使用频率 | 建议 |
| --- | --- | ---: | --- | --- | --- |
| <id> | <system/global/runtime/plugin> | <0-10> | 高/中/低/unavailable | observed/unavailable | 先维修 / [需确认] 评估禁用或卸载 |

没有使用频率或完整 UI 可见证据时，不输出“应卸载”；只能输出 `[需确认] 评估禁用或卸载`。

## 按请求展开
### 中文翻译候选
可见性证据: <截图 / ID 列表 / 已验收导出；缺失为 unavailable>
| 标识 | 原文 -> 中文候选 | 来源 | 质量 | 可编辑性 |
| <id> | <原文> -> <候选> | <绝对路径> | ready/needs_agent_refinement | true/false |

### 项目画像
| 观察到的事实 | 对当前工作的影响 | 证据 | 状态 |
| <技术栈/依赖/规则> | <影响> | <path> | observed/inferred/unavailable |

### 推荐
| 决策 | 解决的具体缺口 | 证据与风险 | 状态 |
| 保留/观察/考虑引入/不建议 | <工作> | <本地依据或已同意联网证据> | observed/inferred/unavailable |

### 生态综合评估（v9.0.0 新增）

**MCP 健康表**
| MCP 服务器 | 健康分 | 等级 | 调用次数 | 关键问题 | 建议 |
| --- | ---: | :---: | ---: | --- | --- |
| <name> | <0-10> | 🟢/🟡/🟠/🔴 | <n> [observed] | <启动/配置/权限/未调用> | 保留/隐藏/[需确认] 卸载 |

**Agent 调用歧义表**
| Agent A | Agent B | Overlap | 调用频次差 | 风险 | 建议 |
| --- | --- | ---: | ---: | :---: | --- |
| <profile_a> | <profile_b> | <0-1> | <0-1> | 🔴/🟡/🟢 | 合并/边界澄清/归档/无干预 |

仅列 `critical` 和 `warning` 风险对，不输出 `ok`。

**上下文压力评估**
| 来源 | 工具数 | 注入 token | 占比 | 等级 |
| --- | ---: | ---: | ---: | :---: |
| Skills | <n> | <n> | <%> | 🟢/🟡/🟠/🔴 [estimated] |
| MCP schemas | <n> | <n> | <%> | |
| Agent profiles | <n> | <n> | <%> | |
| **合计** | <n> | <n> | <%> | |

**精简候选**（按 prune_value 排序）
| 对象 | 类型 | token | 使用次数 | 画像匹配 | 精简值 | 建议 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| <id> | skill/mcp/agent | <n> | <n> | <0-10> | <0-1> | hide/uninstall/[需确认] |

**配置优化总览**
| 层级 | 数量 | 说明 |
| --- | ---: | --- |
| 保留（value≥7） | <n> | 高频高匹配，当前配置合理 |
| 观察（4≤value<7） | <n> | 暂时保留，30 天复查 |
| 隐藏（2≤value<4） | <n> | 从命令栏隐藏但保留文件 |
| 卸载候选（value<2） | <n> | [需确认] 评估卸载 |

数据来源标注：`observed`（transcript/skills 目录）/ `inferred`（算法推导）/ `estimated`（公式估算）/ `market_observed`（联网查询）/ `unavailable`（无数据）。

## 未获取数据
- <例如：结构化使用证据、外部版本新鲜度、完整 UI 可见清单>；说明它为何为 `unavailable`，不使用默认值补齐。

## 下一步
| 优先级 | 建议直接调用 | 用户应提供的输入 |
| P0/P1/P2 | <对应 Agent/技能类型> | <目标、范围、确认条件> |

## 附录
- 已折叠 <n> 条 `info`；仅在用户说“深度”或要求完整清单时展开。
- `--json` 保持完整机器可读证据；常规对话不粘贴原始 JSON。
- `--detail` 输出逐项安装表，包含健康、适用度、使用频率和建议。
```

“下一步”不包含执行命令，也不将后续工作吸收进 Audit。
