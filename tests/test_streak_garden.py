"""Regression tests for Streak Garden's deterministic progression engine."""
import unittest
from datetime import date, timedelta

from streak_garden.enums import GrowthStage, TreeStatus
from streak_garden.engine import (
    TREE_PLANTED_DEW,
    garden_summary,
    initialize_garden_state,
    sell_tree,
    synchronize_garden,
)
from streak_garden.models import default_garden_state, sanitize_garden_state
from streak_garden.rules import (
    calculate_cycle_progress,
    calculate_streak_summary,
    dew_balance,
    growth_stage_for_days,
)


class StreakGardenRuleTests(unittest.TestCase):
    def test_current_streak_includes_yesterday_until_today_is_over(self):
        today = date(2026, 11, 1)
        dates = {today - timedelta(days=2), today - timedelta(days=1)}
        self.assertEqual(calculate_streak_summary(dates, today)["current_streak"], 2)
        self.assertFalse(calculate_streak_summary(dates, today)["today_complete"])

    def test_gap_resets_current_streak_but_not_longest(self):
        today = date(2026, 11, 1)
        dates = {
            today - timedelta(days=5),
            today - timedelta(days=4),
            today - timedelta(days=2),
        }
        summary = calculate_streak_summary(dates, today)
        self.assertEqual(summary["current_streak"], 0)
        self.assertEqual(summary["longest_streak"], 2)

    def test_cycle_progress_counts_unique_days_and_caps_at_target(self):
        start = date(2026, 10, 26)
        dates = [start, start, start + timedelta(days=1), start + timedelta(days=2)]
        result = calculate_cycle_progress(dates, start, start + timedelta(days=3))
        self.assertEqual(result["qualifying_days"], 3)
        self.assertEqual(result["percentage"], 60)
        self.assertFalse(result["completed"])

    def test_tree_growth_stages(self):
        self.assertIsNone(growth_stage_for_days(4))
        self.assertEqual(growth_stage_for_days(5), GrowthStage.SEEDLING)
        self.assertEqual(growth_stage_for_days(6), GrowthStage.SAPLING)
        self.assertEqual(growth_stage_for_days(7), GrowthStage.MATURE)

    def test_wallet_uses_signed_append_only_transactions(self):
        self.assertEqual(
            dew_balance([{"amount": 5}, {"amount": 25}, {"amount": -10}]),
            20,
        )


