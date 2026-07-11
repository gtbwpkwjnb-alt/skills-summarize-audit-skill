#!/usr/bin/env python3
"""skills-audit 自动化验证脚本

每次修改后运行，检查 YAML 可解析性、版本一致性、8维权重和、
平台配置合规性、flow 文件格式等。
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT = Path(__file__).resolve().parent.parent


def parse_yaml_files(strict=False):
    """所有 .yaml 文件可解析"""
    if not HAS_YAML:
        message = "PyYAML 未安装，无法执行 YAML 解析检查（pip install pyyaml）"
        return [message] if strict else [message + "；非严格模式跳过"]
    errors = []
    for f in ROOT.rglob("*.yaml"):
        try:
            with open(f, "r", encoding="utf-8-sig") as fh:
                yaml.safe_load(fh)
        except Exception as e:
            errors.append(f"{f.relative_to(ROOT)}: {e}")
    return errors


def version_consistency():
    """所有对外版本源必须与 VERSION 一致。"""
    checks = {
        "VERSION": (ROOT / "VERSION", r"^\s*(\d+\.\d+\.\d+)\s*$"),
        "SKILL.md": (ROOT / "SKILL.md", r"^> Version:\s*(\d+\.\d+\.\d+)"),
        "README.md": (ROOT / "README.md", r"^# .*?v(\d+\.\d+\.\d+)"),
        "CHANGELOG.md": (ROOT / "CHANGELOG.md", r"^## \[(\d+\.\d+\.\d+)\]"),
        "config.yaml": (ROOT / "config.yaml", r"^# skills-summarize-audit v(\d+\.\d+\.\d+)"),
        "actions-schema.md": (ROOT / "references" / "actions-schema.md", r"^# .*?v(\d+\.\d+\.\d+)"),
        "ci-output-schema.md": (ROOT / "references" / "ci-output-schema.md", r'"version":\s*"(\d+\.\d+\.\d+)"'),
    }
    versions = {}
    for name, (path, pattern) in checks.items():
        if not path.exists():
            versions[name] = "MISSING"
            continue
        match = re.search(pattern, path.read_text(encoding="utf-8-sig"), re.MULTILINE)
        versions[name] = match.group(1) if match else "MISSING"
    return versions


def registry_self_version():
    """skill-registry.yaml 中自身条目版本与 VERSION 一致"""
    registry_path = ROOT / "references" / "skill-registry.yaml"
    if not registry_path.exists():
        return {"error": "skill-registry.yaml 不存在"}
    c = registry_path.read_text(encoding="utf-8")
    # 匹配 skills-summarize-audit 条目下的 version
    m = re.search(
        r'name:\s*"skills-summarize-audit"\s*\n\s*version:\s*"(\d+\.\d+\.\d+)"',
        c,
    )
    if not m:
        return {"error": "未找到自身版本条目"}
    registry_ver = m.group(1)

    version_file = ROOT / "VERSION"
    if version_file.exists():
        actual_ver = version_file.read_text(encoding="utf-8").strip()
    else:
        return {"error": "VERSION 文件不存在"}

    return {
        "registry": registry_ver,
        "VERSION": actual_ver,
        "match": registry_ver == actual_ver,
    }


def weight_sum():
    """8维权重和 = 100%"""
    c = (ROOT / "references" / "flow" / "04-scoring.md").read_text(encoding="utf-8")
    m = re.search(r"综合\s*=\s*(.+?)(?:\n|$)", c)
    if not m:
        return 0.0
    expr = m.group(1)
    decimals = re.findall(r"[×\*]\s*0\.(\d+)", expr)
    return sum(int(d) / 1000 if len(d) == 3 else int(d) / 100 for d in decimals)


def forma_weight_sum():
    """Forma 四维权重和 = 100%"""
    c = (ROOT / "config.yaml").read_text(encoding="utf-8")
    # 提取 forma_check.weights 下的四个权重值
    weights = re.findall(r"(\w+):\s*0\.(\d+)", c)
    forma_weights = [v for k, v in weights if k in {"format_style", "language_consistency", "length_limit", "info_density"}]
    if not forma_weights:
        return 0.0
    return sum(int(d) / 100 if len(d) == 2 else int(d) / 1000 for d in forma_weights)


def health_thresholds():
    """健康阈值合理性检查"""
    c = (ROOT / "config.yaml").read_text(encoding="utf-8")
    issues = []
    # max_total_skills 应为正数
    m = re.search(r"max_total_skills:\s*(\d+)", c)
    if m and int(m.group(1)) <= 0:
        issues.append("max_total_skills 应为正数")
    # t3_ratio 应在 0-1 之间
    m = re.search(r"max_t3_ratio:\s*([\d.]+)", c)
    if m:
        val = float(m.group(1))
        if val <= 0 or val >= 1:
            issues.append(f"max_t3_ratio={val} 应在 0-1 之间")
    return issues


def stale_strings():
    """检查非历史文档中的陈旧字符串"""
    patterns = {
        "五维": [],
        "5dim": [],
        "v5.10.0": [],
        "skills-audit/issues": [],
    }
    historical = {"self-audit-issues.json", "CHANGELOG.md", "README.md"}
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".yaml", ".yml", ".json", ".ps1", ".sh"}:
            c = f.read_text(encoding="utf-8", errors="ignore")
            for pat in patterns:
                if re.search(pat, c):
                    if f.name in historical and pat in {"五维", "5dim"}:
                        continue
                    patterns[pat].append(str(f.relative_to(ROOT)))
    return patterns


def platform_compliance():
    """平台文件不应定义 scan_paths / trigger_words"""
    errors = []
    for f in (ROOT / "platforms").glob("*.yaml"):
        c = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"^scan_paths\s*:", c, re.MULTILINE):
            errors.append(f"{f.relative_to(ROOT)}: scan_paths 定义存在")
        if re.search(r"^trigger_words\s*:", c, re.MULTILINE):
            errors.append(f"{f.relative_to(ROOT)}: trigger_words 定义存在")
    return errors


def flow_format():
    """flow 文件无单引号多行代码块"""
    errors = []
    for f in (ROOT / "references" / "flow").glob("*.md"):
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            if line.strip() == "`":
                errors.append(f"{f.relative_to(ROOT)}:{i}: 单引号多行代码块未转换")
    return errors


def data_directory():
    """.data/ 目录包含必要运行时文件"""
    data_dir = ROOT / ".data"
    errors = []
    for name in ["stats.json", "project-profiles.json", "activity-log.jsonl"]:
        if not (data_dir / name).exists():
            errors.append(f".data/{name} 不存在")
    return errors


def release_contract():
    """发布门禁：安全安装、外部访问、范围协议和证据输出必须齐备。"""
    errors = []
    config = (ROOT / "config.yaml").read_text(encoding="utf-8-sig")
    if not re.search(
        r"community_feed:\s*\n\s+enabled:\s*false\b[\s\S]*?require_explicit_consent:\s*true\b",
        config,
    ):
        errors.append("community_feed 必须默认关闭且要求明确同意")
    if "scope_targets:" not in config or "recommendation_scope:" not in config:
        errors.append("缺少项目/全局作用域配置")

    required = [
        ROOT / "references" / "flow" / "05-ab-github-comparison.md",
        ROOT / "references" / "flow" / "05-c-scope-decision.md",
        ROOT / "references" / "release-checklist.md",
        ROOT / "references" / "output-contract.md",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"缺少发布协议文件: {path.relative_to(ROOT)}")

    actions = (ROOT / "references" / "actions-schema.md").read_text(encoding="utf-8")
    for field in ["install_scope", "target_path", "scope_reason", "evidence_urls", "confirmation_required"]:
        if field not in actions:
            errors.append(f"actions schema 缺少 {field}")

    sh = (ROOT / "install.sh").read_text(encoding="utf-8")
    ps1 = (ROOT / "install.ps1").read_text(encoding="utf-8")
    if "--dry-run" not in sh or "git pull --ff-only" not in sh or "rm -rf" in sh:
        errors.append("install.sh 不满足安全更新契约")
    if "[switch]$DryRun" not in ps1 or "git pull --ff-only" not in ps1 or "Remove-Item -Recurse" in ps1:
        errors.append("install.ps1 不满足安全更新契约")

    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    if re.search(r"curl\s+.*\|\s*bash", readme, re.IGNORECASE) or re.search(r"iwr\s+.*\|\s*iex", readme, re.IGNORECASE):
        errors.append("README 仍含远程脚本管道执行示例")
    for name in ["install.sh", "install.ps1"]:
        expected = re.search(rf"\| `{re.escape(name)}` \| `([A-F0-9]{{64}})`", readme)
        if not expected:
            errors.append(f"README 缺少 {name} SHA256")
            continue
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest().upper()
        if expected.group(1) != actual:
            errors.append(f"README 中 {name} SHA256 不匹配")

    ci = (ROOT / "references" / "ci-github-actions.yml").read_text(encoding="utf-8")
    if "python tests/validate.py --strict" not in ci:
        errors.append("CI 未强制执行严格发布验证")
    return errors


def behavior_and_output_contract():
    """主流程只能覆盖翻译精炼、项目画像和推荐，且默认只读。"""
    errors = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8-sig")
    report = (ROOT / "references" / "report-template.md").read_text(encoding="utf-8")
    flow = (ROOT / "references" / "execution-flow.md").read_text(encoding="utf-8")
    for required in ["技能库翻译精炼", "项目画像", "技能/插件推荐", "默认只读"]:
        if required not in skill:
            errors.append(f"SKILL.md 缺少核心边界: {required}")
    for required in ["翻译精炼", "项目画像", "推荐", "明确不做"]:
        if required not in flow:
            errors.append(f"主流程缺少精简能力定义: {required}")
    for required in ["中文翻译候选", "项目画像", "💡 推荐", "➡️ 下一步建议"]:
        if required not in report:
            errors.append(f"报告模板缺少核心区块: {required}")
    if "外部搜索必须取得本次明确同意" not in skill:
        errors.append("SKILL.md 缺少联网同意门禁")
    return errors


def codex_display_candidate_contract():
    """严格门禁：三类 Codex 展示源必须能只读生成中文候选。"""
    test = ROOT / "tests" / "test_collect_codex_display_candidates.py"
    collector = ROOT / "scripts" / "collect_codex_display_candidates.py"
    if not test.exists() or not collector.exists():
        return ["缺少 Codex 展示候选采集器或 fixture 测试"]
    result = subprocess.run(
        [sys.executable, str(test)], cwd=ROOT, text=True, capture_output=True, timeout=30
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        return [f"Codex 展示候选 fixture 失败: {detail}"]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return [f"Codex 展示候选 fixture 未输出 JSON: {exc}"]
    if payload.get("result") != "passed":
        return ["Codex 展示候选 fixture 未通过"]
    return []


def translation_and_decision_output_contract():
    """中文候选与三项核心输出必须可审计。"""
    errors = []
    glossary = ROOT / "references" / "codex-ui-zh-glossary.json"
    if not glossary.exists():
        return ["缺少 Codex 中文术语库"]
    try:
        data = json.loads(glossary.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"Codex 中文术语库无法解析: {exc}"]
    for key in ["protected_terms", "phrases", "words"]:
        if not data.get(key):
            errors.append(f"Codex 中文术语库缺少 {key}")

    source_map = ROOT / "references" / "display-source-map.md"
    if not source_map.exists():
        errors.append("缺少 Agent 展示文案来源地图")
    else:
        mapping = source_map.read_text(encoding="utf-8")
        for token in ["agents/openai.yaml", ".codex-plugin/plugin.json", "remote_plugin_catalog", "commands/<name>.md", "unavailable"]:
            if token not in mapping:
                errors.append(f"展示来源地图缺少: {token}")

    collector = (ROOT / "scripts" / "collect_codex_display_candidates.py").read_text(encoding="utf-8")
    for token in ["translation_quality", "long_description_quality", "inventory_scope", "codex_plugin_manifest", "manifest_candidates", "INSTALLED_SOURCE_TYPES", "--scope", "--visible-id", "--require-chinese", "--expect-visible-count", "untranslated_visible_items", "user_provided_visible_ui_evidence", "needs_agent_refinement", "GLOSSARY_PATH"]:
        if token not in collector:
            errors.append(f"采集器缺少翻译质量契约: {token}")

    report = (ROOT / "references" / "report-template.md").read_text(encoding="utf-8")
    for section in ["当前用户作用", "中文翻译候选", "项目画像", "💡 推荐", "➡️ 下一步建议"]:
        if section not in report:
            errors.append(f"报告模板缺少核心区块: {section}")
    return errors


def audit_ui_and_skill_contract():
    """Audit 自身 UI 元数据须中文、可触发且不保留过时输出范式。"""
    errors = []
    ui_path = ROOT / "agents" / "openai.yaml"
    if not ui_path.exists():
        return ["缺少 Audit 自身 agents/openai.yaml"]
    ui = ui_path.read_text(encoding="utf-8-sig")
    expected = {
        "display_name": "可见技能中文导览",
        "short_description": "可见技能中文化·项目画像·工具推荐",
        "default_prompt": "使用 $skills-summarize-audit 仅对当前 Codex 可见技能生成中文触发词与简介。",
    }
    for key, value in expected.items():
        if f'{key}: "{value}"' not in ui:
            errors.append(f"Audit UI 元数据缺少中文 {key}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8-sig")
    for required in ["references/report-template.md", "当前 UI 可见", "--visible-id", "用户交互与反馈", "项目画像", "技能/插件推荐", "## 边界"]:
        if required not in skill:
            errors.append(f"SKILL.md 缺少当前输出规则: {required}")
    for stale in ["随后输出评分表片段", "优先输出 30 秒摘要块", "references/installation.md", "CI/CD 无交互模式"]:
        if stale in skill:
            errors.append(f"SKILL.md 保留过时输出或无效引用: {stale}")
    return errors


def main():
    results = []
    failed = False
    strict = "--strict" in sys.argv

    # 1. YAML parse
    errs = parse_yaml_files(strict=strict)
    ok = not errs or (not strict and len(errs) == 1 and "非严格模式跳过" in errs[0])
    failed |= not ok
    results.append(("YAML 解析", ok, errs))

    # 2. Version
    versions = version_consistency()
    ok = len(set(versions.values())) <= 1
    failed |= not ok
    results.append(("版本一致性", ok, [f"{k}: {v}" for k, v in versions.items()]))

    # 2b. Registry 自身版本
    reg_ver = registry_self_version()
    ok = reg_ver.get("match", False)
    failed |= not ok
    details = [f"registry: {reg_ver.get('registry', 'N/A')}", f"VERSION: {reg_ver.get('VERSION', 'N/A')}"]
    if "error" in reg_ver:
        details = [reg_ver["error"]]
    results.append(("Registry自身版本", ok, details))

    # 3. Three-capability behavior and output contract
    errs = behavior_and_output_contract()
    ok = not errs
    failed |= not ok
    results.append(("三项能力与输出契约", ok, errs or ["OK"]))

    # 4. Codex display candidate collector
    errs = codex_display_candidate_contract()
    ok = not errs
    failed |= not ok
    results.append(("Codex 展示候选只读门禁", ok, errs or ["OK"]))

    # 5. Translation quality and concise decision report
    errs = translation_and_decision_output_contract()
    ok = not errs
    failed |= not ok
    results.append(("翻译质量与分类输出门禁", ok, errs or ["OK"]))

    # 6. Audit 自身 UI 文案与主工作流
    errs = audit_ui_and_skill_contract()
    ok = not errs
    failed |= not ok
    results.append(("Audit UI 与主工作流门禁", ok, errs or ["OK"]))

    print("=" * 60)
    print("skills-audit 自动化验证")
    print("=" * 60)
    for name, ok, details in results:
        status = "✅" if ok else "❌"
        print(f"{status} {name}")
        for d in details:
            print(f"   {d}")
    print("=" * 60)
    print(f"结果: {'通过' if not failed else '失败'}")
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
