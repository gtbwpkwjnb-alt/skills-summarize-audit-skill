# 生命周期指导模板 v1.0 — Lifecycle Guidance

> 大脑加强的核心：本技能不动手，但教用户"如何让 agent 高质量地动手"。
> 业界参考：npm install/uninstall、brew bundle、Skill CLI、Homebrew cleanup。
> 所有模板均为"用户对 agent 说什么"的标准 prompt。

## 一、设计哲学

```
用户 ──> Audit (大脑) ──> 输出"应做什么 + 指令模板"
                              ↓
用户 ──> Agent (动手) ──> 执行写入/安装/卸载
                              ↓
用户 ──> Audit ──> 验收回测
```

**原则**：
1. Audit 永远不直接写入（保持 v7.1.0 的只读底线）
2. Audit 输出的指令必须**可直接复制粘贴给 agent**
3. 指令必须包含**前置检查 + 主操作 + 后置验证**
4. 涉及不可逆操作（删除/卸载）必须包含**快照/回滚**

## 二、九大生命周期操作

| 操作 | 触发 | 风险 | 模板编号 |
|:-:|---|:-:|:-:|
| 安装 | 引入新技能/MCP | 中 | A |
| 升级 | 版本过期 | 低 | B |
| 卸载 | 不再用 | 中 | C |
| 归档 | 僵尸但保留 | 低 | D |
| 启用/禁用 | 临时切换 | 低 | E |
| 迁移 | 跨平台 | 高 | F |
| 重命名 | 触发词冲突 | 中 | G |
| 同步 | 跨平台一致 | 中 | H |
| 回滚 | 操作失败 | 低 | I |

## 三、模板规范

每个模板包含：

```yaml
template_spec:
  id: "A"  # 模板编号
  name: "安装"
  risk_level: "low|medium|high"
  reversible: true|false
  requires_snapshot: true|false
  confirmation_gates:  # 用户必须明确同意的检查点
    - "前置检查通过"
    - "已创建快照"
    - "目标路径确认"
    - "操作已完成"
    - "回测通过"
```

## 四、模板 A：安装新技能

```
[用户对 agent 说]

请帮我安装技能/插件 "firecrawl-mcp"，按以下步骤严格执行：

📋 前置检查
  1. 确认目标平台: ZCode | Claude | Codex（用户应说哪个）
  2. 确认作用域:
     - project: 写入 ./.zcode/skills/ 或 ./.claude/skills/
     - global: 写入 ~/.zcode/skills/ 或 ~/.claude/skills/
  3. 确认来源可信度（已由 Audit 评估）:
     - 来源 URL: https://github.com/firecrawl/firecrawl-mcp
     - 许可证: AGPL-3.0
     - Glama 安全评级: A
     - 健康分: 8.5
  4. 确认目录不存在（避免覆盖）

📸 创建快照
  1. 记录当前 skills/ 目录清单到 ~/.agents/skills/.audit-snapshots/{timestamp}.json
  2. 记录被修改的配置文件 mtime

🔧 主操作
  1. git clone https://github.com/firecrawl/firecrawl-mcp ~/.zcode/skills/firecrawl-mcp
     (或 curl 下载 SKILL.md 到目标目录)
  2. 如果是 MCP，追加到 ~/.zcode/cli/config.json 的 mcpServers 段:
     {
       "firecrawl": {
         "command": "npx",
         "args": ["-y", "firecrawl-mcp"],
         "env": { "FIRECRAWL_API_KEY": "<待用户填入>" }
       }
     }
  3. 不要写入任何 API Key（仅占位符）

✅ 后置验证
  1. 列出新目录结构，确认 SKILL.md 可解析
  2. 运行 collect_codex_display_candidates.py --scope visible --visible-id firecrawl --require-chinese
     验证触发词与描述
  3. 提示用户重启 ZCode 客户端
  4. 让用户提供刷新后的截图验收

⚠️ 风险点（必须告知用户）
  - 此技能需 FIRECRAWL_API_KEY，请到 https://firecrawl.dev 注册
  - 涉及网络请求，请确认隐私边界
  - 安装后请删除 SKILL.md 中可能的危险代码（手动 review）

🔄 回滚指令（如失败）
  rm -rf ~/.zcode/skills/firecrawl-mcp
  # 并从 config.json 移除 firecrawl 服务器块
```

## 五、模板 B：升级现有技能

