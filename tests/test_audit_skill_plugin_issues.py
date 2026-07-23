#!/usr/bin/env python3
"""Fixture tests for read-only skill/plugin issue discovery."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_SOURCE = ROOT / "tests" / "fixture-data" / "codex-display"
FIXTURE = Path(tempfile.mkdtemp(prefix="codex-issue-audit-")) / "codex-display"
shutil.copytree(FIXTURE_SOURCE, FIXTURE)
for source in FIXTURE.rglob("SKILL.fixture.md"):
    source.rename(source.with_name("SKILL.md"))
SCRIPT = ROOT / "scripts" / "audit_skill_plugin_issues.py"
spec = importlib.util.spec_from_file_location("issue_audit", SCRIPT)
audit_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(audit_module)


def main() -> None:
    report, watched = audit_module.audit(
        FIXTURE,
        FIXTURE / "remote_plugin_catalog",
        FIXTURE / "missing-runtime",
        None,
        FIXTURE / "missing-user-skills",
        "installed",
        [],
    )
    assert watched
    assert report["mode"] == "read_only"
    assert report["summary"]["items_scanned"] == 3
    assert len(report["skill_scores"]) == 3
    assert set(report["relationship_counts"]) == {"conflict", "complementary", "unrelated"}
    assert report["profile"]["status"] == "unavailable"
    codes = {entry["code"] for entry in report["issues"]}
    assert "SOURCE_DIVERGENCE" in codes
    assert "DESCRIPTION_NEEDS_REFINEMENT" in codes or report["summary"]["issues"] > 0
    divergent = next(entry for entry in report["issues"] if entry["code"] == "SOURCE_DIVERGENCE")
    assert "确认" in divergent["remediation"]
    print(json.dumps({"result": "passed", "issue_count": report["summary"]["issues"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
