# MCP 健康度评估 Checklist v1.0

> v9.0.0 新增。服务能力四「生态综合评估」的 4.1 子能力。
> 把 `health-checklist.md` 的 8 维评分泛化到 MCP server，覆盖 MCP 特有的启动/配置/权限维度。

## 一、为什么 MCP 需要独立的健康维度

MCP server 与 Skill 的本质差异：
- Skill 是**静态文件**，存在即生效
- MCP server 是**进程**，需要启动、保持运行、暴露 tool schema
- MCP 有**权限边界**（API Key、OAuth、文件系统访问）
- MCP 的 tool 通过 `mcp__<server>__<tool>` 命名空间注入到 LLM context

因此 MCP 健康度不能简单复用 skill 的 8 维，需要独立的 6 维框架。

## 二、MCP 六维健康评估

| # | 维度 | 检测方法 | 数据来源 | 健康阈值 | 不健康处置 |
|:-:|---|---|---|---|---|
| 1 | **启动可达性** | 配置中的 command/args 能否启动 stdio/sse server | `config.json` + 实际启动测试 | command 字段存在 = pass（基础检查）；真实启动测试通过 = strong_pass；字段缺失 = fail | 标 `unreachable` |
| 2 | **配置完整性** | 必需字段齐全（command, args, env, type） | `config.json` mcpServers 字段 | 全字段齐 | 标 `incomplete_config` |
| 3 | **权限边界** | API Key/Token 是否暴露、是否使用 HTTPS、env 是否含敏感字段 | `config.json` env + url 字段 | 无明文 token/HTTPS | 标 `risky_exposure` |
| 4 | **Tool Schema 健康** | tool 数量、schema 复杂度是否合理 | 实际 list_tools 调用或缓存的 `mcp/*.json` | tool_count 1-50 | 标 `schema_bloat` 或 `empty` |
| 5 | **实际调用证据** | 最近 N 天存在可归因的 `mcp__<server>__*` tool_call | `extract_usage_signals.py` 的 mcp_usage_evidence | ≥1 次/30 天 | 标 `dormant` |
| 6 | **跨客户端一致** | 同名 MCP 在多客户端配置一致（command/version） | 扫描 `.claude.json`/`.zcode`/`.codex` 等 | 一致 | 标 `drift` |

## 三、综合健康分计算（0-10）

```
mcp_health = (
    dimension_1 * 0.25 +   # 启动可达性权重最高（当前为「配置层可达性」，非进程层）
    dimension_2 * 0.15 +   # 配置完整性
    dimension_3 * 0.20 +   # 权限边界（安全问题影响大）
    dimension_4 * 0.10 +   # Schema 健康
    dimension_5 * 0.20 +   # 实际调用（功能价值证据）
    dimension_6 * 0.10     # 跨客户端一致
)
```

每维取值：
- `pass` = 10
- `warn` = 5
- `fail` = 0
- `unavailable`（无数据）= 不计入分母

## 四、健康等级

| 分数 | 等级 | 标识 | 含义 |
|---|---|---|---|
| ≥ 8.0 | 🟢 优秀 | `healthy` | 配置完整、启动正常、有调用证据 |
| 6.0-7.9 | 🟡 良好 | `ok` | 多数维度通过，个别 warn |
| 4.0-5.9 | 🟠 待改进 | `needs_attention` | 多维 warn 或有 fail |
| < 4.0 | 🔴 危险 | `unhealthy` | 启动失败或安全风险 |

## 五、检测脚本规则（伪代码）

### 检测 1：启动可达性

**当前实现（v9.0.0）**：脚本仅检查 command 字段存在。真实 spawn 测试由用户的 Agent 手动执行（参考 lifecycle-guidance.md 的模板）。

```python
def check_mcp_startup(server_name: str, config: dict) -> dict:
    """启动测试：发送 initialize 请求，3s 内返回为 pass。
    
    注意：v9.0.0 的脚本仅检查 command 字段是否存在，
    并非真正启动进程。真实子进程启动由用户的 Agent 执行。
    """
    cmd = config.get("command")
    args = config.get("args", [])
    if not cmd:
        return {"status": "fail", "reason": "missing command"}
    # 实际执行（当前未实现）：启动子进程，发送 initialize JSON-RPC，等待响应
    # 详见 scripts/audit_skill_plugin_issues.py 的 ecosystem 分支
    return {"status": "pass"} | {"status": "fail", "reason": "..."}
```

### 检测 3：权限边界（联动 security-rules.yaml）

