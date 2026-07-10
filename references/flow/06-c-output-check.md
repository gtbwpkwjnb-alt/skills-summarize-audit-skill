# ⑥-c 报告输出强制检查

确认报告已输出、评分表已生成，并满足 `references/output-contract.md`：

1. 每个健康度、收益、容量、趋势和推荐结论都有事实状态与证据或限制。
2. `unavailable` 数据已列出，未被默认分数或样例数字替代。
3. 操作全部标为 `[需确认]`，报告中声明本轮未写入文件。
4. `report_status` 只能为 `complete` 或 `partial`；不得使用无证据的 `verified=true`。

任一检查失败，报告标记 `partial` 并阻止进入⑦执行阶段。

---
## 下一步

→ [⑦-a 快照备份](07-a-snapshot.md)
