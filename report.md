# VOUCH-OPT — Public Evaluation Report

> Generated from `results/*.json` by `generate_report.py`. Seeds: 101, 102, 103.
> All profiles, decisions and outcomes are synthetic simulator data. These results are exploratory public-kit measurements, not evidence about real people.

## 1. Method and claim

VOUCH-OPT uses the public kit's `eligibility()` as a non-negotiable reciprocal hard gate. It estimates a transparent ranking score by shrinking observed agreement on relationship goal, pace, lifestyle and conversation style toward a neutral prior; unknown values are omitted. It spends the daily clarification budget first on unresolved hard-constraint bundles with overlap-aware potential value, then on soft fields that could affect feasible-edge ranking. A linearly declining reservation threshold adjusts edge values, after which positive values are allocated as a general-graph maximum-weight matching. A focused ablation replaces only the global allocator with descending-weight greedy allocation.

This is an implementation of the proposed Round 1 approach, not a validated VOI estimator or a calibrated outcome model. `q` is a ranking score, not a probability. The policy has no access to hidden profile truth, future arrivals, random seeds, or outcomes.

## 2. Run and reproducibility

- Official public source snapshot: `a8e26b35118cfa8e886a02f93984923e43ab64f6`.
- Seeds: 101, 102, 103; public variants: development, sparse, cold_start, delayed, shift, drift.
- Each episode uses the public evaluator's 60 decision days and 40 follow-up days.
- Commands: `bash run_experiments.sh`, `bash run_ablations.sh`, then `python generate_report.py`.
- NetworkX 3.4.2 and decorator 5.2.1 are pinned and vendored as wheels; no model training, external dataset, GPU, or inference-time network is used.
- Unit tests and data checks are run by `run_experiments.sh`; the report is based on the machine-readable JSON beside it.

## 3. Overall results

Overall score is the evaluator's equally weighted mean of the six variant means. Values are descriptive averages over the listed episodes; the seed count is small.

| Method | MSMI / 100 arrived | Coverage | Mutual accepts / 100 | Ask cost | Inference sec / episode | Valid episodes |
|---|---:|---:|---:|---:|---:|---:|
| Greedy baseline | 0.39 | 37.17% | 5.50 | 206.67 | 10.242 | 18 |
| No-asks baseline | 0.14 | 14.28% | 1.75 | 0.00 | 10.624 | 18 |
| Random-feasible baseline | 0.28 | 37.67% | 5.33 | 206.67 | 10.054 | 18 |
| VOUCH-OPT | 0.42 | 26.17% | 4.19 | 297.72 | 19.946 | 18 |
| Greedy-allocation ablation | 0.42 | 26.14% | 4.19 | 297.72 | 17.860 | 18 |

## 4. Scenario-level outcomes

Means across the same seeds within each scenario. MSMI uses the simulator's qualifying date and two timely second-meeting reports; coverage is the distinct-arrived-member coverage measure.

