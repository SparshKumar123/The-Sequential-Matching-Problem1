"""VOUCH-OPT policy for the public Sequential Matching Problem simulator.

The policy uses only observable JSON state. It applies the kit's reciprocal
eligibility function as a hard gate, requests decision-relevant clarification,
and allocates positive edges with weighted general-graph matching. It makes no
real-world relationship or probability claims.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from typing import Any

from kit import HARD, eligibility

# Only these fields are used in the transparent initial edge-ranking score.
# The relative weights are declared heuristic choices, not fitted parameters.
SOFT_WEIGHTS = {
    "relationship_goal": 0.50,
    "relationship_pace": 0.25,
    "lifestyle": 0.15,
    "conversations": 0.10,
}
K_SHRINK = 0.75
Q0 = 0.50
ASK_BUDGET_DEFAULT = 12


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def _past_pairs(state: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        _pair_key(row["user_a"], row["user_b"])
        for row in state.get("introductions", [])
    }


def _q_score(a: dict[str, Any], b: dict[str, Any]) -> float:
    """Shrink observed agreement toward a neutral prior; never impute missing."""
    observed_weight = 0.0
    agreement_weight = 0.0
    fa, fb = a.get("fields", {}), b.get("fields", {})
    for field, weight in SOFT_WEIGHTS.items():
        va, vb = fa.get(field), fb.get(field)
        if va is None or vb is None:
            continue
        observed_weight += weight
        if va == vb:
            agreement_weight += weight
    if observed_weight == 0:
        observed_similarity = Q0
    else:
        observed_similarity = agreement_weight / observed_weight
    return (
        K_SHRINK * Q0 + observed_weight * observed_similarity
    ) / (K_SHRINK + observed_weight)


def _reservation_value(day: int) -> float:
    """Declining, observable-state-only reservation threshold."""
    bounded_day = max(0, min(59, int(day)))
    return 0.58 - 0.13 * bounded_day / 59.0


def _askable_constraints(member: dict[str, Any]) -> bool:
    fields = member.get("fields", {})
    status = member.get("field_status", {})
    missing = [f for f in HARD if fields.get(f) is None]
    # A declined hard answer remains unresolved; do not spend a bundle that
    # cannot clear the reciprocal-feasibility gate for this member.
    return bool(missing) and all(status.get(f) == "not_asked" for f in missing)


def _askable_soft(member: dict[str, Any], field: str) -> bool:
    return (
        member.get("fields", {}).get(field) is None
        and member.get("field_status", {}).get(field) == "not_asked"
    )


def _select_asks(state: dict[str, Any]) -> list[dict[str, str]]:
    """Greedy, overlap-aware clarification under the exact per-day budget.

    Hard bundles receive fractional credit for promising unresolved edges,
    with a small completion bonus when the last missing bundle is selected.
    This is a deterministic decision-value heuristic, not an unbiased VOI
    estimate. Soft questions are considered only for currently hard-feasible
    edges and only for the four fields used by the ranking score.
    """
    available = sorted(
        (m for m in state.get("members", []) if m.get("available")),
        key=lambda m: m["member_id"],
    )
    budget = max(0, int(state.get("ask_budget_remaining", ASK_BUDGET_DEFAULT)))
    past = _past_pairs(state)
    askable = {
        m["member_id"]: m
        for m in available
        if _askable_constraints(m)
    }

    # Potential hard edges are those with no known contradiction and whose
    # missing hard bundles could all be requested. No inferred answer is used.
    potential_edges: list[tuple[tuple[str, str], tuple[str, ...], float]] = []
    for a, b in itertools.combinations(available, 2):
        key = _pair_key(a["member_id"], b["member_id"])
        if key in past:
            continue
        result = eligibility(a, b)
        if result["status"] != "needs_clarification":
            continue
        needed_ids = tuple(sorted({
            item.split(":", 1)[0] for item in result.get("missing", [])
        }))
        if not needed_ids or any(i not in askable for i in needed_ids):
            continue
        potential_edges.append((key, needed_ids, _q_score(a, b)))

    asks: list[dict[str, str]] = []
    selected: set[str] = set()
    while budget >= 3 and askable:
        best_id: str | None = None
        best_value = 0.0
        for ident in sorted(askable):
            if ident in selected:
                continue
            gain = 0.0
            for _, needed_ids, q in potential_edges:
                if ident not in needed_ids:
                    continue
                before = len(selected.intersection(needed_ids))
                after = before + 1
                gain += q / len(needed_ids)
                if before < len(needed_ids) and after == len(needed_ids):
                    gain += 0.15 * q
            value_per_unit = gain / 3.0
            if value_per_unit > best_value + 1e-12:
                best_id, best_value = ident, value_per_unit
        if best_id is None:
            break
        selected.add(best_id)
        asks.append({"member_id": best_id, "field": "constraints"})
        budget -= 3

    # Soft asks are a lower priority. A missing feature is considered only if
    # it is observed on at least one feasible counterpart, so the answer can
    # alter today's edge ordering after refresh.
    if budget > 0:
        hard_complete = [
            m for m in available
            if all(m.get("fields", {}).get(f) is not None for f in HARD)
        ]
        feasible_partners: dict[str, list[dict[str, Any]]] = {
            m["member_id"]: [] for m in hard_complete
        }
        for a, b in itertools.combinations(hard_complete, 2):
            key = _pair_key(a["member_id"], b["member_id"])
            if key in past or eligibility(a, b)["status"] != "feasible":
                continue
            feasible_partners[a["member_id"]].append(b)
            feasible_partners[b["member_id"]].append(a)

        requested_soft: set[tuple[str, str]] = set()
        while budget > 0:
            best: tuple[str, str] | None = None
            best_gain = 0.0
            for member in hard_complete:
                ident = member["member_id"]
                for field, field_weight in SOFT_WEIGHTS.items():
                    candidate = (ident, field)
                    if candidate in requested_soft or not _askable_soft(member, field):
                        continue
                    support = 0.0
                    for other in feasible_partners.get(ident, []):
                        if other.get("fields", {}).get(field) is not None:
                            support += max(0.05, _q_score(member, other))
                    gain = field_weight * support
                    if gain > best_gain + 1e-12:
                        best, best_gain = candidate, gain
            if best is None:
                break
            ident, field = best
            requested_soft.add(best)
            asks.append({"member_id": ident, "field": field})
            budget -= 1

    return asks


def _edge_rows(state: dict[str, Any]) -> list[tuple[float, tuple[str, str]]]:
    available = sorted(
        (m for m in state.get("members", []) if m.get("available")),
        key=lambda m: m["member_id"],
    )
    by_id = {m["member_id"]: m for m in available}
    past = _past_pairs(state)
    reserve = _reservation_value(state.get("day", 0))
    edges: list[tuple[float, tuple[str, str]]] = []
    for a, b in itertools.combinations(available, 2):
        key = _pair_key(a["member_id"], b["member_id"])
        if key in past or eligibility(a, b)["status"] != "feasible":
            continue
        adjusted = _q_score(by_id[key[0]], by_id[key[1]]) - reserve
        if adjusted > 0:
            edges.append((adjusted, key))
    return sorted(edges, key=lambda row: (-row[0], row[1]))


def _allocate_global(edges: list[tuple[float, tuple[str, str]]]) -> list[list[str]]:
    """Deterministic NetworkX blossom maximum-weight general matching."""
    if not edges:
        return []
    # Import only for match-phase invocations; the ask phase remains lean.
    import networkx as nx

    graph = nx.Graph()
    vertices = sorted({ident for _, edge in edges for ident in edge})
    graph.add_nodes_from(vertices)
    # Quantize at 1e-6 and make the deterministic tie-break strictly smaller
    # than a one-unit primary-score difference across any 200-person batch.
    tie_scale = 10_000_000
    rank_max = len(edges)
    for rank, (weight, (a, b)) in enumerate(sorted(edges, key=lambda row: row[1])):
        primary = int(round(weight * 1_000_000))
        tie_bonus = rank_max - rank
        graph.add_edge(a, b, weight=primary * tie_scale + tie_bonus)
    matched = nx.max_weight_matching(graph, maxcardinality=False, weight="weight")
    return [list(pair) for pair in sorted(_pair_key(a, b) for a, b in matched)]


def _allocate_greedy(edges: list[tuple[float, tuple[str, str]]]) -> list[list[str]]:
    """Greedy allocator used only for the focused allocation ablation."""
    used: set[str] = set()
    output: list[list[str]] = []
    for _, (a, b) in sorted(edges, key=lambda row: (-row[0], row[1])):
        if a not in used and b not in used:
            output.append([a, b])
            used.update((a, b))
    return output


def decide(
    request: dict[str, Any],
    *,
    allocator: str = "global",
    ask_enabled: bool = True,
) -> dict[str, Any]:
    state = request["state"]
    memory = request.get("memory")
    if memory is None:
        memory = {}
    if request.get("phase") == "ask":
        asks = _select_asks(state) if ask_enabled else []
        return {"asks": asks, "memory": memory}
    if request.get("phase") == "match":
        edges = _edge_rows(state)
        if allocator == "global":
            pairs = _allocate_global(edges)
        elif allocator == "greedy":
            pairs = _allocate_greedy(edges)
        else:
            raise ValueError(f"unsupported allocator: {allocator}")
        return {"pairs": pairs, "memory": memory}
    raise ValueError("phase must be 'ask' or 'match'")


def serve(*, allocator: str = "global", ask_enabled: bool = True) -> None:
    """Read one protocol request and emit exactly one protocol response."""
    parser = argparse.ArgumentParser(add_help=False)
    # The official evaluator appends --baseline even for custom policy files.
    # It is accepted for runner compatibility and deliberately ignored here.
    parser.add_argument("--baseline", default="greedy")
    parser.parse_known_args()
    try:
        request = json.load(sys.stdin)
        response = decide(request, allocator=allocator, ask_enabled=ask_enabled)
        print(json.dumps(response, allow_nan=False, separators=(",", ":")))
    except Exception as exc:
        print(f"policy error: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    serve()