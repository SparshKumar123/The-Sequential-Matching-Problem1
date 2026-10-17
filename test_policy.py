import unittest

from kit import Simulator, generate
from policy import decide


class PolicyTests(unittest.TestCase):
    def test_output_is_deterministic_and_disjoint(self):
        sim = Simulator(generate(73, 100))
        for _ in range(15):
            state = sim.observe()
            asks = decide({"phase": "ask", "state": state})["asks"]
            sim.resolve_asks(asks)
            state = sim.observe()
            first = decide({"phase": "match", "state": state})
            second = decide({"phase": "match", "state": state})
            self.assertEqual(first, second)
            used = [ident for pair in first["pairs"] for ident in pair]
            self.assertEqual(len(used), len(set(used)))
            sim.advance(first["pairs"])

    def test_no_action_uses_unavailable_or_infeasible_members(self):
        sim = Simulator(generate(87, 80))
        state = sim.observe()
        asks = decide({"phase": "ask", "state": state})["asks"]
        sim.resolve_asks(asks)
        state = sim.observe()
        available = {m["member_id"] for m in state["members"] if m["available"]}
        pairs = decide({"phase": "match", "state": state})["pairs"]
        self.assertTrue(all(a in available and b in available for a, b in pairs))
        sim.advance(pairs)  # The reference simulator validates every hard rule.

    def test_empty_pool_and_no_ask_ablation(self):
        state = Simulator(generate(21, 0)).observe()
        self.assertEqual(decide({"phase": "match", "state": state})["pairs"], [])
        self.assertEqual(
            decide({"phase": "ask", "state": state}, ask_enabled=False)["asks"],
            [],
        )

    def test_ask_budget_and_unique_requests(self):
        sim = Simulator(generate(112, 200, variant="cold_start"))
        state = sim.observe()
        asks = decide({"phase": "ask", "state": state})["asks"]
        cost = sum(3 if ask["field"] == "constraints" else 1 for ask in asks)
        self.assertLessEqual(cost, state["ask_budget_remaining"])
        self.assertEqual(len({(a["member_id"], a["field"]) for a in asks}), len(asks))
        sim.resolve_asks(asks)


if __name__ == "__main__":
    unittest.main()