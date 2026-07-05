# ⑦-a 快照备份（v5.9.1）

执行前自动备份所有 editable=true 技能：

1. 读取 config.yaml snapshot.dir（默认 ~/.agents/skills/.audit-snapshots/）
2. 创建 {dir}/{timestamp}/（YYYYMMDDTHHMMSS）
3. 复制每个 editable=true 技能完整目录
4. 生成 manifest.json（timestamp, skill_list, file_count, total_size）
5. 输出：📸 快照已创建 (N 个技能) — '技能审查 --undo {id}' 恢复

保留 retention_days 天，超期自动 GC。

---
## 下一步

→ [⑦-b 用户确认](07-b-confirm.md)