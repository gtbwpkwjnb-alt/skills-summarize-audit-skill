# Report Template — Skills-Summarize-Audit v6.4.0

报告必须遵循 `output-contract.md`。尖括号字段由本次扫描替换；没有证据时保留 `unavailable`，不得使用示例值补齐。

```text
审计状态: complete | partial
写入状态: 本轮只读，未修改文件
证据覆盖: observed <N> / inferred <N> / estimated <N> / unavailable <N>

⚡ 摘要
- 健康度: <状态> | 依据: <评分覆盖或阈值> | 限制: <缺失维度>
- 关键发现: <observed/inferred> <结论> | 证据: <路径/命令/记录时间>
- 容量: <estimated/unavailable> <结果> | 公式/限制: <说明>
- 趋势: <observed/unavailable> <结果> | 依据: <已确认保存的历史快照>

📋 项目画像
| 字段 | 值 | 状态 | 证据 |
| 类型 | <值> | observed/inferred | <文件或规则> |
| 活动 | <值> | observed/inferred | <文件或规则> |
| 痛点 | <值或 unavailable> | observed/inferred/unavailable | <证据或限制> |

📊 技能评分
| 技能 | 综合 | 有效权重 | 维度状态 | 理由与证据 | 建议 |
| <name> | <S/A/B/C/D 或 unavailable> | <0-100%> | <observed/inferred/...> | <一句理由+来源> | 保留/评估中 |

🧪 活性检查
| 技能 | 配置/命令/MCP | 使用证据 | 活性状态 | 限制 |
| <name> | PASS/FAIL/N/A | observed/unavailable | <状态> | 配置可达不等于实际有效 |

🌐 外部与质量信号
- Community: <observed/unavailable>；外部搜索未获同意时不参与综合分。
- Quality ledger: <observed/unavailable>；缺失时不回填默认分数。
- Registry: <observed> <本地对齐状态>；不等同于最新版本。

📦 [需确认] 操作建议
| 操作 | 作用域/目标路径 | 证据 | 风险与回滚 | 状态 |
| <archive/install/update/description> | <project/global/plugin/defer> | <URL/文件> | <快照或限制> | [需确认] |

未获取数据
- <数据项>: <原因>；影响: <不评分/不推荐/不输出趋势>
```

只有用户确认具体操作后，才能创建快照、写入画像/缓存/日志或修改目标文件。
