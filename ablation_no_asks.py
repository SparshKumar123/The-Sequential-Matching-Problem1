"""Optional ablation entry point: VOUCH-OPT allocation without clarification."""
from policy import serve

if __name__ == "__main__":
    serve(ask_enabled=False)