| Method | Scenario | MSMI / 100 | Coverage | Assignments | Mutual accepts | Dates | MSMI count | Ask cost | Missing feedback |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Greedy baseline | `development` | 0.50 | 43.17% | 99.67 | 13.00 | 10.00 | 1.00 | 200.00 | 60.00 |
| Greedy baseline | `sparse` | 0.17 | 14.50% | 17.67 | 4.67 | 4.00 | 0.33 | 196.00 | 8.33 |
| Greedy baseline | `cold_start` | 0.17 | 36.00% | 65.00 | 9.33 | 7.67 | 0.33 | 244.00 | 30.33 |
| Greedy baseline | `delayed` | 0.50 | 43.00% | 96.33 | 13.67 | 10.67 | 1.00 | 200.00 | 55.33 |
| Greedy baseline | `shift` | 0.50 | 43.17% | 99.67 | 13.00 | 10.00 | 1.00 | 200.00 | 58.67 |
| Greedy baseline | `drift` | 0.50 | 43.17% | 100.67 | 12.33 | 9.33 | 1.00 | 200.00 | 60.33 |
| No-asks baseline | `development` | 0.17 | 18.33% | 32.33 | 4.33 | 3.33 | 0.33 | 0.00 | 18.00 |
| No-asks baseline | `sparse` | 0.00 | 4.33% | 5.33 | 1.00 | 1.00 | 0.00 | 0.00 | 2.00 |
| No-asks baseline | `cold_start` | 0.00 | 8.00% | 11.00 | 2.33 | 1.67 | 0.00 | 0.00 | 4.67 |
| No-asks baseline | `delayed` | 0.33 | 18.33% | 32.33 | 5.00 | 3.33 | 0.67 | 0.00 | 19.00 |
| No-asks baseline | `shift` | 0.17 | 18.33% | 32.67 | 4.00 | 3.33 | 0.33 | 0.00 | 18.33 |
| No-asks baseline | `drift` | 0.17 | 18.33% | 32.33 | 4.33 | 3.33 | 0.33 | 0.00 | 18.00 |
| Random-feasible baseline | `development` | 0.33 | 44.00% | 101.00 | 13.00 | 11.00 | 0.67 | 200.00 | 54.67 |
| Random-feasible baseline | `sparse` | 0.17 | 14.50% | 17.67 | 4.33 | 3.67 | 0.33 | 196.00 | 8.33 |
| Random-feasible baseline | `cold_start` | 0.17 | 36.33% | 65.00 | 9.00 | 8.33 | 0.33 | 244.00 | 31.67 |
| Random-feasible baseline | `delayed` | 0.17 | 43.83% | 98.00 | 13.67 | 10.33 | 0.33 | 200.00 | 50.00 |
| Random-feasible baseline | `shift` | 0.50 | 43.33% | 100.33 | 11.67 | 9.00 | 1.00 | 200.00 | 52.00 |
| Random-feasible baseline | `drift` | 0.33 | 44.00% | 101.00 | 12.33 | 10.33 | 0.67 | 200.00 | 54.67 |
| VOUCH-OPT | `development` | 0.67 | 30.83% | 49.33 | 11.33 | 9.67 | 1.33 | 302.33 | 25.67 |
| VOUCH-OPT | `sparse` | 0.00 | 8.50% | 9.67 | 1.67 | 1.67 | 0.00 | 217.67 | 5.33 |
| VOUCH-OPT | `cold_start` | 0.33 | 25.00% | 36.00 | 8.00 | 6.33 | 0.67 | 359.33 | 19.33 |
| VOUCH-OPT | `delayed` | 0.33 | 31.00% | 50.33 | 9.33 | 7.67 | 0.67 | 302.00 | 25.67 |
| VOUCH-OPT | `shift` | 0.50 | 30.83% | 50.67 | 9.33 | 8.33 | 1.00 | 302.67 | 26.67 |
| VOUCH-OPT | `drift` | 0.67 | 30.83% | 49.33 | 10.67 | 9.33 | 1.33 | 302.33 | 25.33 |
| Greedy-allocation ablation | `development` | 0.67 | 30.83% | 49.33 | 11.33 | 9.67 | 1.33 | 302.33 | 26.33 |
| Greedy-allocation ablation | `sparse` | 0.00 | 8.50% | 9.67 | 1.67 | 1.67 | 0.00 | 217.67 | 5.33 |
| Greedy-allocation ablation | `cold_start` | 0.33 | 25.00% | 36.00 | 8.00 | 6.33 | 0.67 | 359.33 | 19.33 |
| Greedy-allocation ablation | `delayed` | 0.33 | 30.83% | 50.00 | 9.33 | 7.67 | 0.67 | 302.00 | 26.33 |
| Greedy-allocation ablation | `shift` | 0.50 | 30.83% | 50.67 | 9.33 | 8.33 | 1.00 | 302.67 | 27.33 |
| Greedy-allocation ablation | `drift` | 0.67 | 30.83% | 49.33 | 10.67 | 9.33 | 1.33 | 302.33 | 26.00 |

### Waiting, unserved members, and runtime

Wait summaries are over member-episode observations that received a first introduction; unserved members are averaged across episodes.

