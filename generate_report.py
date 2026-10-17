#!/usr/bin/env python3
"""Build report.md from the checked evaluator JSON; no scores are hard-coded."""

from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VARIANTS = ("development", "sparse", "cold_start", "delayed", "shift", "drift")
METHODS = (
    ("Greedy baseline", "greedy.json"),
    ("No-asks baseline", "no_asks.json"),
    ("Random-feasible baseline", "random.json"),
    ("VOUCH-OPT", "vouchopt.json"),
    ("Greedy-allocation ablation", "ablation_greedy_allocator.json"),
)


def load_result(filename: str) -> dict:
    path = ROOT / "results" / filename
    if not path.is_file():
        raise SystemExit(f"Missing {path.relative_to(ROOT)}; run the experiment scripts first.")
    data = json.loads(path.read_text())
    rows = data.get("episodes", [])
    if not rows or any(row.get("valid") is not True for row in rows):
        raise SystemExit(f"{filename} contains missing or invalid episodes; do not report it.")
    if data.get("summary", {}).get("eligible") is not True:
        raise SystemExit(f"{filename} is not marked eligible by the evaluator.")
    got = {row.get("variant") for row in rows}
    if got != set(VARIANTS):
        raise SystemExit(f"{filename} does not contain all six public variants: {sorted(got)}")
    return data


def mean(rows: list[dict], key: str) -> float:
    return statistics.mean(float(row[key]) for row in rows)


def fmt(value: float, places: int = 2) -> str:
    return f"{value:.{places}f}"


def group(data: dict, variant: str) -> list[dict]:
    return [row for row in data["episodes"] if row["variant"] == variant]


def wait_days(data: dict) -> list[float]:
    return [
        float(value)
        for row in data["episodes"]
        for value in row.get("first_introduction_wait_days", [])
    ]