⚠️ **区分标准配置与真风险**：

| 场景 | 判定 | 原因 |
|---|---|---|
| 明文 API Key 存于本地 `config.json`，文件权限合理，未出现在日志/UI/外部读取路径 | **pass（标准配置）** | MCP 官方推荐方式：`config.json` 是本地配置文件，不属于暴露 |
| 明文出现在版本控制（`git` 仓库内）、日志文件、环境变量继承到子进程、URL 参数中 | **warn / fail（真风险）** | 凭证被持久化到可共享或可泄露的路径 |

```python
def check_mcp_permissions(server_name: str, config: dict) -> dict:
    """检查 env 中是否有明文敏感字段。
    
    区分标准配置（本地 config.json，pass）与真风险（git 跟踪/日志泄露/warn）。
    """
    env = config.get("env", {})
    sensitive_patterns = [
        r"(?i)(token|key|secret|password|api[_-]?key)",
    ]
    exposed = []
    for k, v in env.items():
        if re.search(sensitive_patterns[0], k) and v and not v.startswith("${"):
            # 明文 token：需要进一步判断是真风险还是标准配置
            is_in_git_repo = os.path.isdir(os.path.join(os.path.dirname(config.get("_source_path", "")), ".git"))
            is_in_log_path = any(log_dir in config.get("_source_path", "") for log_dir in ["logs", "log", "transcript"])
            
            if is_in_git_repo:
                risk_level = "warn"  # 被版本控制跟踪
            elif is_in_log_path:
                risk_level = "warn"  # 出现在日志路径
            else:
                risk_level = "pass"  # 标准本地配置，标记但不告警
                
            exposed.append({
                "field": k, 
                "value_prefix": v[:8] + "...",
                "risk_level": risk_level,
                "risk_reason": "标准配置（本地 config.json）" if risk_level == "pass" 
                              else "版本控制跟踪" if is_in_git_repo
                              else "日志路径泄露"
            })
    
    url = config.get("url", "")
    is_https = url.startswith("https://") if url else True
    
    # 仅真风险项触发 warn
    real_risks = [e for e in exposed if e["risk_level"] == "warn"]
    if real_risks or not is_https:
        return {"status": "warn", "exposed_fields": real_risks, "https": is_https,
                "note": "仅标记真风险项；标准配置项（本地 config.json）列于 info 字段"}
    if exposed:
        return {"status": "pass", "info": "含标准配置明文，但未出现于 git/日志路径，属安全范围"}
    return {"status": "pass"}
```

### 检测 5：实际调用证据

```python
def check_mcp_usage_evidence(server_name: str, signals: dict) -> dict:
    """从 extract_usage_signals.py 输出中查找调用次数。"""
    for m in signals.get("mcp_usage_evidence", []):
        if m["mcp_server"] == server_name:
            if m["status"] == "configured_never_observed":
                return {"status": "fail", "calls": 0, "reason": "configured but never called"}
            if m["tool_calls"] >= 1:
                return {"status": "pass", "calls": m["tool_calls"]}
    return {"status": "unavailable", "reason": "no signals data"}
```

## 六、输出格式

```json
{
  "mcp_health_assessment": [
    {
      "server": "firecrawl",
      "health_score": 9.2,
      "grade": "healthy",
      "dimensions": {
        "startup": {"status": "pass"},
        "config": {"status": "pass"},
        "permissions": {"status": "pass", "info": "标准配置（本地 config.json，未纳入 git），通过", "note": "FIRECRAWL_API_KEY 明文存于本地 config.json 为 MCP 标准配置方式"},
        "schema": {"status": "pass", "tool_count": 18},
        "usage": {"status": "pass", "calls": 17, "last_used": "2026-07-25"},
        "consistency": {"status": "pass"}
      },
      "data_source": {
        "config_path": "C:/Users/Administrator/.zcode/cli/config.json",
        "signals_source": "extract_usage_signals.py"
      }
    }
  ]
}
```

## 七、与 v8 health-checklist 的关系

- `health-checklist.md` 的 8 维继续服务 skill
- 本文件的 6 维服务 MCP server
- 二者在报告「评分与证据边界」中分开展示，不混用维度

## 八、维护

- 新增 MCP 类型（如 SSE、WebSocket、HTTP）时扩展检测 1 的启动逻辑
- 新增敏感字段模式时更新检测 3 的正则
- 与 `mcp-marketplaces.md` 的六维市场评估互补：本文件评**已安装**，marketplaces 评**候选**
