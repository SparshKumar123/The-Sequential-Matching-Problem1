# VOUCH-OPT — Sequential Matching Submission

This is a ready-to-upload project package based on the official public release of **The One Introduction Problem**. VOUCH-OPT applies the kit's reciprocal hard-eligibility gate, a deterministic clarification heuristic, a reservation value and weighted general-graph matching. Every profile and outcome in the kit is synthetic; these evaluations do not establish real-world relationship outcomes.

The base kit is pinned to source commit `a8e26b35118cfa8e886a02f93984923e43ab64f6`. The supplied Round 1 research note is retained at `docs/reference/VOUCH-OPT_Round1_Research_Note.pdf`.

## Quick start

Requirements: Python 3.10+ (tested with Python 3.13); Docker is needed for the isolated container check. The pinned NetworkX and decorator wheels are included in `wheelhouse/`, so dependency installation and image builds do not need network access.

```bash
python -m pip install --no-index --find-links=wheelhouse -r requirements.txt
python -m unittest -v
python verify_data.py
python evaluate.py --policy policy.py --seeds 101 --variants all --output results/quick.json
```

## Full experiments and dynamic report

Run the same three public seeds on all six public scenario variants for the three supplied baselines, VOUCH-OPT, and the allocation ablation:

```bash
bash run_experiments.sh
bash run_ablations.sh
python generate_report.py
```

The scripts retain the JSON output from every episode under `results/`. `generate_report.py` reads those results and regenerates `report.md` from their actual contents. It exits with an error if a required result is missing or any episode is invalid; it never inserts placeholder scores.

The exact commands run by the scripts are:

```bash
python -m unittest -v
python verify_data.py
python evaluate.py --policy starter_policy.py --baseline greedy --seeds 101,102,103 --variants all --output results/greedy.json
python evaluate.py --policy starter_policy.py --baseline no_asks --seeds 101,102,103 --variants all --output results/no_asks.json
python evaluate.py --policy starter_policy.py --baseline random --seeds 101,102,103 --variants all --output results/random.json
python evaluate.py --policy policy.py --seeds 101,102,103 --variants all --output results/vouchopt.json
python evaluate.py --policy ablation_greedy_allocator.py --seeds 101,102,103 --variants all --output results/ablation_greedy_allocator.json
python generate_report.py
```

The focused ablation changes only the allocator (global weighted matching vs. greedy edge selection); its asks, edge score and reservation rule are the same. Three seeds are a modest reproducible public run, not enough for strong statistical or superiority claims.

## Policy and safeguards

- `policy.py`: custom policy; asks first, then uses the refreshed observations.
- `starter_policy.py`: exact copy of the repository's supplied baseline adapter, used for baseline comparisons.
- `kit.py`: authoritative public eligibility and simulator semantics.
- Hard constraints, availability and repeat pairs are checked before an edge is added. Unknown or declined hard answers never become consent.
- The ranking score is a shrunk soft-feature agreement score, not a success probability. Missing soft values are excluded.
- General-graph maximum-weight matching uses pinned NetworkX 3.4.2.
- No latent truth, simulator seed, future arrival or hidden outcome is read by the policy. Memory is returned unchanged; no filesystem state is needed.

## Container check

After Docker is available:

```bash
docker build -t sequential-policy:submission .
python evaluate.py --image sequential-policy:submission --seeds 101 --variants all --output results/container_check.json
```

Container evaluation uses the official harness's offline, restricted runtime. The environment used to prepare this archive did not have Docker installed, so the Docker build and isolated container check remain to be run before the official submission. The Dockerfile and vendored wheels are present.

## Upload to GitHub

Create or open the intended public repository, extract this archive, and upload the extracted project contents (including `data/`, `results/`, `report.md`, `Dockerfile`, and `wheelhouse/`). For Git-based submission, commit the complete contents and pin the full 40-character commit SHA in the official Final submission issue. `results/` is ignored by the upstream starter's `.gitignore`; force-add the result JSON files when committing:

```bash
git add -f results/*.json
git add README.md report.md policy.py Dockerfile requirements.txt wheelhouse
git add .
git commit -m "Submit VOUCH-OPT policy and public evaluation"
git rev-parse HEAD
```

Follow `docs/SUBMISSION.md` and the official issue template for the final submission. The public submission cutoff is 18 October 2026, 23:59 IST.

## Dependencies and licences

- Official starter code and public synthetic data: licences and terms in `LICENSE` and `DATA_LICENSE.md`.
- NetworkX 3.4.2: BSD-3-Clause.
- decorator 5.2.1: BSD-2-Clause.
- Full bundled dependency licence texts: `THIRD_PARTY_NOTICES.md` and `third_party_licenses/`.
- No pretrained model, external participant data, training run or GPU is used.
- Coding assistance: Notion AI and a local coding environment; all reported metrics are produced by the included public evaluator.