```
[用户对 agent 说]

请帮我升级技能 "scrapling" 从 1.0.0 到 1.2.3：

📋 前置检查
  1. 读取当前版本: cat ~/.agents/skills/scrapling/VERSION
  2. 确认目标版本来源: https://github.com/D4Vinci/Scrapling/releases/tag/v1.2.3
  3. 阅读 CHANGELOG，列出关键变更:
     - v1.1.0: 新增 typosquatting 检测
     - v1.2.0: 性能优化 +30%
     - v1.2.3: 修复 #234
  4. 检查破坏性变更（breaking changes）
  5. 确认无本地修改（如 git status 干净）

📸 创建快照
  1. cp -r ~/.agents/skills/scrapling ~/.agents/skills/.audit-snapshots/scrapling-1.0.0-{date}
  2. 或 git stash（如果是 git 仓库）

🔧 主操作
  方案 1（git 仓库）:
    cd ~/.agents/skills/scrapling
    git fetch origin
    git checkout v1.2.3  # 或 git pull origin main
  
  方案 2（无 git）:
    rm -rf ~/.agents/skills/scrapling  # 仅在快照后
    git clone --branch v1.2.3 https://github.com/D4Vinci/Scrapling ~/.agents/skills/scrapling

✅ 后置验证
  1. cat VERSION  # 应为 1.2.3
  2. 运行该技能的 tests/（如有）
  3. 测试触发词: "技能审查 快速" 应能识别 scrapling
  4. 让用户在真实场景试用一次

🔄 回滚
  cd ~/.agents/skills/scrapling && git checkout v1.0.0
  # 或 rm -rf 后从快照恢复
```

## 六、模板 C：卸载

```
[用户对 agent 说]

请帮我卸载技能 "old-skill"：

📋 前置检查
  1. 确认无其他技能引用它（用 grep -r "old-skill" ~/.agents/skills/）
  2. 列出引用清单（如有），询问用户是否强制卸载
  3. 确认配置文件未硬编码（grep config.json/.yaml）
  4. 询问是否保留配置/数据（如有 .data/ 目录）

📸 创建快照（必做，因为卸载不可逆）
  tar czf ~/.agents/skills/.audit-snapshots/old-skill-{date}.tar.gz ~/.agents/skills/old-skill
  # 保留 30 天后自动清理（或用户指定）

🔧 主操作
  rm -rf ~/.agents/skills/old-skill
  
  如果是 MCP，从 config.json 移除:
    # 用 jq 安全修改:
    jq 'del(.mcpServers.old-skill)' ~/.zcode/cli/config.json > tmp && mv tmp ~/.zcode/cli/config.json
  
  如果是 Codex 插件:
    codex plugin uninstall old-skill  # 或手动 rm -rf 插件目录

✅ 后置验证
  1. ls ~/.agents/skills/old-skill  # 应不存在
  2. grep -r "old-skill" ~/.agents/ ~/.zcode/  # 应无残留
  3. 让用户重启客户端，确认触发词不再列出 old-skill

🔄 回滚（30 天内）
  tar xzf ~/.agents/skills/.audit-snapshots/old-skill-{date}.tar.gz -C /
```

## 七、模板 D：归档（保留备份）

```
[用户对 agent 说]

请归档僵尸技能 "deprecated-tool"（不删除，便于恢复）：

📋 前置检查
  1. 确认归档原因: 90 天未使用 + 健康分 4.5
  2. 检查是否有活跃的 cron/hook 引用
  3. 列出依赖该技能的脚本（如有）

📸 自动快照（mv 操作即可恢复）
  # 归档操作本身是可逆的，无需额外快照

🔧 主操作
  mkdir -p ~/.agents/skills/archived
  mv ~/.agents/skills/deprecated-tool ~/.agents/skills/archived/deprecated-tool-{date}
  
  # 在 archived/README.md 追加记录
  echo "| deprecated-tool | 2026-07-19 | 90 天未使用 + 健康分 4.5 | 可恢复 |" >> ~/.agents/skills/archived/README.md

  # 从扫描路径排除（如有 config 引用）
  # config.yaml 已通过 .archived 模式排除，无需修改

✅ 后置验证
  1. ls ~/.agents/skills/  # 应无 deprecated-tool
  2. ls ~/.agents/skills/archived/  # 应有 deprecated-tool-{date}
  3. 重启客户端确认触发词不再列出

🔄 恢复
  mv ~/.agents/skills/archived/deprecated-tool-{date} ~/.agents/skills/deprecated-tool
```

## 八、模板 E：启用/禁用（不删除）