def main() -> None:
    loaded = {label: load_result(filename) for label, filename in METHODS}
    all_seed_sets = {
        label: sorted({row["seed"] for row in data["episodes"]})
        for label, data in loaded.items()
    }
    expected = all_seed_sets["VOUCH-OPT"]
    if any(seeds != expected for seeds in all_seed_sets.values()):
        raise SystemExit("Methods were not evaluated on the same seed set.")

    lines: list[str] = [
        "# VOUCH-OPT — Public Evaluation Report",
        "",
        f"> Generated from `results/*.json` by `generate_report.py`. Seeds: {', '.join(map(str, expected))}.",
        "> All profiles, decisions and outcomes are synthetic simulator data. These results are exploratory public-kit measurements, not evidence about real people.",
        "",
        "## 1. Method and claim",
        "",
        "VOUCH-OPT uses the public kit's `eligibility()` as a non-negotiable reciprocal hard gate. It estimates a transparent ranking score by shrinking observed agreement on relationship goal, pace, lifestyle and conversation style toward a neutral prior; unknown values are omitted. It spends the daily clarification budget first on unresolved hard-constraint bundles with overlap-aware potential value, then on soft fields that could affect feasible-edge ranking. A linearly declining reservation threshold adjusts edge values, after which positive values are allocated as a general-graph maximum-weight matching. A focused ablation replaces only the global allocator with descending-weight greedy allocation.",
        "",
        "This is an implementation of the proposed Round 1 approach, not a validated VOI estimator or a calibrated outcome model. `q` is a ranking score, not a probability. The policy has no access to hidden profile truth, future arrivals, random seeds, or outcomes.",
        "",
        "## 2. Run and reproducibility",
        "",
        "- Official public source snapshot: `a8e26b35118cfa8e886a02f93984923e43ab64f6`.",
        "- Seeds: " + ", ".join(map(str, expected)) + "; public variants: " + ", ".join(VARIANTS) + ".",
        "- Each episode uses the public evaluator's 60 decision days and 40 follow-up days.",
        "- Commands: `bash run_experiments.sh`, `bash run_ablations.sh`, then `python generate_report.py`.",
        "- NetworkX 3.4.2 and decorator 5.2.1 are pinned and vendored as wheels; no model training, external dataset, GPU, or inference-time network is used.",
        "- Unit tests and data checks are run by `run_experiments.sh`; the report is based on the machine-readable JSON beside it.",
        "",
        "## 3. Overall results",
        "",
        "Overall score is the evaluator's equally weighted mean of the six variant means. Values are descriptive averages over the listed episodes; the seed count is small.",
        "",
        "| Method | MSMI / 100 arrived | Coverage | Mutual accepts / 100 | Ask cost | Inference sec / episode | Valid episodes |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label, _ in METHODS:
        summary = loaded[label]["summary"]
        overall = summary["overall"]
        lines.append(
            f"| {label} | {fmt(overall['msmi_per_100_arrived_members'])} "
            f"| {fmt(overall['coverage'] * 100)}% "
            f"| {fmt(overall['mutual_acceptances_per_100'])} "
            f"| {fmt(overall['ask_cost'])} "
            f"| {fmt(overall['inference_seconds'], 3)} "
            f"| {len(loaded[label]['episodes'])} |"
        )
    lines.extend([
        "",
        "## 4. Scenario-level outcomes",
        "",
        "Means across the same seeds within each scenario. MSMI uses the simulator's qualifying date and two timely second-meeting reports; coverage is the distinct-arrived-member coverage measure.",
        "",
        "| Method | Scenario | MSMI / 100 | Coverage | Assignments | Mutual accepts | Dates | MSMI count | Ask cost | Missing feedback |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for label, _ in METHODS:
        data = loaded[label]
        for variant in VARIANTS:
            rows = group(data, variant)
            lines.append(
                f"| {label} | `{variant}` "
                f"| {fmt(mean(rows, 'msmi_per_100_arrived_members'))} "
                f"| {fmt(mean(rows, 'coverage') * 100)}% "
                f"| {fmt(mean(rows, 'assignments'))} "
                f"| {fmt(mean(rows, 'mutual_acceptances'))} "
                f"| {fmt(mean(rows, 'dates'))} "
                f"| {fmt(mean(rows, 'mutual_second_meeting_intention'))} "
                f"| {fmt(mean(rows, 'ask_cost'))} "
                f"| {fmt(mean(rows, 'missing_feedback'))} |"
            )

    lines.extend([
        "",
        "### Waiting, unserved members, and runtime",
        "",
        "Wait summaries are over member-episode observations that received a first introduction; unserved members are averaged across episodes.",
        "",
        "| Method | Scenario | Mean wait days | Median wait days | Unserved members | Inference sec / episode |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for label, _ in METHODS:
        data = loaded[label]
        for variant in VARIANTS:
            rows = group(data, variant)
            waits = [
                float(value)
                for row in rows
                for value in row.get("first_introduction_wait_days", [])
            ]
            average_wait = fmt(statistics.mean(waits)) if waits else "n/a"
            median_wait = fmt(statistics.median(waits)) if waits else "n/a"
            lines.append(
                f"| {label} | `{variant}` | {average_wait} | {median_wait} "
                f"| {fmt(mean(rows, 'unserved_members'))} "
                f"| {fmt(mean(rows, 'inference_seconds'), 3)} |"
            )

    lines.extend([
        "",
        "## 5. Outcome funnel, waits, and runtime",
        "",
        "VOUCH-OPT totals across all evaluated episodes (counts are summed, not pooled rates):",
        "",
        "| Assignments | Mutual acceptances | Dates | Qualifying MSMI | Missing feedback events | Ask cost |",
        "|---:|---:|---:|---:|---:|---:|",
    ])
    vouch = loaded["VOUCH-OPT"]
    total = lambda key: sum(int(row[key]) for row in vouch["episodes"])
    lines.append(
        f"| {total('assignments')} | {total('mutual_acceptances')} | {total('dates')} "
        f"| {total('mutual_second_meeting_intention')} | {total('missing_feedback')} | {total('ask_cost')} |"
    )
    waits = wait_days(vouch)
    if waits:
        lines.append(
            f"\nAmong VOUCH-OPT members who received a first introduction, the mean wait was "
            f"{fmt(statistics.mean(waits))} days and the median was "
            f"{fmt(statistics.median(waits))} days (n={len(waits)} member-episode observations)."
        )
    else:
        lines.append("\nNo VOUCH-OPT member received a first introduction in these episodes.")
    lines.extend([
        "",
        "Inference time is measured by the evaluator around each policy subprocess call, including startup. It does not include experiment orchestration.",
        "",
        "## 6. Hypothesis-driven allocation ablation",
        "",
        "The comparison below changes only the allocation algorithm. It uses paired public seed/variant episodes and the same policy score, asks, and reservation rule. The delta is global matching minus greedy allocation. With three seeds per variant, this is a diagnostic comparison, not a significance test.",
        "",
        "| Scenario | Global MSMI / 100 | Greedy MSMI / 100 | Paired delta | Global coverage | Greedy coverage |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for variant in VARIANTS:
        left = group(loaded["VOUCH-OPT"], variant)
        right = group(loaded["Greedy-allocation ablation"], variant)
        by_seed_left = {row["seed"]: row for row in left}
        by_seed_right = {row["seed"]: row for row in right}
        if set(by_seed_left) != set(by_seed_right):
            raise SystemExit(f"Ablation seeds differ for {variant}.")
        paired = [
            by_seed_left[seed]["msmi_per_100_arrived_members"]
            - by_seed_right[seed]["msmi_per_100_arrived_members"]
            for seed in sorted(by_seed_left)
        ]
        lines.append(
            f"| `{variant}` | {fmt(mean(left, 'msmi_per_100_arrived_members'))} "
            f"| {fmt(mean(right, 'msmi_per_100_arrived_members'))} "
            f"| {fmt(statistics.mean(paired), 3)} "
            f"| {fmt(mean(left, 'coverage') * 100)}% "
            f"| {fmt(mean(right, 'coverage') * 100)}% |"
        )
    overall_paired = []
    for variant in VARIANTS:
        left = {row["seed"]: row for row in group(loaded["VOUCH-OPT"], variant)}
        right = {row["seed"]: row for row in group(loaded["Greedy-allocation ablation"], variant)}
        overall_paired.extend(
            left[seed]["msmi_per_100_arrived_members"]
            - right[seed]["msmi_per_100_arrived_members"]
            for seed in sorted(left)
        )
    lines.extend([
        "",
        "Across paired episode-seed units, the mean MSMI-rate delta was "
        f"{fmt(statistics.mean(overall_paired), 3)} points per 100 arrived members "
        f"(range {fmt(min(overall_paired), 3)} to {fmt(max(overall_paired), 3)}). "
        "No equivalence or causal claim beyond this controlled simulator contrast is implied.",
        "",
        "## 7. Interpretation and limitations",
        "",
        "- Public seeds and six variants are stress tests, not the organizer's private assessment worlds.",
        "- Three seeds per variant are not enough to establish robust ranking, equivalence, or superiority. Differences may be noisy, especially when MSMI counts are low.",
        "- Synthetic outcomes are generated by the simulator, and the policy's ranking score is not a calibrated MSMI probability.",
        "- The policy is myopic at each daily batch. The reservation schedule is a fixed heuristic; it does not solve the 60-day horizon.",
        "- Clarification is a deterministic public-kit self-report abstraction; its budget units are not real user burden estimates.",
        "- Feedback is selectively observed for assigned pairs; these runs do not identify outcomes for unassigned pairs.",
        "- A successful local run checks these public episodes only. The official final check requires an isolated Docker run and private validation by organizers.",
        "- The environment that generated this report had no Docker executable, so the Docker image build and restricted container smoke test have not been performed here.",
        "",
        "## 8. Included evidence",
        "",
        "All per-episode outputs, action hashes, validity flags, scenario summaries, inference timings, and raw metric values are included in `results/`. Re-run the experiment scripts and `python generate_report.py` to refresh this report after any code or seed change.",
        "",
    ])
    (ROOT / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote report.md using {len(METHODS)} result files and {len(expected)} seeds.")


if __name__ == "__main__":
    main()