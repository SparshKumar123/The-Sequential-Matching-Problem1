#!/usr/bin/env bash
set -euo pipefail
python -m unittest -v
python verify_data.py
python evaluate.py --policy starter_policy.py --baseline greedy --seeds 101,102,103 --variants all --output results/greedy.json
python evaluate.py --policy starter_policy.py --baseline no_asks --seeds 101,102,103 --variants all --output results/no_asks.json
python evaluate.py --policy starter_policy.py --baseline random --seeds 101,102,103 --variants all --output results/random.json
python evaluate.py --policy policy.py --seeds 101,102,103 --variants all --output results/vouchopt.json