class StreakGardenEngineTests(unittest.TestCase):
    def setUp(self):
        self.start = date(2026, 10, 26)
        self.today = self.start + timedelta(days=4)
        self.names = {"fractions": "Simple Fractions"}
        self.state = initialize_garden_state(
            default_garden_state(), self.names, self.start
        )

    def test_five_of_seven_plants_seedling_and_awards_water_and_tree_dew_once(self):
        dates = {self.start + timedelta(days=day) for day in range(5)}
        updated, changed = synchronize_garden(
            self.state, self.names, {"fractions": dates}, dates, self.today
        )
        self.assertTrue(changed)
        self.assertEqual(len(updated["trees"]), 1)
        self.assertEqual(updated["trees"][0]["growth_stage"], GrowthStage.SEEDLING)
        self.assertEqual(updated["trees"][0]["status"], TreeStatus.ACTIVE.value)
        self.assertEqual(
            garden_summary(updated, {"fractions": dates}, dates, self.today)["dew_balance"],
            5 * 5 + TREE_PLANTED_DEW,
        )

        repeated, changed_again = synchronize_garden(
            updated, self.names, {"fractions": dates}, dates, self.today
        )
        self.assertFalse(changed_again)
        self.assertEqual(len(repeated["trees"]), 1)
        self.assertEqual(len(repeated["wallet_transactions"]), len(updated["wallet_transactions"]))

    def test_sixth_and_seventh_days_grow_the_existing_tree(self):
        dates = {self.start + timedelta(days=day) for day in range(5)}
        updated, _ = synchronize_garden(
            self.state, self.names, {"fractions": dates}, dates, self.today
        )
        day_six = self.start + timedelta(days=5)
        dates.add(day_six)
        updated, _ = synchronize_garden(
            updated, self.names, {"fractions": dates}, dates, day_six
        )
        self.assertEqual(updated["trees"][0]["growth_stage"], GrowthStage.SAPLING)
        day_seven = self.start + timedelta(days=6)
        dates.add(day_seven)
        updated, _ = synchronize_garden(
            updated, self.names, {"fractions": dates}, dates, day_seven
        )
        self.assertEqual(updated["trees"][0]["growth_stage"], GrowthStage.MATURE)
        reasons = [item["reason"] for item in updated["wallet_transactions"]]
        self.assertEqual(reasons.count("tree_growth"), 2)

    def test_selling_tree_retains_history_and_new_cycle_uses_freed_slot(self):
        state = initialize_garden_state(self.state, self.names, self.start)
        state["forests"]["fractions"]["tree_capacity"] = 5
        first_cycle_dates = {self.start + timedelta(days=day) for day in range(5)}
        state, _ = synchronize_garden(
            state, self.names, {"fractions": first_cycle_dates}, first_cycle_dates,
            self.start + timedelta(days=4)
        )
        tree_id = state["trees"][0]["id"]
        sold_state, sale_value = sell_tree(state, tree_id, self.start + timedelta(days=5))
        self.assertEqual(sale_value, 5)
        self.assertEqual(sold_state["trees"][0]["status"], TreeStatus.SOLD.value)

        second_cycle_dates = first_cycle_dates | {
            self.start + timedelta(days=7 + day) for day in range(5)
        }
        updated, _ = synchronize_garden(
            sold_state, self.names, {"fractions": second_cycle_dates},
            second_cycle_dates, self.start + timedelta(days=11)
        )
        self.assertEqual(len(updated["trees"]), 2)
        self.assertEqual(
            sum(item["status"] == TreeStatus.ACTIVE.value for item in updated["trees"]),
            1,
        )

    def test_capacity_blocks_new_trees_without_discarding_milestones(self):
        state = initialize_garden_state(self.state, self.names, self.start)
        state["forests"]["fractions"]["tree_capacity"] = 5
        state["trees"] = [
            {
                "id": f"old:{index}",
                "forest_id": "fractions",
                "cycle_start": self.start.isoformat(),
                "growth_stage": 1,
                "status": TreeStatus.ACTIVE.value,
                "planted_on": self.start.isoformat(),
                "sold_on": None,
            }
            for index in range(5)
        ]
        dates = {
            self.start + timedelta(days=day) for day in range(5)
        } | {
            self.start + timedelta(days=7 + day) for day in range(5)
        }
        updated, _ = synchronize_garden(
            state, self.names, {"fractions": dates}, dates,
            self.start + timedelta(days=11)
        )
        self.assertEqual(len(updated["trees"]), 5)

    def test_sanitizer_drops_invalid_rows_and_preserves_valid_state(self):
        value = {
            "schema_version": 1,
            "created_on": "2026-10-26",
            "forests": {"fractions": {
                "name": "Simple Fractions",
                "anchor_date": "2026-10-26",
                "target_days": 5,
                "tree_capacity": 10,
            }},
            "trees": [{"id": "bad"}],
            "wallet_transactions": [{
                "source_key": "water:2026-10-26",
                "amount": 5,
                "reason": "daily_water",
                "created_on": "2026-10-26",
            }],
        }
        cleaned = sanitize_garden_state(value)
        self.assertEqual(cleaned["created_on"], "2026-10-26")
        self.assertEqual(cleaned["forests"]["fractions"]["tree_capacity"], 10)
        self.assertEqual(cleaned["trees"], [])
        self.assertEqual(len(cleaned["wallet_transactions"]), 1)


if __name__ == "__main__":
    unittest.main()
