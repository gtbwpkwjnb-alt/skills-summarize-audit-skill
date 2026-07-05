# ⑦-c 执行

仅用户层技能（editable=true）可修改。系统技能只读。操作：归档、修改描述、安装、更新、回滚。
执行日志写入 {snapshot.dir}/{timestamp}/execution-log.json。

**审计反馈收集**：
```text
📊 本次审计效果如何？
  [1] 有帮助 [2] 部分有用 [3] 帮助不大 [4] 跳过
```
反馈写入 .data/stats.json user_feedback。

---
## 下一步

→ [⑦-d 回滚操作](07-d-rollback.md)
→ [⑧ 持久化](08-persist.md)

