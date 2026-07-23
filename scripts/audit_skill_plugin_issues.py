#!/usr/bin/env python3
"""Read-only local issue audit for installed skills and plugin skill sources."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allow direct execution and fixture loading without installing this skill as a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from collect_codex_display_candidates import (
    collect,
    frontmatter,
    logical_items,
    unresolved_visible_items,
)


def issue(item: dict, code: str, severity: str, message: str, remediation: str, evidence: list[str]) -> dict:
    return {
        "id": item.get("id"),
        "source_type": item.get("source_type"),
        "severity": severity,
        "code": code,
        "message": message,
        "remediation": remediation,
        "evidence": evidence,
        "editable": item.get("editable", False),
    }


def audit_item(item: dict) -> list[dict]:
    issues: list[dict] = []
    source_paths = [Path(value) for value in item.get("source_paths", [])]
    skill_paths = sorted({path for path in source_paths if path.name == "SKILL.md"})
    if item.get("fact_status") != "observed":
        return [issue(item, "SOURCE_UNAVAILABLE", "critical", "技能来源无法解析", "修复或重新安装来源后再审查。", [str(path) for path in source_paths])]

    if item.get("source_conflict"):
        issues.append(issue(item, "SOURCE_DIVERGENCE", "critical", "同一技能 ID 的安装来源内容不同。", "先用 UI 证据确认 cache/staging/用户来源，再只修改确认的可编辑来源。", [str(path) for path in source_paths]))
    elif item.get("source_resolution_status") == "equivalent_sources":
        issues.append(issue(item, "DUPLICATE_EQUIVALENT_SOURCE", "info", "cache 与 staging 内容一致，存在重复部署来源。", str(item.get("source_resolution_plan") or "以 cache 为当前来源，staging 仅作待刷新来源。"), [str(path) for path in source_paths]))

    if item.get("translation_quality") != "ready":
        issues.append(issue(item, "DESCRIPTION_NEEDS_REFINEMENT", "warning", "技能展示说明仍需人工精炼。", "按翻译质量规则生成候选，保留 ID 和 display_name 后回读验证。", [str(path) for path in source_paths]))

    for skill_path in skill_paths:
        meta = frontmatter(skill_path)
        missing = [field for field in ("name", "description") if not str(meta.get(field) or "").strip()]
        if missing:
            issues.append(issue(item, "METADATA_MISSING", "warning", "SKILL.md frontmatter 缺少: " + ", ".join(missing), "补齐 frontmatter；系统或插件来源通过上游包更新，不直接改 cache。", [str(skill_path)]))
        ui_path = skill_path.parent / "agents" / "openai.yaml"
        if not ui_path.exists():
            issues.append(issue(item, "UI_METADATA_FALLBACK", "info", "未找到 agents/openai.yaml，将回退到 SKILL.md frontmatter。", "用户 skill 可补充 UI metadata；系统/插件 skill 保持只读并通过上游发布更新。", [str(skill_path)]))
    return issues


def load_profile(profile_path: Path | None) -> tuple[str, str]:
    if profile_path is None or not profile_path.exists():
        return "", "unavailable"
    try:
        return profile_path.read_text(encoding="utf-8-sig", errors="replace"), "observed"
    except OSError:
        return "", "unavailable"


def terms(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9+.-]{2,}", text)}


def item_terms(item: dict) -> set[str]:
    return terms(" ".join([
        str(item.get("id", "")),
        str(item.get("command_palette", {}).get("original", "")),
        str(item.get("sidebar", {}).get("original", "")),
        str(item.get("sidebar", {}).get("short_description", "")),
    ]))


def version_info(item: dict) -> dict:
    for raw_path in item.get("source_paths", []):
        path = Path(raw_path)
        for parent in (path.parent, *path.parents):
            version_file = parent / "VERSION"
            if version_file.exists():
                value = version_file.read_text(encoding="utf-8-sig", errors="replace").strip()
                match = re.search(r"\d+(?:\.\d+)+", value)
                if match:
                    return {"status": "observed", "version": match.group(0), "source": str(version_file)}
        for part in path.parts:
            if re.fullmatch(r"\d+(?:\.\d+)+", part):
                return {"status": "observed", "version": part, "source": str(path)}
    return {"status": "unavailable", "version": None, "source": None}


def score_items(items: list[dict], item_issues: list[dict], profile_text: str, profile_status: str) -> list[dict]:
    by_id: dict[str, list[dict]] = {}
    for entry in item_issues:
        by_id.setdefault(entry["id"], []).append(entry)
    profile_terms = terms(profile_text)
    results: list[dict] = []
    for item in items:
        codes = {entry["code"] for entry in by_id.get(item["id"], [])}
        dimensions = {
            "existence": 0 if "SOURCE_UNAVAILABLE" in codes else 10,
            "metadata": 4 if "METADATA_MISSING" in codes else 10,
            "source": 0 if "SOURCE_DIVERGENCE" in codes else 10,
            "description": 6 if "DESCRIPTION_NEEDS_REFINEMENT" in codes else 10,
            "version": 5 if version_info(item)["status"] == "observed" else None,
        }
        available = [value for value in dimensions.values() if value is not None]
        score = round(sum(available) / len(available), 1) if available else 0
        if profile_status == "observed":
            overlap = item_terms(item) & profile_terms
            alignment = {"status": "observed", "score": round(min(10.0, len(overlap) * 2.0), 1), "matched_terms": sorted(overlap)}
        else:
            alignment = {"status": "unavailable", "score": None, "matched_terms": []}
        results.append({"id": item["id"], "health_score": score, "dimensions": dimensions, "profile_alignment": alignment, "version": version_info(item)})
    return results


def relationships(items: list[dict], scores: list[dict]) -> tuple[list[dict], dict[str, int]]:
    score_map = {entry["id"]: entry["profile_alignment"].get("score") for entry in scores}
    result: list[dict] = []
    counts = {"conflict": 0, "complementary": 0, "unrelated": 0}
    for index, left in enumerate(items):
        left_terms = item_terms(left)
        for right in items[index + 1:]:
            right_terms = item_terms(right)
            union = left_terms | right_terms
            overlap = left_terms & right_terms
            ratio = round(len(overlap) / len(union), 3) if union else 0.0
            if ratio >= 0.5:
                relationship = "conflict"
                reason = "触发词或描述高度重叠"
            elif ratio <= 0.15 and (score_map.get(left["id"]) or 0) > 0 and (score_map.get(right["id"]) or 0) > 0:
                relationship = "complementary"
                reason = "用户画像相关但能力词集合重叠较低"
            else:
                relationship = "unrelated"
                reason = "当前证据不足以判定冲突或互补"
            counts[relationship] += 1
            if relationship != "unrelated":
                result.append({"left": left["id"], "right": right["id"], "relationship": relationship, "overlap_score": ratio, "reason": reason})
    return result, counts


def audit(root: Path, catalog_dir: Path, runtime_dir: Path, staging_dir: Path | None, user_skill_dir: Path | None, scope: str, visible_ids: list[str], profile_path: Path | None = None) -> tuple[dict, list[Path]]:
    items, watched = collect(root, catalog_dir, runtime_dir, staging_dir, user_skill_dir)
    selected = logical_items(items, scope, visible_ids if scope == "visible" else None)
    issues = [entry for item in selected for entry in audit_item(item)]
    profile_text, profile_status = load_profile(profile_path)
    scores = score_items(selected, issues, profile_text, profile_status)
    by_severity = {severity: sum(entry["severity"] == severity for entry in issues) for severity in ("critical", "warning", "info")}
    relationship_items, relationship_counts = relationships(selected, scores)
    report = {
        "schema_version": 1,
        "mode": "read_only",
        "scope": scope,
        "summary": {"items_scanned": len(selected), "issues": len(issues), "by_severity": by_severity},
        "unresolved_items": unresolved_visible_items(selected) if scope == "visible" else [],
        "issues": issues,
        "profile": {"status": profile_status, "source": str(profile_path) if profile_status == "observed" else None},
        "skill_scores": scores,
        "relationships": relationship_items,
        "relationship_counts": relationship_counts,
        "items": selected,
        "watched_source_count": len(watched),
    }
    return report, watched


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local skill/plugin issues without writing files.")
    parser.add_argument("--root", type=Path, default=Path(__import__("os").environ.get("CODEX_HOME", Path.home() / ".codex")))
    parser.add_argument("--catalog-dir", type=Path)
    parser.add_argument("--runtime-dir", type=Path, default=Path.home() / ".cache" / "codex-runtimes")
    parser.add_argument("--staging-dir", type=Path)
    parser.add_argument("--user-skill-dir", type=Path, default=Path.home() / ".agents" / "skills")
    parser.add_argument("--profile", type=Path, default=None, help="用户画像文件；缺失时 profile_alignment=unavailable。")
    parser.add_argument("--scope", choices=("installed", "visible", "all"), default="installed")
    parser.add_argument("--visible-id", action="append", default=[])
    parser.add_argument("--fail-on", choices=("none", "info", "warning", "critical"), default="none")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    catalog_dir = args.catalog_dir or args.root / "cache" / "remote_plugin_catalog"
    staging_dir = args.staging_dir or args.root / ".tmp" / "bundled-marketplaces"
    report, _ = audit(
        args.root,
        catalog_dir,
        args.runtime_dir,
        staging_dir if staging_dir.exists() else None,
        args.user_skill_dir,
        args.scope,
        args.visible_id,
        args.profile or (args.user_skill_dir / "skills-summarize-audit" / "user-profile.md"),
    )
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"技能/插件问题审查（{args.scope}）：扫描 {report['summary']['items_scanned']} 项，发现 {report['summary']['issues']} 项")
        for entry in report["issues"]:
            print(f"[{entry['severity']}] {entry['id']} {entry['code']}: {entry['message']} 处理：{entry['remediation']}")
    order = {"info": 1, "warning": 2, "critical": 3, "none": 0}
    if args.fail_on != "none" and any(order[entry["severity"]] >= order[args.fail_on] for entry in report["issues"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
