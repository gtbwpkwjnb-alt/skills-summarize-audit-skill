# 测试：7 维权重和

> 验证 `references/flow/04-scoring.md` 中 7 维权重之和为 100%。

## 输入

读取 `references/flow/04-scoring.md` 权重表与公式。

## 预期输出

```text
Fit 30% + Value 20% + Fresh 15% + Community 15% + ROI 10% + Novelty 7% + Contamination 3% = 100%
```

## 验证标准

- 权重表中 7 个百分比相加等于 100%。
- 公式中 7 个小数系数相加等于 1.0。
- 若和不等于 100%，则 S/A/B/C/D 阈值失效。

## 执行方式

```bash
python tests/validate.py
# 或手动检查：grep 公式行中的 0.xx 并求和
```
