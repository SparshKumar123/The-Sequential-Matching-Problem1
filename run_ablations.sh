#!/usr/bin/env bash
set -euo pipefail
python evaluate.py --policy ablation_greedy_allocator.py --seeds 101,102,103 --variants all --output results/ablation_greedy_allocator.json
