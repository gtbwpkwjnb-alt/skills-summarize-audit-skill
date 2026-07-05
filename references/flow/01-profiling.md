# ① 项目画像

只扫描当前工作目录。提取：目录信息→关键文件→文件特征→构建多维画像（类型/用途/活动/技术栈/兴趣/痛点/入口）。

**痛点必须来自数据源，禁止猜测**。画像强制持久化到 {project}/.agents/project-profile.md，设置 persisted=true。

**画像过期检查**（v5.9.1）：如果 .data/project-profiles.json 最后更新超过 auto_refresh_days 天，自动触发重新画像。

---
## 下一步

→ [② 技能清单](02-inventory.md)