| Method | Scenario | Mean wait days | Median wait days | Unserved members | Inference sec / episode |
|---|---|---:|---:|---:|---:|
| Greedy baseline | `development` | 6.04 | 3.00 | 113.67 | 10.363 |
| Greedy baseline | `sparse` | 6.24 | 4.00 | 171.00 | 11.528 |
| Greedy baseline | `cold_start` | 8.05 | 6.00 | 128.00 | 10.684 |
| Greedy baseline | `delayed` | 6.47 | 3.00 | 114.00 | 9.602 |
| Greedy baseline | `shift` | 5.98 | 3.00 | 113.67 | 9.658 |
| Greedy baseline | `drift` | 6.04 | 3.00 | 113.67 | 9.618 |
| No-asks baseline | `development` | 4.26 | 0.00 | 163.33 | 10.697 |
| No-asks baseline | `sparse` | 4.23 | 0.00 | 191.33 | 10.913 |
| No-asks baseline | `cold_start` | 3.58 | 0.00 | 184.00 | 10.829 |
| No-asks baseline | `delayed` | 4.29 | 0.00 | 163.33 | 10.569 |
| No-asks baseline | `shift` | 4.12 | 0.00 | 163.33 | 10.198 |
| No-asks baseline | `drift` | 4.26 | 0.00 | 163.33 | 10.536 |
| Random-feasible baseline | `development` | 6.09 | 4.00 | 112.00 | 9.147 |
| Random-feasible baseline | `sparse` | 6.15 | 4.00 | 171.00 | 11.494 |
| Random-feasible baseline | `cold_start` | 8.37 | 6.00 | 127.33 | 11.066 |
| Random-feasible baseline | `delayed` | 6.41 | 4.00 | 112.33 | 9.838 |
| Random-feasible baseline | `shift` | 6.17 | 4.00 | 113.33 | 9.424 |
| Random-feasible baseline | `drift` | 6.09 | 4.00 | 112.00 | 9.352 |
| VOUCH-OPT | `development` | 13.96 | 15.00 | 138.33 | 20.116 |
| VOUCH-OPT | `sparse` | 15.14 | 14.00 | 183.00 | 19.812 |
| VOUCH-OPT | `cold_start` | 17.28 | 19.00 | 150.00 | 19.881 |
| VOUCH-OPT | `delayed` | 14.31 | 15.00 | 138.00 | 19.942 |
| VOUCH-OPT | `shift` | 13.85 | 15.00 | 138.33 | 20.102 |
| VOUCH-OPT | `drift` | 13.96 | 15.00 | 138.33 | 19.825 |
| Greedy-allocation ablation | `development` | 14.02 | 15.00 | 138.33 | 18.355 |
| Greedy-allocation ablation | `sparse` | 15.14 | 14.00 | 183.00 | 19.561 |
| Greedy-allocation ablation | `cold_start` | 17.28 | 19.00 | 150.00 | 17.509 |
| Greedy-allocation ablation | `delayed` | 14.19 | 15.00 | 138.33 | 17.218 |
| Greedy-allocation ablation | `shift` | 13.91 | 15.00 | 138.33 | 17.518 |
| Greedy-allocation ablation | `drift` | 14.02 | 15.00 | 138.33 | 16.999 |

## 5. Outcome funnel, waits, and runtime

VOUCH-OPT totals across all evaluated episodes (counts are summed, not pooled rates):

| Assignments | Mutual acceptances | Dates | Qualifying MSMI | Missing feedback events | Ask cost |
|---:|---:|---:|---:|---:|---:|
| 736 | 151 | 129 | 15 | 384 | 5359 |

Among VOUCH-OPT members who received a first introduction, the mean wait was 14.60 days and the median was 15.00 days (n=942 member-episode observations).

Inference time is measured by the evaluator around each policy subprocess call, including startup. It does not include experiment orchestration.

## 6. Hypothesis-driven allocation ablation

The comparison below changes only the allocation algorithm. It uses paired public seed/variant episodes and the same policy score, asks, and reservation rule. The delta is global matching minus greedy allocation. With three seeds per variant, this is a diagnostic comparison, not a significance test.

| Scenario | Global MSMI / 100 | Greedy MSMI / 100 | Paired delta | Global coverage | Greedy coverage |
|---|---:|---:|---:|---:|---:|
| `development` | 0.67 | 0.67 | 0.000 | 30.83% | 30.83% |
| `sparse` | 0.00 | 0.00 | 0.000 | 8.50% | 8.50% |
| `cold_start` | 0.33 | 0.33 | 0.000 | 25.00% | 25.00% |
| `delayed` | 0.33 | 0.33 | 0.000 | 31.00% | 30.83% |
| `shift` | 0.50 | 0.50 | 0.000 | 30.83% | 30.83% |
| `drift` | 0.67 | 0.67 | 0.000 | 30.83% | 30.83% |

Across paired episode-seed units, the mean MSMI-rate delta was 0.000 points per 100 arrived members (range 0.000 to 0.000). No equivalence or causal claim beyond this controlled simulator contrast is implied.

## 7. Interpretation and limitations

- Public seeds and six variants are stress tests, not the organizer's private assessment worlds.
- Three seeds per variant are not enough to establish robust ranking, equivalence, or superiority. Differences may be noisy, especially when MSMI counts are low.
- Synthetic outcomes are generated by the simulator, and the policy's ranking score is not a calibrated MSMI probability.
- The policy is myopic at each daily batch. The reservation schedule is a fixed heuristic; it does not solve the 60-day horizon.
- Clarification is a deterministic public-kit self-report abstraction; its budget units are not real user burden estimates.
- Feedback is selectively observed for assigned pairs; these runs do not identify outcomes for unassigned pairs.
- A successful local run checks these public episodes only. The official final check requires an isolated Docker run and private validation by organizers.
- The environment that generated this report had no Docker executable, so the Docker image build and restricted container smoke test have not been performed here.

## 8. Included evidence

All per-episode outputs, action hashes, validity flags, scenario summaries, inference timings, and raw metric values are included in `results/`. Re-run the experiment scripts and `python generate_report.py` to refresh this report after any code or seed change.
