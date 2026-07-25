"""
compute_value_scores.py — v9.0.0 修复 B3：实现 ecosystem-optimization.md 的 value_score 计算

独立模块，供 audit_skill_plugin_issues.py 的 audit_ecosystem 调用。
计算每个 skill/mcp/agent 的综合价值分，输出保留/观察/隐藏/卸载分层建议。
"""
from __future__ import annotations

from typing import Iterable


def normalize_usage(raw_count: int, max_count: int) -> float:
    """归一化到 0-10。"""
    if max_count <= 0:
        return 0.0
    return min(10.0, (raw_count / max_count) * 10)


def value_score(usage: float, alignment: float, health: float, market: float = 0.0) -> float:
    """
    综合价值分（0-10）。
    权重见 ecosystem-optimization.md §2。
    """
    return round(
        usage * 0.40 + alignment * 0.25 + health * 0.20 + market * 0.15,
        2,
    )


def confidence_level(has_local_usage: bool, has_market: bool, has_alignment: bool) -> str:
    """返回 high/medium/low。"""
    if has_local_usage:
        return "high"
    if has_market or has_alignment:
        return "medium"
    return "low"


def recommendation_layer(score: float) -> str:
    """分层建议。"""
    if score >= 7.0:
        return "keep"
    if score >= 4.0:
        return "watch"
    if score >= 2.0:
        return "hide"
    return "uninstall_candidate"


def assess_skills_optimization(
    skill_scores: list[dict],
    skill_usage: dict[str, dict],
) -> list[dict]:
    """
    计算 skill 层的配置优化建议。
    skill_scores: 来自 audit() 的 skill_scores 字段
    skill_usage: 来自 extract_usage_signals.py 的 skill_invocation_evidence
    """
    # 找出最大使用次数用于归一化
    max_usage = max((u.get("invocations", 0) for u in skill_usage.values()), default=0)
    usage_by_id = {k: v.get("invocations", 0) for k, v in skill_usage.items()}

    results = []
    for s in skill_scores:
        sid = s.get("id", "")
        usage_raw = usage_by_id.get(sid, 0)
        usage_norm = normalize_usage(usage_raw, max_usage) if max_usage > 0 else 0.0
        alignment = (s.get("profile_alignment") or {}).get("score", 0) or 0
        health = s.get("health_score", 0) or 0
        # market 暂为 0（联网补全由用户 Agent 执行）
        market = 0.0
        score = value_score(usage_norm, alignment, health, market)
        layer = recommendation_layer(score)
        conf = confidence_level(
            has_local_usage=usage_raw > 0,
            has_market=False,
            has_alignment=alignment > 0,
        )
        results.append({
            "target": sid,
            "type": "skill",
            "value_score": score,
            "layer": layer,
            "confidence": conf,
            "breakdown": {
                "usage": round(usage_norm, 2),
                "alignment": round(alignment, 2),
                "health": round(health, 2),
                "market": round(market, 2),
            },
            "evidence": {
                "usage_count": usage_raw,
                "has_local_evidence": usage_raw > 0,
                "market_evidence": "unavailable (需用户 Agent 联网补全)",
            },
        })
    results.sort(key=lambda x: x["value_score"], reverse=True)
    return results


def assess_mcp_optimization(
    mcp_health: list[dict],
    mcp_usage: list[dict],
) -> list[dict]:
    """计算 MCP 层的配置优化建议。"""
    usage_by_server = {m["mcp_server"]: m.get("tool_calls", 0) for m in mcp_usage}
    max_usage = max(usage_by_server.values(), default=0)

    results = []
    for m in mcp_health:
        server = m["server"]
        usage_raw = usage_by_server.get(server, 0)
        usage_norm = normalize_usage(usage_raw, max_usage) if max_usage > 0 else 0.0
        health = m.get("health_score", 0)
        # alignment 暂用 health 近似（MCP 没有画像匹配）
        alignment = health * 0.5
        market = 0.0
        score = value_score(usage_norm, alignment, health, market)
        layer = recommendation_layer(score)
        # 对 MCP 卸载建议特别谨慎：必须 [需确认]
        if layer == "uninstall_candidate":
            layer = "hide_review"  # 降级为隐藏并复查
        conf = confidence_level(
            has_local_usage=usage_raw > 0,
            has_market=False,
            has_alignment=False,
        )
        results.append({
            "target": server,
            "type": "mcp",
            "value_score": score,
            "layer": layer,
            "confidence": conf,
            "breakdown": {
                "usage": round(usage_norm, 2),
                "alignment": round(alignment, 2),
                "health": round(health, 2),
                "market": round(market, 2),
            },
            "evidence": {
                "usage_count": usage_raw,
                "has_local_evidence": usage_raw > 0,
                "market_evidence": "unavailable (需用户 Agent 联网补全)",
            },
        })
    results.sort(key=lambda x: x["value_score"], reverse=True)
    return results


def ecosystem_optimization_summary(
    skill_recs: list[dict],
    mcp_recs: list[dict],
) -> dict:
    """汇总三层建议数量。"""
    def count(items, layer):
        return sum(1 for i in items if i["layer"] == layer)

    all_recs = skill_recs + mcp_recs
    return {
        "total_tools": len(all_recs),
        "keep": count(all_recs, "keep"),
        "watch": count(all_recs, "watch"),
        "hide": count(all_recs, "hide") + count(all_recs, "hide_review"),
        "uninstall_candidates": count(all_recs, "uninstall_candidate"),
        "data_gaps": [
            "market_signal 全部为 0：需用户 Agent 通过 firecrawl/rival-search 联网补全（参考 mcp-marketplaces.md URL 模板）",
            "MCP 调用证据仅来自 ZCode transcript；用户在 Codex/Claude Code 中的调用未计入",
            "skill_invocation_evidence 仅捕获显式 Skill tool 调用；通过其他路径触发的技能未计入",
        ],
    }
