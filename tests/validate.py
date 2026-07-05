#!/usr/bin/env python3
"""skills-audit 自动化验证脚本

每次修改后运行，检查 YAML 可解析性、版本一致性、7维权重和、
平台配置合规性、flow 文件格式等。
"""
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


def parse_yaml_files():
    """所有 .yaml 文件可解析"""
    if not HAS_YAML:
        return ["PyYAML 未安装，跳过 YAML 解析检查（pip install pyyaml 可启用）"]
    errors = []
    for f in ROOT.rglob("*.yaml"):
        try:
            with open(f, "r", encoding="utf-8-sig") as fh:
                yaml.safe_load(fh)
        except Exception as e:
            errors.append(f"{f.relative_to(ROOT)}: {e}")
    return errors


def version_consistency():
    """VERSION / SKILL.md / README.md / CHANGELOG / skill-registry.yaml 一致"""
    versions = {}
    for f in [
        ROOT / "VERSION",
        ROOT / "SKILL.md",
        ROOT / "README.md",
        ROOT / "references" / "skill-registry.yaml",
    ]:
        if f.exists():
            c = f.read_text(encoding="utf-8")
            m = re.search(r"(?:version|VERSION).{0,10}(5\.\d+\.\d+)", c, re.IGNORECASE)
            if m:
                versions[str(f.relative_to(ROOT))] = m.group(1)
    c = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(r"^## \[(5\.\d+\.\d+)\]", c, re.MULTILINE)
    if m:
        versions["CHANGELOG.md"] = m.group(1)
    return versions


def weight_sum():
    """7维权重和 = 100%"""
    c = (ROOT / "references" / "flow" / "04-scoring.md").read_text(encoding="utf-8")
    m = re.search(r"综合\s*=\s*(.+?)(?:\n|$)", c)
    if not m:
        return 0.0
    expr = m.group(1)
    decimals = re.findall(r"[×\*]\s*0\.(\d+)", expr)
    return sum(int(d) / 1000 if len(d) == 3 else int(d) / 100 for d in decimals)


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


def main():
    results = []
    failed = False

    # 1. YAML parse
    errs = parse_yaml_files()
    ok = not errs or (len(errs) == 1 and "PyYAML 未安装" in errs[0])
    failed |= not ok
    results.append(("YAML 解析", ok, errs))

    # 2. Version
    versions = version_consistency()
    ok = len(set(versions.values())) <= 1
    failed |= not ok
    results.append(("版本一致性", ok, [f"{k}: {v}" for k, v in versions.items()]))

    # 3. Weight sum
    total = weight_sum()
    ok = abs(total - 1.0) < 0.001
    failed |= not ok
    results.append(("7维权重和", ok, [f"sum = {total:.3f}"]))

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
