# ④ 三级分层+七维评分（质量信号联动）

**分层**：T1核心→保留 · T2通用→保留 · T3专业→建议归档

**质量信号读取**（v6.0.0 — 联动 summarize 错误账本）：

在评分前，读取 `config.yaml quality_signals.error_ledger` 指向的 error-ledger.md，提取 `TOOL:{工具名}` 格式的错误记录。

```
解析规则:
  1. 扫描 error-ledger.md 表格中"涉实体"列含 TOOL: 的行
  2. 提取: 工具名, 错误次数, days_clean, 状态
  3. 转换为质量评分(0-10):
     - 错误次数 ≥3 且 days_clean=0 → 4/10 (危险)
     - 错误次数 ≥1 且 days_clean=0 → 5/10 (需关注)
     - 错误次数 ≥1 且 days_clean≥1 → 6/10 (有历史问题)
     - 无错误记录 → 9/10 (正常)
     - 不在账本中 → 8/10 (默认)
  4. 质量评分 < quality_threshold(默认6.0) → 标记为 P1 缺口
```

质量评分影响：
- 评分时，质量过低的工具在 Fit 维度扣 1 档
- 推荐时，P1 缺口自动触发搜索替代品（Phase 3）

**七维评分（S/A/B/C/D + 强制理由）**：

| 维度 | 权重 | 标准概要 |
|:---|:---:|:---|
| Fit 项目匹配 | 30% | 命中≥2核心活动=S |
| Value 预期价值 | 20% | 命中核心活动+高频=S |
| Fresh 版本时效 | 15% | 版本≥registry=S |
| Community 外部信号 | 15% | ⭐≥100/近1月更新=S |
| ROI 成本效益 | 10% | >+3000t/run=S |
| Novelty 新颖性 | 7% | 独特无替代=S |
| Contamination 污染 | 3% | 纯目标语言=S |

综合 = Fit×0.30 + Value×0.20 + Fresh×0.15 + Community×0.15 + ROI×0.10 + Novelty×0.07 + Contamination×0.03
≥4.0→S · ≥3.0→A · ≥2.0→B · ≥1.5→C · <1.5→D

**安全子项**（融入 Value）：SkillSpector 扫描通过 +0.5档，Critical→D，High→C。

---
## 下一步

→ [④-a T3 验证](04-a-t3-validation.md)
→ [④-bis 深度阅读](04-bis-deepread.md)