```
[用户对 agent 说]

请帮我临时禁用技能 "experimental-feature"（保留文件，不触发）：

📋 前置检查
  1. 确认平台是否支持 enable/disable 配置:
     - ZCode: ~/.zcode/cli/config.json 的 skills 段
     - Claude Code: 暂无原生支持，需移到 archived/
     - Codex: agents/openai.yaml 可注释
  2. 确认禁用不影响其他技能依赖

🔧 主操作（按平台）

ZCode:
  # 编辑 ~/.zcode/cli/config.json
  # 在 skills 段追加:
  "experimental-feature": {
    "enabled": false,
    "path": "~/.agents/skills/experimental-feature",
    "disabled_at": "2026-07-19",
    "disabled_reason": "用户主动禁用"
  }

Claude Code（fallback 到 archived）:
  mv ~/.claude/skills/experimental-feature ~/.claude/skills/.disabled/experimental-feature
  # 注意: 不是所有平台都识别 .disabled/ 前缀

Codex:
  # 编辑 agents/openai.yaml
  # 在 experimental-feature 段追加: disabled: true

✅ 后置验证
  1. 重启客户端，确认触发词不再列出 experimental-feature
  2. 确认其他技能不受影响

🔄 启用
  将 enabled 改回 true，或 mv 回原目录
```

## 九、模板 F：跨平台迁移

```
[用户对 agent 说]

请帮我把技能 "summarize" 从 ZCode 迁移到 Claude Code：

📋 前置检查
  1. 确认源: ~/.zcode/skills/summarize/（版本 6.8.0）
  2. 确认目标: ~/.claude/skills/summarize/（应不存在或版本更低）
  3. 检查平台差异:
     - ZCode 特有配置: agents/zcode.yaml（如有）→ 转换为 agents/openai.yaml
     - 路径引用: 是否硬编码 ~/.zcode/ → 改为 ~/.claude/
     - MCP 依赖: 是否需在 Claude Code 也配置

📸 创建快照
  tar czf ~/.agents/skills/.audit-snapshots/summarize-migrate-{date}.tar.gz \
    ~/.zcode/skills/summarize/ ~/.claude/skills/summarize/  # 如有

🔧 主操作
  # 1. 复制（不删除源）
  cp -r ~/.zcode/skills/summarize ~/.claude/skills/summarize
  
  # 2. 平台适配
  cd ~/.claude/skills/summarize
  # 修改 SKILL.md 中的绝对路径
  sed -i 's|~/.zcode/|~/.claude/|g' SKILL.md references/*.md
  
  # 3. 删除源平台特有文件
  rm -f agents/zcode.yaml  # 如有
  
  # 4. 确保 Claude Code 必需文件存在
  test -f SKILL.md || echo "缺少 SKILL.md"
  test -f agents/openai.yaml || echo "建议创建 openai.yaml"

✅ 后置验证
  1. cat ~/.claude/skills/summarize/VERSION  # 应为 6.8.0
  2. 测试触发词 "总结" 在 Claude Code 是否触发
  3. 检查跨平台一致性（references/skill-marketplaces.md 第五节）

🔄 回滚
  rm -rf ~/.claude/skills/summarize
  # 源未删除，无需恢复

⚠️ 高风险提醒
  - 跨平台迁移常有平台特有差异，强烈建议先在测试项目试用
  - 数据目录（.data/）一般不迁移，避免污染新平台
```

## 十、模板 G：重命名（解决触发词冲突）

```
[用户对 agent 说]

请帮我把技能 "summarize-cli" 重命名为 "content-summary-cli"（解决与 summarize 冲突）：

📋 前置检查
  1. 列出所有引用 summarize-cli 的位置:
     grep -r "summarize-cli" ~/.agents/ ~/.zcode/ ~/.claude/ ~/.codex/
  2. 检查 git 历史（如果是 git 仓库）
  3. 准备新触发词: "内容总结"（避免与"总结"冲突）

📸 创建快照
  tar czf .audit-snapshots/summarize-cli-rename-{date}.tar.gz \
    ~/.agents/skills/summarize-cli/

🔧 主操作
  # 1. 目录重命名
  mv ~/.agents/skills/summarize-cli ~/.agents/skills/content-summary-cli
  
  # 2. 修改 SKILL.md frontmatter
  cd ~/.agents/skills/content-summary-cli
  # name: summarize-cli → name: content-summary-cli
  # description: "...总结..." → "...内容总结..."（触发词更新）
  
  # 3. 同步更新引用
  # - skill-registry.yaml 中的对应条目
  # - agents/openai.yaml 的 display_name
  # - README.md 中的自我引用
  
  # 4. 更新 codex-ui-zh-glossary.json 的 skill_overrides（如有）

✅ 后置验证
  1. cat SKILL.md | grep "^name:"  # 应为 content-summary-cli
  2. 运行 conflict-detection（references/conflict-detection.md）确认无新冲突
  3. 重启客户端，确认新触发词生效

🔄 回滚
  mv content-summary-cli summarize-cli
  # 恢复 SKILL.md 和引用
```

