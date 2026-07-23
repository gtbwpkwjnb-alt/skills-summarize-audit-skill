#!/usr/bin/env python3
"""Bounded, read-only project fingerprint and recommendation scanner."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by environment setup
    raise SystemExit("PyYAML is required for project profile scanning") from exc


ROOT = Path(__file__).resolve().parent.parent
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "dist", "build", ".next", "target", "vendor",
    "fixture-data", "fixtures", ".audit-snapshots", ".tmp", "tmp", "backups", "archives",
    "archived_sessions", "sessions", "worktrees", ".archived", "memories", "snapshots",
}
IGNORE_FILES = {"tech-fingerprints.yaml", "project-types.yaml"}


def iter_files(project: Path, max_files: int, max_depth: int) -> tuple[list[Path], bool]:
    found: list[Path] = []
    if not project.exists():
        return found, False
    for current, directories, files in os.walk(project, topdown=True, followlinks=False):
        base = Path(current)
        depth = len(base.relative_to(project).parts)
        directories[:] = [name for name in directories if name not in IGNORE_DIRS and not (base / name).is_symlink() and depth < max_depth]
        for name in files:
            path = base / name
            if path.is_file() and name not in IGNORE_FILES:
                found.append(path)
                if len(found) >= max_files:
                    return found, True
    return found, False


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return yaml.safe_load(handle)


def matching_files(files: list[Path], project: Path, patterns: list[str]) -> list[Path]:
    return [path for path in files if any(path.relative_to(project).match(pattern) for pattern in patterns)]


def package_version(project: Path, tech: dict) -> str | None:
    probe = tech.get("version_probe") or {}
    if probe.get("file") != "package.json":
        return None
    package = project / "package.json"
    if not package.exists():
        return None
    try:
        data = json.loads(package.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    dependency = str(probe.get("jsonpath", "")).split(".")[-1]
    return (data.get("dependencies") or {}).get(dependency) or (data.get("devDependencies") or {}).get(dependency)


def detect(project: Path, max_files: int = 2000, max_depth: int = 10) -> dict:
    files, truncated = iter_files(project, max_files, max_depth)
    database = load_yaml(ROOT / "references" / "tech-fingerprints.yaml")
    detected: list[dict] = []
    fingerprint_errors: list[dict] = []
    for category, entries in database.items():
        if not isinstance(entries, list):
            continue
        for tech in entries:
            if not isinstance(tech, dict):
                continue
            evidence: list[dict] = []
            for fingerprint in tech.get("fingerprints", []) or []:
                candidates = matching_files(files, project, fingerprint.get("files", []) or [])
                pattern = fingerprint.get("contents")
                if pattern:
                    pattern = str(pattern).replace("\\\\", "\\")
                    try:
                        compiled = re.compile(pattern)
                    except re.error as exc:
                        fingerprint_errors.append({"technology": tech.get("id"), "pattern": pattern, "error": str(exc)})
                        candidates = []
                    else:
                        candidates = [path for path in candidates if compiled.search(path.read_text(encoding="utf-8", errors="ignore"))]
                for path in candidates[:8]:
                    evidence.append({"path": str(path.relative_to(project)), "confidence": fingerprint.get("confidence", "low")})
            if evidence:
                rank = {"high": 3, "medium": 2, "low": 1}
                confidence = max(evidence, key=lambda item: rank.get(item["confidence"], 0))["confidence"]
                detected.append({"id": tech.get("id"), "name": tech.get("name"), "category": tech.get("category", category), "confidence": confidence, "version": package_version(project, tech), "evidence": evidence, "tags": tech.get("tags", [])})
    ids = {item["id"] for item in detected}
    types: list[dict] = []
    for rule in (database.get("matching_rules", {}).get("project_type_inference", []) or []):
        matched = [tech_id for tech_id in rule.get("when_any", []) if tech_id in ids]
        if matched:
            types.append({"type": rule.get("then_type"), "confidence": rule.get("confidence"), "based_on": matched})

    project_types = load_yaml(ROOT / "references" / "project-types.yaml") or []
    recommendations: list[dict] = []
    package_data = {}
    package_path = project / "package.json"
    if package_path.exists():
        try:
            package_data = json.loads(package_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            package_data = {}
    dependencies = set((package_data.get("dependencies") or {})) | set((package_data.get("devDependencies") or {}))
    matched_recommendations = 0
    for entry in project_types:
        pattern = entry.get("pattern", {}) if isinstance(entry, dict) else {}
        if pattern.get("fallback"):
            continue
        checks: list[bool] = []
        evidence: list[str] = []
        file_patterns = pattern.get("files", []) or []
        if file_patterns:
            matched = matching_files(files, project, file_patterns)
            checks.append(bool(matched))
            evidence.extend(str(path.relative_to(project)) for path in matched[:8])
        contained_patterns = pattern.get("contains_files", []) or []
        if contained_patterns:
            matched = matching_files(files, project, contained_patterns)
            minimum = int(pattern.get("count_min", 1))
            checks.append(len(matched) >= minimum)
            evidence.extend(str(path.relative_to(project)) for path in matched[:8])
        contained_dirs = pattern.get("contains_dirs", []) or []
        if contained_dirs:
            found_dirs = [name for name in contained_dirs if (project / name).is_dir()]
            checks.append(len(found_dirs) == len(contained_dirs))
            evidence.extend(found_dirs)
        required = set(pattern.get("contains_deps", []) or [])
        if required:
            checks.append(required <= dependencies)
            if required <= dependencies:
                evidence.append("package.json dependencies: " + ", ".join(sorted(required)))
        if checks and all(checks):
            recommendations.append({"project_type": entry.get("type"), "description": entry.get("description"), "skills": entry.get("skills", []), "evidence": list(dict.fromkeys(evidence))})
            matched_recommendations += 1

    if not matched_recommendations:
        fallback = next((entry for entry in project_types if isinstance(entry, dict) and (entry.get("pattern") or {}).get("fallback")), None)
        if fallback:
            recommendations.append({"project_type": fallback.get("type"), "description": fallback.get("description"), "skills": fallback.get("skills", []), "evidence": ["未命中更具体的 project-types 规则"]})
    merged_recommendations: dict[str, dict] = {}
    for recommendation in recommendations:
        project_type = str(recommendation.get("project_type"))
        existing = merged_recommendations.get(project_type)
        if existing is None:
            merged_recommendations[project_type] = recommendation
            continue
        existing["evidence"] = list(dict.fromkeys([*existing.get("evidence", []), *recommendation.get("evidence", [])]))
        existing_skills = {str(skill.get("name")): skill for skill in existing.get("skills", []) if isinstance(skill, dict)}
        for skill in recommendation.get("skills", []):
            if isinstance(skill, dict):
                existing_skills.setdefault(str(skill.get("name")), skill)
        existing["skills"] = list(existing_skills.values())
    recommendations = list(merged_recommendations.values())
    return {"schema_version": 1, "mode": "read_only", "project": str(project.resolve()), "limits": {"max_files": max_files, "max_depth": max_depth, "files_scanned": len(files), "truncated": truncated}, "detected_technologies": detected, "inferred_project_types": types, "recommendations": recommendations, "fingerprint_errors": fingerprint_errors, "fact_status": "observed"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan project technology fingerprints without writing files.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--max-files", type=int, default=2000)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = detect(args.project, args.max_files, args.max_depth)
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"项目画像：{report['project']}；扫描 {report['limits']['files_scanned']} 个文件，识别 {len(report['detected_technologies'])} 项技术")
        for tech in report["detected_technologies"]:
            print(f"- {tech['name']} [{tech['confidence']}] version={tech['version'] or 'unavailable'}")
        for recommendation in report["recommendations"]:
            print(f"推荐技能组：{recommendation['project_type']} ({len(recommendation['skills'])} 项)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
