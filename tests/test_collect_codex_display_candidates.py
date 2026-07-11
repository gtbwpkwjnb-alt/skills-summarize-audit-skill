#!/usr/bin/env python3
"""Fixture tests for the read-only Codex display candidate collector."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "codex-display"
SCRIPT = ROOT / "scripts" / "collect_codex_display_candidates.py"

spec = importlib.util.spec_from_file_location("collector", SCRIPT)
collector = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(collector)


def hashes():
    return {str(p.relative_to(FIXTURE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in FIXTURE.rglob("*") if p.is_file()}


def main():
    before = hashes()
    items, watched = collector.collect(FIXTURE, FIXTURE / "remote_plugin_catalog", FIXTURE / "missing-runtime")
    after = hashes()
    assert before == after, "只读采集器修改了 fixture"
    assert watched, "未记录扫描源"
    by_type = {item["source_type"]: item for item in items if item["fact_status"] == "observed"}
    for source in ("codex_global_skill", "codex_plugin_cache", "codex_plugin_manifest", "remote_plugin_catalog"):
        assert source in by_type, f"缺少来源 {source}"
        item = by_type[source]
        assert item["only_list"] is True
        if source != "codex_global_skill":
            assert item["editable"] is False
        assert item["command_palette"]["original"] and item["sidebar"]["original"]
        assert any("\u4e00" <= char <= "\u9fff" for char in item["command_palette"]["display_name"])
        assert any("\u4e00" <= char <= "\u9fff" for char in item["sidebar"]["short_description"])
        assert len(item["command_palette"]["display_name"]) <= collector.DISPLAY_MAX
        assert len(item["sidebar"]["short_description"]) <= collector.SHORT_MAX
        assert len(item["sidebar"]["long_description"]) <= collector.LONG_MAX
    assert by_type["codex_global_skill"]["sidebar"]["short_description"] == "基于审核证据生成业务决策报告"
    assert by_type["codex_plugin_cache"]["sidebar"]["short_description"] == "分析或发布前评估表格与数据集"
    assert by_type["remote_plugin_catalog"]["sidebar"]["short_description"] == "创建有依据的产品指标仪表板"
    assert by_type["remote_plugin_catalog"]["translation_quality"] == "ready"
    assert by_type["remote_plugin_catalog"]["long_description_quality"] == "ready"
    assert by_type["remote_plugin_catalog"]["sidebar"]["long_original"] == "Build dashboards for product metrics."
    summary = collector.inventory_summary(items)
    assert by_type["codex_plugin_manifest"]["command_palette"]["display_name"] == "插件"
    assert by_type["codex_plugin_manifest"]["sidebar"]["short_description"] == "创建可复用工件模板"
    assert summary["installed_unique_items"] == 3
    assert summary["catalog_only_source_records"] == 1
    assert len(collector.logical_items(items, "installed")) == 3
    assert len(collector.logical_items(items, "catalog")) == 1
    selected_plugin = next(item for item in collector.logical_items(items, "installed") if item["id"] == "fixture-plugin")
    assert "1.0.0" in selected_plugin["source_paths"][0]
    assert selected_plugin["selection_reason"] == "highest_non_temporary_cache_version"
    installed_markdown = collector.markdown(collector.logical_items(items, "installed"), "installed")
    assert "fixture-catalog" not in installed_markdown
    assert "（installed，3 项）" in installed_markdown
    assert collector.GLOSSARY["skill_overrides"]["imagegen"]["display_name"] == "图像生成"
    print(json.dumps({"result": "passed", "candidate_count": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
