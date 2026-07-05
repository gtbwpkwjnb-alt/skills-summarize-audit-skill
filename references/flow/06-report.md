# ⑥ 生成报告

**评分快照即时持久化**：报告输出前立即持久化评分快照到 .data/stats.json。

**30秒摘要块**（始终最先输出，v5.9.1 趋势行）：
```text
🟢 健康度: 良好 (均档 A ↑ +1档 · T3 17% ↓ -2%)
📌 操作: 归档 3 · 安装 2
💰 收益: ~3,200 tokens/轮
📈 趋势: 活性 +5% · T3 -2% · 容量 → 🟢
```

**容量报告块**：agent 类型、固定消耗、token 成本表、容量判定。

**评分表趋势列**（v5.9.1）：每个技能旁显示 ↑/↓/→ 评分变化。

**CI 模式**：JSON 输出，含 summary/skills/recommendations/alerts/capacity_analysis/exit_code/token_usage。

**描述质量检查**：语言自适应→格式检查→精炼→翻译→双语拼接。审计后自检 skills-audit 自身。

---
## 下一步

→ [⑥-bis 审计验证](06-bis-verify.md)

