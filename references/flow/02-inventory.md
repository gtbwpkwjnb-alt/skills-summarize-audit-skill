# ② 已安装技能清单（含容量采集）

使用已加载 config.yaml 中所有 scan_paths，提取每个技能的 name/description/路径/来源/版本号。
同时扫描 MCP 服务器（mcp_config.files），提取服务器+工具列表。去重：同name优先 editable=true→版本高者。

**容量采集**（同时执行，不额外增加轮次）：

| 采集项 | 采集方式 | 用途 |
|:---|:---|:---|
| SKILL.md 文件大小 | Read → 字节数 / 4 ≈ token 估算 | 计算注入成本 |
| MCP 工具数量 | 解析 mcp_config 配置 | 计算工具池 token 成本 |
| MCP 工具描述长度 | 读取每个工具的 description | 计算 tool listing 成本 |
| Agent 类型 | 从平台特征判定 | 选择计算模型 |

**CI 降级**（v5.9.1）：CI 模式下 token 预算不够时，跳过 MCP 工具扫描以节省 30-50% 开销。

---
## 下一步

→ [②-bis 容量分析](02-bis-capacity.md)
