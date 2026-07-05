# ⑧ 持久化

画像双写 · 统计 · 日志 · 缓存 · 快照 · 自检缺陷追踪。

**缓存GC**：清理 .data/external-signals-cache.json 中不在当前技能列表的条目。
**快照GC**：清理超过 retention_days 的旧快照。
**画像刷新**（v5.9.1）：.data/project-profiles.json 超过 auto_refresh_days → 自动重新画像。

失败不阻塞主流程。

---
## 下一步

✅ 流程结束。返回 [索引](../execution-flow.md)

