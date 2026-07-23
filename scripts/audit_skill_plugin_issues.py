#!/usr/bin/env python3
"""Read-only local issue audit for installed skills and plugin skill sources."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
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
        issues.append(issue(item, "DUPLICATE_EQUIVALENT_SOURCE", "info", "检测到内容一致的多个来源。", str(item.get("source_resolution_plan") or "按已安装来源优先级选择当前来源；等价副本不阻断使用。"), [str(path) for path in source_paths]))

    if item.get("inventory_scope") == "visible" and item.get("translation_quality") != "ready":
        issues.append(issue(item, "DESCRIPTION_NEEDS_REFINEMENT", "warning", "技能展示说明仍需人工精炼。", "按翻译质量规则生成候选，保留 ID 和 display_name 后回读验证。", [str(path) for path in source_paths]))

    for skill_path in skill_paths:
        meta = frontmatter(skill_path)
        missing = [field for field in ("name", "description") if not str(meta.get(field) or "").strip()]
        if missing:
            issues.append(issue(item, "METADATA_MISSING", "warning", "SKILL.md frontmatter 缺少: " + ", ".join(missing), "补齐 frontmatter；系统或插件来源通过上游包更新，不直接改 cache。", [str(skill_path)]))
        ui_path = skill_path.parent / "agents" / "openai.yaml"
        if not ui_path.exists():
            issues.append(issue(item, "UI_METADATA_FALLBACK", "info", "未找到 agents/openai.yaml，将回退到 SKILL.md frontmatter。", "用户 skill 可补充 UI metadata；系统/插件 skill 保持只读并通过上游发布更新。", [str(skill_path)]))
        text = skill_path.read_text(encoding="utf-8-sig", errors="replace")
        references = sorted(set(re.findall(r"(?:references|scripts|agents)/[A-Za-z0-9_.\-/]+", text)))
        for reference in references:
            cleaned = reference.rstrip(".,;:)")
            roots = [skill_path.parent, *list(skill_path.parents)[1:5]]
            candidates = [root / cleaned for root in roots]
            if not any(target.exists() for target in candidates):
                editable = bool(item.get("editable"))
                code = "REFERENCE_MISSING" if editable else "REFERENCE_UNRESOLVED_READONLY"
                severity = "warning" if editable else "info"
                message = f"技能引用不存在: {reference}" if editable else f"只读来源中的引用未在包内解析: {reference}"
                remediation = (
                    f"在 {skill_path.parent} 下补齐 {cleaned}，或修正 SKILL.md 中的相对引用；修后重新运行审查。"
                    if editable else
                    "记录为上游包问题；不要修改 cache，升级对应插件或系统技能后重新审查。"
                )
                issues.append(issue(item, code, severity, message, remediation, [str(skill_path), *[str(target) for target in candidates]]))
    return issues


def load_profile(profile_path: Path | None) -> tuple[str, str]:
    if profile_path is None or not profile_path.exists():
        return "", "unavailable"
    try:
        return profile_path.read_text(encoding="utf-8-sig", errors="replace"), "observed"
    except OSError:
        return "", "unavailable"


def terms(text: str) -> set[str]:
    result = {token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9+.-]{2,}", text)}
    stopwords = {"当前", "使用", "用于", "进行", "支持", "用户", "技能", "功能", "问题", "相关", "可以", "主要"}
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        if chunk not in stopwords:
            result.add(chunk)
        for size in (2, 3, 4):
            for index in range(0, len(chunk) - size + 1):
                token = chunk[index:index + size]
                if token not in stopwords:
                    result.add(token)
    return result


def item_terms(item: dict) -> set[str]:
    return terms(" ".join([
        str(item.get("id", "")),
        str(item.get("command_palette", {}).get("original", "")),
        str(item.get("sidebar", {}).get("original", "")),
        str(item.get("sidebar", {}).get("short_description", "")),
    ]))


def trigger_terms(item: dict) -> set[str]:
    description = str(item.get("sidebar", {}).get("short_description") or item.get("sidebar", {}).get("original", ""))
    trigger = description.split("→", 1)[0] if "→" in description else ""
    raw = "|".join([str(item.get("command_palette", {}).get("original", "")), trigger])
    extracted = {token.strip().lower() for token in re.split(r"[|/·、,;]+", raw) if len(token.strip()) >= 2}
    return extracted or terms(str(item.get("id", "")))


def capability_terms(item: dict) -> set[str]:
    description = str(item.get("sidebar", {}).get("short_description") or item.get("sidebar", {}).get("original", ""))
    capability = description.split("→", 1)[1] if "→" in description else description
    return terms(capability)


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
            "description": (6 if "DESCRIPTION_NEEDS_REFINEMENT" in codes else 10) if item.get("inventory_scope") == "visible" else None,
            "version": 10 if version_info(item)["status"] == "observed" else None,
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
    profile_map = {entry["id"]: set(entry["profile_alignment"].get("matched_terms", [])) for entry in scores}
    result: list[dict] = []
    counts = {"conflict": 0, "complementary": 0, "unrelated": 0}
    for index, left in enumerate(items):
        left_triggers = trigger_terms(left)
        left_capabilities = capability_terms(left)
        for right in items[index + 1:]:
            right_triggers = trigger_terms(right)
            right_capabilities = capability_terms(right)
            trigger_union = left_triggers | right_triggers
            trigger_overlap = left_triggers & right_triggers
            trigger_ratio = round(len(trigger_overlap) / len(trigger_union), 3) if trigger_union else 0.0
            generic_triggers = {"创建", "审查", "查询", "文档", "技能", "通用技能", "分析", "使用", "生成", "控制", "工具", "create", "review", "use"}
            def meaningful_contains(a: str, b: str) -> bool:
                shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
                if shorter in generic_triggers:
                    return False
                if re.fullmatch(r"[\u4e00-\u9fff]+", shorter):
                    return len(shorter) >= 3 and shorter in longer
                # Identifier substrings such as summarize/skills-summarize-audit or
                # figma-use/figma-use-motion are distinct invocation IDs, not trigger conflicts.
                return False
            contains_trigger = any(meaningful_contains(a, b) for a in left_triggers for b in right_triggers)
            if contains_trigger:
                trigger_ratio = max(trigger_ratio, 0.6)
            capability_union = left_capabilities | right_capabilities
            capability_overlap = left_capabilities & right_capabilities
            capability_ratio = round(len(capability_overlap) / len(capability_union), 3) if capability_union else 0.0
            complement_profile_terms = {"知识", "写作", "调研", "视频", "网页", "历史", "小说", "图像", "游戏", "投资", "安全", "测试", "自动化", "研究"}
            shared_profile = (profile_map.get(left["id"], set()) & profile_map.get(right["id"], set())) & complement_profile_terms
            if trigger_ratio >= 0.5:
                relationship = "conflict"
                reason = "触发词或描述高度重叠"
            elif trigger_ratio < 0.3 and capability_ratio <= 0.15 and shared_profile:
                relationship = "complementary"
                reason = "服务同一画像需求，但触发词与能力边界不同"
            else:
                relationship = "unrelated"
                reason = "当前证据不足以判定冲突或互补"
            counts[relationship] += 1
            if relationship != "unrelated":
                result.append({"left": left["id"], "right": right["id"], "relationship": relationship, "trigger_overlap": trigger_ratio, "capability_overlap": capability_ratio, "shared_profile_terms": sorted(shared_profile), "reason": reason})
    return result, counts


def recommendations(scores: list[dict], item_issues: list[dict], relationship_items: list[dict]) -> list[dict]:
    by_id: dict[str, list[dict]] = {}
    for entry in item_issues:
        by_id.setdefault(entry["id"], []).append(entry)
    result: list[dict] = []
    for scored in scores:
        entries = by_id.get(scored["id"], [])
        severities = {entry["severity"] for entry in entries}
        if "critical" in severities:
            decision, reason = "升级/修复", "存在 critical 来源或解析问题"
        elif "warning" in severities:
            decision, reason = "优化", "存在元数据或说明质量问题"
        elif scored["health_score"] >= 8 and (scored["profile_alignment"].get("score") or 0) > 0:
            decision, reason = "保留", "健康分达标且与用户画像有匹配证据"
        elif scored["health_score"] >= 8:
            decision, reason = "观察", "健康分达标但当前画像匹配证据不足"
        else:
            decision, reason = "观察", "健康分或证据不足，暂不做安装/归档结论"
        result.append({"target": scored["id"], "decision": decision, "reason": reason, "evidence": [entry["code"] for entry in entries]})
    for relation in relationship_items:
        if relation["relationship"] == "conflict":
            result.append({"target": f"{relation['left']} + {relation['right']}", "decision": "边界调整", "reason": relation["reason"], "evidence": [f"trigger_overlap={relation['trigger_overlap']}"]})
        elif relation["relationship"] == "complementary":
            result.append({"target": f"{relation['left']} + {relation['right']}", "decision": "共存", "reason": relation["reason"], "evidence": [f"capability_overlap={relation['capability_overlap']}", "shared_profile=" + ",".join(relation["shared_profile_terms"])]})
    return result


def bundle_name(item: dict) -> str:
    """Return the installed source group without treating cache entries as UI-visible skills."""
    paths = "|".join(str(path).replace("\\", "/") for path in item.get("source_paths", []))
    for name in ("openai-templates", "figma", "github", "browser", "computer-use", "visualize"):
        if f"/{name}/" in paths:
            return name
    if item.get("source_type") == "codex_runtime_plugin":
        return "runtime"
    if item.get("source_type") == "codex_system_skill":
        return "system"
    return "global"


def inventory_analysis(items: list[dict], scores: list[dict], recommendation_items: list[dict], profile_status: str) -> dict:
    """Summarize installed sources, suitability, and inferred pressure without claiming usage data."""
    score_by_id = {entry["id"]: entry for entry in scores}
    recommendation_by_id = {entry["target"]: entry for entry in recommendation_items if " + " not in entry["target"]}
    bundles: dict[str, list[dict]] = defaultdict(list)
    source_counts = Counter()
    decision_counts = Counter()
    repair_candidates = []
    for item in items:
        bundle = bundle_name(item)
        bundles[bundle].append(item)
        source_counts[item.get("source_type", "unavailable")] += 1
        score = score_by_id.get(item["id"], {})
        alignment = score.get("profile_alignment", {})
        fit_score = alignment.get("score")
        suitability = "unavailable" if alignment.get("status") != "observed" else ("高" if (fit_score or 0) >= 4 else "中" if (fit_score or 0) >= 2 else "低")
        decision = recommendation_by_id.get(item["id"], {}).get("decision", "观察")
        decision_counts[decision] += 1
        if decision in {"优化", "升级/修复"}:
            repair_candidates.append({
                "id": item["id"], "bundle": bundle, "source_type": item.get("source_type"),
                "health_score": score.get("health_score"), "suitability": suitability,
                "decision": decision, "usage": "unavailable",
            })
    bundle_rows = []
    candidates = list(repair_candidates)
    for name, members in sorted(bundles.items(), key=lambda entry: (-len(entry[1]), entry[0])):
        plugin_group = name not in {"global", "system", "runtime"}
        low_fit = 0
        for item in members:
            alignment = score_by_id.get(item["id"], {}).get("profile_alignment", {})
            if alignment.get("status") == "observed" and (alignment.get("score") or 0) == 0:
                low_fit += 1
        pressure = "高" if len(members) >= 12 else "中" if len(members) >= 5 else "低"
        advice = "保留" if not plugin_group else ("评估禁用/卸载" if len(members) >= 10 and low_fit * 2 >= len(members) else "按任务保留")
        bundle_rows.append({
            "bundle": name, "items": len(members), "source_types": sorted({item.get("source_type") for item in members}),
            "low_suitability_items": low_fit, "context_pressure": pressure,
            "pressure_status": "inferred", "advice": advice,
        })
        if advice == "评估禁用/卸载":
            candidates.append({
                "id": f"plugin:{name}", "bundle": name, "source_type": "plugin_bundle",
                "health_score": "-", "suitability": f"低适用 {low_fit}/{len(members)} 项",
                "decision": "评估禁用/卸载", "usage": "unavailable",
            })
    return {
        "usage_evidence": "unavailable: 未取得可归因的结构化 session/tool-call 事件",
        "profile_status": profile_status,
        "source_counts": dict(sorted(source_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "bundles": bundle_rows,
        "action_candidates": candidates,
        "context_pressure_note": "按安装项数量推断来源组的潜在发现/选择噪声；不等同于实际注入 prompt token。",
    }


def audit(root: Path, catalog_dir: Path, runtime_dir: Path, staging_dir: Path | None, user_skill_dir: Path | None, scope: str, visible_ids: list[str], profile_path: Path | None = None) -> tuple[dict, list[Path]]:
    items, watched = collect(root, catalog_dir, runtime_dir, staging_dir, user_skill_dir)
    selected = logical_items(items, scope, visible_ids if scope == "visible" else None)
    issues = [entry for item in selected for entry in audit_item(item)]
    profile_text, profile_status = load_profile(profile_path)
    scores = score_items(selected, issues, profile_text, profile_status)
    by_severity = {severity: sum(entry["severity"] == severity for entry in issues) for severity in ("critical", "warning", "info")}
    relationship_candidates = [item for item in selected if item.get("source_type") != "codex_plugin_manifest"]
    relationship_scores = [entry for entry in scores if any(item["id"] == entry["id"] for item in relationship_candidates)]
    relationship_items, relationship_counts = relationships(relationship_candidates, relationship_scores)
    recommendation_items = recommendations(scores, issues, relationship_items)
    inventory = inventory_analysis(selected, scores, recommendation_items, profile_status)
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
        "recommendations": recommendation_items,
        "inventory_analysis": inventory,
        "external_candidate_status": "unavailable: 未取得本次联网同意",
        "items": selected,
        "watched_source_count": len(watched),
    }
    return report, watched


def render_human_report(report: dict, detail: bool = False) -> str:
    """Render the compact, action-first terminal report; keep --json as the full contract."""
    summary = report["summary"]
    severities = summary["by_severity"]
    issues = report["issues"]
    actionable = [entry for entry in issues if entry["severity"] in {"critical", "warning"}]
    relationships = report["relationships"]
    inventory = report["inventory_analysis"]
    lines = [
        "技能/插件审查",
        f"状态: complete | 范围: {report['scope']} | 模式: {report['mode']}",
        f"结论: 扫描 {summary['items_scanned']} 项；需处理 {len(actionable)} 项（critical {severities['critical']} / warning {severities['warning']}）。",
        f"适用度: {inventory['profile_status']} | 使用频率: unavailable（未取得可归因调用证据）。",
    ]
    lines.extend(["", "安装全景", "| 来源组 | 项数 | 低适用项 | 上下文压力 | 建议 |", "| --- | ---: | ---: | --- | --- |"])
    for bundle in inventory["bundles"]:
        lines.append(f"| {bundle['bundle']} | {bundle['items']} | {bundle['low_suitability_items']} | {bundle['context_pressure']} (inferred) | {bundle['advice']} |")
    lines.extend(["", "评分与证据边界", "| 维度 | 含义 |", "| --- | --- |", "| 健康分 | 来源、元数据与版本可解析性；不代表常用或适用。 |", "| 适用度 | 仅按用户画像词命中计算；高/中/低为 observed，缺画像则 unavailable。 |", "| 使用频率 | " + inventory["usage_evidence"] + " |", "| 上下文压力 | " + inventory["context_pressure_note"] + " |"])
    if actionable:
        lines.extend(["", "需处理"])
        for index, entry in enumerate(actionable, 1):
            evidence = entry["evidence"][0] if entry["evidence"] else "unavailable"
            lines.extend([
                f"{index}. [{entry['severity'].upper()}] {entry['id']} - {entry['code']}",
                f"   问题: {entry['message']}",
                f"   证据: {evidence}",
                f"   建议: {entry['remediation']}",
            ])
    else:
        lines.extend(["", "需处理", "无。"])
    if relationships:
        lines.extend(["", "边界与协同"])
        for relation in relationships:
            overlap = relation["trigger_overlap"] if relation["relationship"] == "conflict" else relation["capability_overlap"]
            action = "明确触发边界" if relation["relationship"] == "conflict" else "保留并按能力分工"
            lines.append(f"- {relation['left']} + {relation['right']}: {relation['relationship']}（重叠 {overlap}）；{action}。")
    candidates = inventory["action_candidates"]
    lines.extend(["", "优化与卸载候选", "| 对象 | 来源组 | 健康 | 适用度 | 使用频率 | 建议 |", "| --- | --- | ---: | --- | --- | --- |"])
    if candidates:
        for candidate in candidates:
            decision = "先维修" if candidate["decision"] in {"优化", "升级/修复"} else "[需确认] 评估禁用/卸载"
            lines.append(f"| {candidate['id']} | {candidate['bundle']} | {candidate['health_score']} | {candidate['suitability']} | {candidate['usage']} | {decision} |")
    else:
        lines.append("| 无 | - | - | - | - | 无足够证据建议卸载。 |")
    if detail:
        score_by_id = {entry["id"]: entry for entry in report["skill_scores"]}
        recommendation_by_id = {entry["target"]: entry for entry in report["recommendations"] if " + " not in entry["target"]}
        lines.extend(["", "完整安装清单", "| 技能/插件 | 来源组 | 健康 | 适用度 | 使用频率 | 决策 |", "| --- | --- | ---: | --- | --- | --- |"])
        for item in sorted(report["items"], key=lambda value: (bundle_name(value), value["id"])):
            score = score_by_id.get(item["id"], {})
            alignment = score.get("profile_alignment", {})
            fit = alignment.get("score")
            suitability = "unavailable" if alignment.get("status") != "observed" else ("高" if (fit or 0) >= 4 else "中" if (fit or 0) >= 2 else "低")
            decision = recommendation_by_id.get(item["id"], {}).get("decision", "观察")
            lines.append(f"| {item['id']} | {bundle_name(item)} | {score.get('health_score')} | {suitability} | unavailable | {decision} |")
    unavailable = []
    if report["profile"]["status"] != "observed":
        unavailable.append("用户画像")
    if report["external_candidate_status"].startswith("unavailable"):
        unavailable.append("外部候选数据")
    if unavailable:
        lines.extend(["", "未获取数据", "、".join(unavailable) + "；未用默认值补齐。"])
    info_count = severities["info"]
    if info_count:
        lines.extend(["", f"附注: 已折叠 {info_count} 条非阻断提示；使用 --json 查看完整证据。"])
    return "\n".join(lines)


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
    parser.add_argument("--detail", action="store_true", help="人类可读输出中包含每项安装资产；默认只显示来源组和行动候选。")
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
        print(render_human_report(report, args.detail))
    order = {"info": 1, "warning": 2, "critical": 3, "none": 0}
    if args.fail_on != "none" and any(order[entry["severity"]] >= order[args.fail_on] for entry in report["issues"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
