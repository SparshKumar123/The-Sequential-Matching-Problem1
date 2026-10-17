"""Ablation entry point: same asks and edge scores, greedy allocation."""
from policy import serve

if __name__ == "__main__":
    serve(allocator="greedy")