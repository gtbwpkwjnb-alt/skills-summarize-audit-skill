# 测试：版本号同步

> 验证所有版本源统一为同一版本号，避免安装/运行时显示不一致。

## 输入

读取以下文件的首个版本号：

- `VERSION`
- `SKILL.md` frontmatter
- `README.md` 标题/徽章/changelog
- `CHANGELOG.md` 首个条目
- `references/skill-registry.yaml` 中 `skills-audit` 条目

## 预期输出

所有来源版本号一致，例如 `5.9.1`。

## 验证标准

| 来源 | 当前版本 |
|:-----|:---------|
| VERSION | 5.9.1 |
| SKILL.md | 5.9.1 |
| README.md | 5.9.1 |
| CHANGELOG.md | 5.9.1 |
| skill-registry.yaml | 5.9.1 |

若任一来源不一致，验证失败。

## 执行方式

```bash
python tests/validate.py
```
