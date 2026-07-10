#!/usr/bin/env python3
"""skills-audit 自动化验证脚本

每次修改后运行，检查 YAML 可解析性、版本一致性、8维权重和、
平台配置合规性、flow 文件格式等。
"""
import hashlib
import json
import re
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
        "审查技能": [],
        "skills-audit/issues": [],
    }
    historical = {"self-audit-issues.json", "CHANGELOG.md", "README.md"}
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".yaml", ".yml", ".json", ".ps1", ".sh"}:
            c = f.read_text(encoding="utf-8", errors="ignore")
            for pat in patterns:
                if re.search(pat, c):
                    if f.name in historical and pat in {"五维", "审查技能", "5dim"}:
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
    """审计默认只读，且所有用户可见结论必须保留事实状态。"""
    errors = []
    config = (ROOT / "config.yaml").read_text(encoding="utf-8-sig")
    expected_config = {
        "write_policy.default_mode": r"write_policy:\s*\n\s+default_mode:\s*\"read_only\"",
        "write_policy.confirmation": r"require_explicit_confirmation:\s*true",
        "memory_config.auto_sync": r"memory_config:[\s\S]*?auto_sync:\s*false",
        "project_profiles.auto_persist": r"project_profiles:[\s\S]*?auto_persist:\s*false",
        "trend_tracking.enabled": r"trend_tracking:[\s\S]*?enabled:\s*false",
        "logging.enabled": r"logging:\s*\n\s+enabled:\s*false",
        "quality_signals.fallback": r"fallback_score:\s*null",
    }
    for name, pattern in expected_config.items():
        if not re.search(pattern, config):
            errors.append(f"缺少只读/事实配置: {name}")

    contract = (ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
    for state in ["observed", "inferred", "estimated", "unavailable", "[需确认]"]:
        if state not in contract:
            errors.append(f"输出契约缺少状态: {state}")

    report = (ROOT / "references" / "report-template.md").read_text(encoding="utf-8")
    for forbidden in ["健康度: 良好", "~3,200 tokens", "归档 3 项", "installed skills token 成本"]:
        if forbidden in report:
            errors.append(f"报告模板含无证据示例结论: {forbidden}")

    output_check = (ROOT / "references" / "flow" / "06-c-output-check.md").read_text(encoding="utf-8")
    if "[需确认]" not in output_check or "事实状态" not in output_check:
        errors.append("输出检查未强制事实状态或确认门禁")

    preflight = (ROOT / "references" / "flow" / "00-config.md").read_text(encoding="utf-8")
    if "codegraph --help" not in preflight or "命令存在但探针失败" not in preflight:
        errors.append("关键工具未要求可执行探针与降级")

    verify = (ROOT / "references" / "flow" / "06-bis-verify.md").read_text(encoding="utf-8")
    if "execution_blocked=true" not in verify:
        errors.append("自检或安全失败未阻止执行")

    signals = (ROOT / "references" / "flow" / "05-signals.md").read_text(encoding="utf-8")
    deepread = (ROOT / "references" / "flow" / "04-bis-deepread.md").read_text(encoding="utf-8")
    execute = (ROOT / "references" / "flow" / "07-c-execute.md").read_text(encoding="utf-8")
    if "用户明确同意本次联网查询" not in signals or "用户明确同意本次联网查询" not in deepread:
        errors.append("外部信号或深读外部验证缺少联网同意门禁")
    if "execution_blocked=true" not in execute:
        errors.append("执行阶段未检查 execution_blocked")

    flow = (ROOT / "references" / "execution-flow.md").read_text(encoding="utf-8")
    if "⑦-b确认→⑦-a快照→⑦-c执行" not in flow:
        errors.append("执行流程未保持确认优先于快照")
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

    # 3. Weight sum
    total = weight_sum()
    ok = abs(total - 1.0) < 0.001
    failed |= not ok
    results.append(("8维权重和", ok, [f"sum = {total:.3f}"]))

    # 3b. Forma weight sum
    forma_total = forma_weight_sum()
    ok = abs(forma_total - 1.0) < 0.001 or forma_total == 0.0
    failed |= not ok and forma_total > 0
    results.append(("Forma四维权重和", ok, [f"sum = {forma_total:.3f}" if forma_total > 0 else "未检测到"]))

    # 3c. 健康阈值合理性
    thresh_issues = health_thresholds()
    ok = not thresh_issues
    failed |= not ok
    results.append(("健康阈值合理性", ok, thresh_issues or ["OK"]))

    # 4. Stale strings
    stale = stale_strings()
    issues = [f"{k}: {v}" for k, v in stale.items() if v]
    ok = not issues
    failed |= not ok
    results.append(("陈旧字符串", ok, issues or ["none"]))

    # 5. Platform compliance
    errs = platform_compliance()
    ok = not errs
    failed |= not ok
    results.append(("平台配置合规", ok, errs or ["OK"]))

    # 6. Flow format
    errs = flow_format()
    ok = not errs
    failed |= not ok
    results.append(("flow 格式", ok, errs or ["OK"]))

    # 7. Data directory
    errs = data_directory()
    ok = not errs
    failed |= not ok
    results.append(("数据目录", ok, errs or ["OK"]))

    # 8. Release contract
    errs = release_contract()
    ok = not errs
    failed |= not ok
    results.append(("发布契约", ok, errs or ["OK"]))

    # 9. Behavior and output contract
    errs = behavior_and_output_contract()
    ok = not errs
    failed |= not ok
    results.append(("行为与输出契约", ok, errs or ["OK"]))

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
