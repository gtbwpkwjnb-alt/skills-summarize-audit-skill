#!/usr/bin/env python3
"""Collect read-only Simplified Chinese candidates for Codex skill UI text."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # The parser still supports the small UI metadata subset below.
    yaml = None

DISPLAY_MAX = 24
SHORT_MAX = 40
LONG_MAX = 80
GLOSSARY_PATH = Path(__file__).resolve().parent.parent / "references" / "codex-ui-zh-glossary.json"
INSTALLED_SOURCE_TYPES = {"codex_global_skill", "codex_system_skill", "codex_plugin_cache", "codex_runtime_plugin", "codex_plugin_manifest"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def glossary() -> dict:
    data = json.loads(read_text(GLOSSARY_PATH))
    if not isinstance(data.get("phrases"), dict) or not isinstance(data.get("words"), dict) or not isinstance(data.get("skill_overrides"), dict):
        raise ValueError("术语库缺少 phrases、words 或 skill_overrides")
    return data


GLOSSARY = glossary()


def yaml_subset(path: Path) -> dict:
    """Load UI metadata without requiring PyYAML at runtime."""
    text = read_text(path)
    if yaml:
        try:
            value = yaml.safe_load(text)
            return value if isinstance(value, dict) else {}
        except yaml.YAMLError:
            pass
    result: dict[str, object] = {}
    interface: dict[str, str] = {}
    for key in ("display_name", "short_description", "long_description"):
        match = re.search(rf"^\s*{key}:\s*[\"']?(.+?)[\"']?\s*$", text, re.M)
        if match:
            interface[key] = match.group(1).strip()
    if interface:
        result["interface"] = interface
    return result


def frontmatter(path: Path) -> dict:
    text = read_text(path)
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not match:
        return {}
    if yaml:
        try:
            value = yaml.safe_load(match.group(1))
            return value if isinstance(value, dict) else {}
        except yaml.YAMLError:
            pass
    value = {}
    for key in ("name", "description"):
        item = re.search(rf"^{key}:\s*[\"']?(.+?)[\"']?\s*$", match.group(1), re.M)
        if item:
            value[key] = item.group(1).strip()
    return value


def compact(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def chinese_candidate(value: str, limit: int, fallback: str) -> tuple[str, str]:
    """Create a conservative candidate; unrecognized prose is flagged for agent refinement."""
    value = re.sub(r"\bUse when\b.*", "", value, flags=re.I).strip()
    if re.search(r"[\u4e00-\u9fff]", value):
        return compact(value, limit), "source_chinese"
    normalized = re.sub(r"[.?!]+$", "", value).lower().strip()
    phrase = GLOSSARY["phrases"].get(normalized)
    if phrase:
        return compact(str(phrase), limit), "glossary_exact"
    words = re.findall(r"[A-Za-z0-9+.#]+", value)
    word_map = GLOSSARY["words"]
    translated = [word_map[word.lower()] for word in words if word.lower() in word_map]
    result = "".join(translated)
    if not re.search(r"[\u4e00-\u9fff]", result):
        result = "通用技能"
    return compact(result, limit), "glossary_partial_needs_refinement"


def translated_fields(command: str, sidebar: str, long: str, fallback: str, skill_id: str) -> dict:
    override = GLOSSARY["skill_overrides"].get(skill_id, {})
    if override:
        display_name = compact(str(override["display_name"]), DISPLAY_MAX)
        short_description = compact(str(override["short_description"]), SHORT_MAX)
        display_method = short_method = "skill_override"
    else:
        display_name, display_method = chinese_candidate(command, DISPLAY_MAX, fallback)
        short_description, short_method = chinese_candidate(sidebar, SHORT_MAX, fallback)
    long_description, long_method = chinese_candidate(long, LONG_MAX, fallback)
    core_methods = {display_method, short_method}
    quality = "ready" if core_methods <= {"source_chinese", "glossary_exact", "skill_override"} else "needs_agent_refinement"
    return {
        "translation_quality": quality,
        "translation_methods": sorted({display_method, short_method, long_method}),
        "long_description_quality": "ready" if long_method in {"source_chinese", "glossary_exact"} else "needs_agent_refinement",
        "command_palette": {"original": command, "display_name": display_name},
        "sidebar": {"original": sidebar, "short_description": short_description, "long_original": long, "long_description": long_description},
    }


def source_hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def skill_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        p for p in root.rglob("SKILL.md")
        if ".archived" not in p.parts and ".archived" not in str(p).lower()
    )


def candidate_from_skill(path: Path, source_type: str, editable: bool) -> tuple[dict, list[Path]]:
    meta = frontmatter(path)
    skill_id = str(meta.get("name") or path.parent.name)
    description = str(meta.get("description") or "")
    ui_path = path.parent / "agents" / "openai.yaml"
    ui = yaml_subset(ui_path).get("interface", {}) if ui_path.exists() else {}
    ui = ui if isinstance(ui, dict) else {}
    command_original = str(ui.get("display_name") or skill_id)
    sidebar_original = str(ui.get("short_description") or description or command_original)
    long_original = str(ui.get("long_description") or description or sidebar_original)
    paths = [path] + ([ui_path] if ui_path.exists() else [])
    translated = translated_fields(command_original, sidebar_original, long_original, description or skill_id, skill_id)
    return ({
        "id": skill_id, "source_paths": [str(p.resolve()) for p in paths],
        "source_type": source_type, "inventory_scope": "installed", "editable": editable, "only_list": True,
        "fact_status": "observed", **translated,
    }, paths)


def catalog_candidates(catalog: Path) -> tuple[list[dict], list[Path]]:
    try:
        data = json.loads(read_text(catalog))
    except (OSError, json.JSONDecodeError) as exc:
        return ([{"id": catalog.name, "source_paths": [str(catalog.resolve())], "source_type": "remote_plugin_catalog",
                  "editable": False, "only_list": True, "fact_status": "unavailable", "error": str(exc)}], [catalog])
    items = []
    for plugin in data.get("plugins", []):
        release = plugin.get("release", {}) if isinstance(plugin, dict) else {}
        for skill in release.get("skills", []) or []:
            if not isinstance(skill, dict):
                continue
            interface = skill.get("interface", {}) if isinstance(skill.get("interface"), dict) else {}
            skill_id = str(skill.get("name") or "unknown-skill")
            command = str(interface.get("display_name") or skill_id)
            sidebar = str(interface.get("short_description") or skill.get("description") or command)
            long = str(skill.get("description") or sidebar)
            translated = translated_fields(command, sidebar, long, skill_id, skill_id)
            items.append({
                "id": skill_id, "plugin": plugin.get("name"), "source_paths": [str(catalog.resolve())],
                "source_type": "remote_plugin_catalog", "inventory_scope": "catalog_only", "editable": False, "only_list": True,
                "fact_status": "observed", **translated,
            })
    return items, [catalog]


def manifest_candidates(root: Path) -> tuple[list[dict], list[Path]]:
    """Collect installed Codex plugin-card UI metadata from plugin.json interfaces."""
    items: list[dict] = []
    manifests = sorted(root.rglob(".codex-plugin/plugin.json")) if root.exists() else []
    for manifest in manifests:
        try:
            data = json.loads(read_text(manifest))
        except (OSError, json.JSONDecodeError) as exc:
            items.append({
                "id": manifest.parent.parent.name, "source_paths": [str(manifest.resolve())],
                "source_type": "codex_plugin_manifest", "inventory_scope": "installed", "editable": False,
                "only_list": True, "fact_status": "unavailable", "error": str(exc),
            })
            continue
        interface = data.get("interface", {}) if isinstance(data.get("interface"), dict) else {}
        plugin_id = str(data.get("name") or manifest.parent.parent.name)
        command = str(interface.get("displayName") or plugin_id)
        sidebar = str(interface.get("shortDescription") or data.get("description") or command)
        long = str(interface.get("longDescription") or data.get("description") or sidebar)
        translated = translated_fields(command, sidebar, long, plugin_id, f"plugin:{plugin_id}")
        items.append({
            "id": f"plugin:{plugin_id}", "plugin": plugin_id, "source_paths": [str(manifest.resolve())],
            "source_type": "codex_plugin_manifest", "inventory_scope": "installed", "editable": False,
            "only_list": True, "fact_status": "observed", **translated,
        })
    return items, manifests


def watched_source_files(root: Path, catalog_dir: Path, runtime_dir: Path) -> list[Path]:
    """Discover every file the collector may read before parsing any metadata."""
    files: list[Path] = []
    for location in (root / "skills", root / "plugins" / "cache", runtime_dir):
        for skill in skill_files(location):
            files.append(skill)
            ui_path = skill.parent / "agents" / "openai.yaml"
            if ui_path.exists():
                files.append(ui_path)
            manifest = next(
                (parent / ".codex-plugin" / "plugin.json" for parent in [skill.parent, *skill.parents]
                 if (parent / ".codex-plugin" / "plugin.json").exists()),
                None,
            )
            if manifest:
                files.append(manifest)
    if catalog_dir.exists():
        files.extend(catalog_dir.glob("*.json"))
    files.extend((root / "plugins" / "cache").rglob(".codex-plugin/plugin.json"))
    return sorted(set(files))


def collect(root: Path, catalog_dir: Path, runtime_dir: Path) -> tuple[list[dict], list[Path]]:
    candidates: list[dict] = []
    watched: list[Path] = []
    groups = [
        (root / "skills", "codex_global_skill", True),
        (root / "plugins" / "cache", "codex_plugin_cache", False),
        (runtime_dir, "codex_runtime_plugin", False),
    ]
    seen: set[Path] = set()
    for location, source_type, editable in groups:
        for path in skill_files(location):
            if path in seen:
                continue
            seen.add(path)
            item_editable = editable and ".system" not in path.parts
            item, paths = candidate_from_skill(path, source_type, item_editable)
            if source_type == "codex_global_skill" and not item_editable:
                item["source_type"] = "codex_system_skill"
            candidates.append(item)
            watched.extend(paths)
            manifest = next((parent / ".codex-plugin" / "plugin.json" for parent in [path.parent, *path.parents] if (parent / ".codex-plugin" / "plugin.json").exists()), None)
            if manifest:
                watched.append(manifest)
                item["plugin_manifest"] = str(manifest.resolve())
    if catalog_dir.exists():
        for catalog in sorted(catalog_dir.glob("*.json")):
            items, paths = catalog_candidates(catalog)
            candidates.extend(items)
            watched.extend(paths)
    manifest_items, manifests = manifest_candidates(root / "plugins" / "cache")
    candidates.extend(manifest_items)
    watched.extend(manifests)
    return candidates, sorted(set(watched))


def logical_items(items: list[dict], scope: str) -> list[dict]:
    """Filter the requested inventory scope and de-duplicate installed UI entries."""
    if scope == "installed":
        selected = [item for item in items if item["source_type"] in INSTALLED_SOURCE_TYPES]
    elif scope == "catalog":
        selected = [item for item in items if item["source_type"] == "remote_plugin_catalog"]
    else:
        return items
    unique: dict[str, dict] = {}
    for item in selected:
        # Prefer a normal cache directory, then the highest discovered version, then newest metadata.
        existing = unique.get(item["id"])
        if existing is None or candidate_rank(item) > candidate_rank(existing):
            unique[item["id"]] = item
    for item in unique.values():
        item["selection_reason"] = "highest_non_temporary_cache_version"
    return list(unique.values())


def candidate_rank(item: dict) -> tuple:
    paths = [Path(value) for value in item.get("source_paths", [])]
    temporary = any(part.startswith("plugin-install-") for path in paths for part in path.parts)
    versions: list[tuple[int, ...]] = []
    newest_mtime = 0.0
    for path in paths:
        for part in path.parts:
            numbers = re.findall(r"\d+", part)
            if numbers and ("." in part or "-" in part):
                versions.append(tuple(int(number) for number in numbers))
        try:
            newest_mtime = max(newest_mtime, path.stat().st_mtime)
        except OSError:
            pass
    return (not temporary, max(versions, default=()), newest_mtime)


def inventory_summary(items: list[dict]) -> dict:
    installed = [item for item in items if item["source_type"] in INSTALLED_SOURCE_TYPES]
    catalog = [item for item in items if item["source_type"] == "remote_plugin_catalog"]
    installed_unique = logical_items(items, "installed")
    installed_ids = {item["id"] for item in installed_unique}
    for item in catalog:
        item["matches_installed_id"] = item["id"] in installed_ids
    return {
        "installed_source_records": len(installed),
        "installed_unique_items": len(installed_unique),
        "installed_ready": sum(item["translation_quality"] == "ready" for item in installed_unique),
        "installed_needs_agent_refinement": sum(item["translation_quality"] == "needs_agent_refinement" for item in installed_unique),
        "catalog_only_source_records": len(catalog),
        "catalog_matches_installed_id": sum(item["matches_installed_id"] for item in catalog),
        "note": "remote_plugin_catalog 是可发现市场项；不计入已安装健康度或 P1 翻译积压。",
    }


def markdown(items: list[dict], scope: str) -> str:
    lines = [f"## Codex 命令栏与侧边栏中文翻译清单（{scope}，{len(items)} 项）", "", "仅清单，不写入 Codex UI、插件缓存或技能触发逻辑。", "",
             "| 标识 | 命令栏原文 | 中文候选 | 侧边栏原文 | 中文候选 | 来源 | 状态 |", "|---|---|---|---|---|---|---|"]
    for item in items:
        if item.get("fact_status") != "observed":
            continue
        lines.append("| {id} | {co} | {cc} | {so} | {sc} | {source} | observed / {quality} / 只读 |".format(
            id=item["id"], co=item["command_palette"]["original"], cc=item["command_palette"]["display_name"],
            so=item["sidebar"]["original"], sc=item["sidebar"]["short_description"], source=item["source_type"], quality=item["translation_quality"]))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect read-only Codex Chinese UI candidates.")
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    parser.add_argument("--catalog-dir", type=Path)
    parser.add_argument("--runtime-dir", type=Path, default=Path.home() / ".cache" / "codex-runtimes")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--check-unchanged", action="store_true")
    parser.add_argument("--scope", choices=("installed", "catalog", "all"), default="all")
    parser.add_argument("--batch-size", type=int, default=0, help="Limit the emitted scope items for P1 refinement batches.")
    parser.add_argument("--offset", type=int, default=0, help="Zero-based offset used with --batch-size.")
    args = parser.parse_args()
    catalog_dir = args.catalog_dir or args.root / "cache" / "remote_plugin_catalog"
    watched = watched_source_files(args.root, catalog_dir, args.runtime_dir)
    before = source_hashes(watched) if args.check_unchanged else {}
    items, _ = collect(args.root, catalog_dir, args.runtime_dir)
    # Formatting happens after collection; this script intentionally has no write path.
    summary = inventory_summary(items)
    scoped_items = logical_items(items, args.scope)
    if args.batch_size < 0 or args.offset < 0:
        parser.error("--batch-size and --offset must be non-negative")
    if args.batch_size:
        scoped_items = scoped_items[args.offset: args.offset + args.batch_size]
    output = {
        "mode": "read_only", "only_list": True, "scope": args.scope,
        "inventory_summary": summary, "items": scoped_items,
        "batch": {"offset": args.offset, "size": args.batch_size or None},
        "watched_source_count": len(watched),
    }
    after = source_hashes(watched) if args.check_unchanged else {}
    if args.check_unchanged and before != after:
        print("扫描源 SHA256 在运行期间变化", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(markdown(scoped_items, args.scope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