## 十一、模板 H：跨平台同步

```
[用户对 agent 说]

请帮我把"summarize"在不同平台的版本/描述同步一致：

📋 前置检查
  1. 列出所有平台版本:
     - ZCode: 6.8.0, description: A
     - Claude: 6.5.0, description: B
     - Codex: 6.8.0, description: A
  2. 确定基准: 选最新版本（6.8.0）+ 最佳描述（A）
  3. 列出待同步项: Claude 需升级 + 描述改为 A

🔧 主操作
  
  Step 1: 升级 Claude 版本
    [按模板 B 升级 Claude 上的 summarize 到 6.8.0]
  
  Step 2: 同步 description
    cp ~/.zcode/skills/summarize/SKILL.md ~/.claude/skills/summarize/SKILL.md
    # 注意: 路径差异需调整（按模板 F 步骤 2）
  
  Step 3: 同步 references/
    rsync -av --exclude='.data/' --exclude='.git/' \
      ~/.zcode/skills/summarize/references/ \
      ~/.claude/skills/summarize/references/

✅ 后置验证
  1. 三平台 VERSION 一致
  2. 三平台 description 一致
  3. 三平台触发词一致
  4. 运行跨平台一致性检查（references/skill-marketplaces.md 第五节）

🔄 回滚
  按平台单独恢复（每个平台有独立快照）
```

## 十二、模板 I：回滚

```
[用户对 agent 说]

刚才升级 scrapling 后触发词失效，请回滚：

📋 检查可回滚的快照
  ls -la ~/.agents/skills/.audit-snapshots/ | grep scrapling
  # 应该看到 scrapling-1.0.0-2026-07-19/ 或 .tar.gz

🔧 主操作
  
  方案 A（目录快照）:
    rm -rf ~/.agents/skills/scrapling
    cp -r ~/.agents/skills/.audit-snapshots/scrapling-1.0.0-2026-07-19 ~/.agents/skills/scrapling
  
  方案 B（tar.gz 快照）:
    rm -rf ~/.agents/skills/scrapling
    tar xzf ~/.agents/skills/.audit-snapshots/scrapling-1.0.0-2026-07-19.tar.gz -C /
  
  方案 C（git 仓库）:
    cd ~/.agents/skills/scrapling
    git checkout v1.0.0

✅ 后置验证
  1. cat VERSION  # 应为 1.0.0
  2. 测试触发词
  3. 用户确认问题已解决

📝 复盘
  记录本次失败到 ~/.agents/skills/.audit-snapshots/rollback-log.jsonl:
    {
      "skill": "scrapling",
      "attempted": "1.0.0 → 1.2.3",
      "failed_at": "2026-07-19T03:00Z",
      "failure_reason": "触发词失效",
      "rolled_back_to": "1.0.0"
    }
```

## 十三、模板选择决策树

```
用户的需求是什么？
│
├─ 引入新工具 → 模板 A
├─ 升级现有 → 模板 B
├─ 不再用 → 模板 C (删除) 或 D (归档)
├─ 临时切换 → 模板 E (启用/禁用)
├─ 换平台 → 模板 F (迁移)
├─ 改名 → 模板 G (重命名)
├─ 多平台同步 → 模板 H
└─ 操作失败 → 模板 I (回滚)
```

## 十四、与 v7.1.0 的关系

### 替代 v7.1.0 的 06-e-action-plan.md

```yaml
# v7.1.0 的"下一步建议"过于抽象：
v7_1_0_example: "建议直接调用发布 Agent，并提供目标仓库与发布范围"

# v1.0（本文件）的"具体指令"可直接复制：
v1_0_example: |
  [对 agent 说]
  请按模板 B 升级 scrapling...
  [完整 8 步指令]
```

### 保留 v7.1.0 的边界

- 仍然不主动执行任何操作
- 仍然要求用户明确授权
- 仍然输出"建议"而非"强制"

### 增强内容

- 把抽象建议变成可执行 prompt 模板
- 加入前置检查/快照/验证/回滚四步
- 加入风险点和明确告知

## 十五、维护

- 新增操作类型：本文件第三节"九大生命周期操作"
- 模板更新：第四-十二节
- 平台适配：根据实际平台扩展（OpenCode / Cursor / Windsurf 等）
- 业界对照：Skill CLI / npm / brew / pip 在 _docs/package-managers-research.md（如有）
