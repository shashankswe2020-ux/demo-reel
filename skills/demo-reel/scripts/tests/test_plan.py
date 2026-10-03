import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reelkit import captions  # noqa: E402
from reelkit.checks import CATALOG, score  # noqa: E402
from reelkit.plan_lint import hook_score, lint, variant_cues  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PROJECT = FIXTURES / "project"


def load_plan():
    return json.loads((FIXTURES / "reel-plan.json").read_text())


def run_lint(plan):
    checks, info = lint(plan, PROJECT, FIXTURES)
    return {c.id: c for c in checks}, info


class PlanLintTest(unittest.TestCase):
    def test_fixture_plan_passes_every_gate(self):
        checks, info = run_lint(load_plan())
        failed = {k: c.message for k, c in checks.items() if c.passed is False}
        self.assertEqual(failed, {})
        self.assertEqual(list(info["hook_scores"])[:3], ["h3", "h4", "h1"])
        self.assertEqual(set(checks), {k for k in CATALOG if k.startswith("plan.")})

    def test_unverifiable_claim_is_a_blocker(self):
        plan = load_plan()
        plan["claims"][0]["evidence"]["quote"] = "Generates an episode from 5000 commits"
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.claims_evidence"].passed)
        self.assertFalse(checks["plan.numbers_backed"].passed)
        self.assertIn("plan.claims_evidence", score(list(checks.values()))["blockers"])

    def test_evidence_cannot_escape_the_project(self):
        plan = load_plan()
        plan["claims"][0]["evidence"] = {"file": "../../../../reelkit/specs.py", "quote": "FORMATS"}
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.claims_evidence"].passed)

    def test_invented_number_on_screen_fails(self):
        plan = load_plan()
        plan["scenes"][3]["text"][0].pop("claim")
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.numbers_backed"].passed)

    def test_demo_must_showcase_one_backed_feature(self):
        plan = load_plan()
        demo = next(s for s in plan["scenes"] if s["role"] == "demo")
        demo.pop("feature")
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.product_in_use"].passed)
        demo["feature"] = {"title": "Voice cloning", "claim": "c2"}
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.product_in_use"].passed, "feature title must appear on screen")
        demo["feature"] = {"title": "Play episode", "claim": "c9"}
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.product_in_use"].passed, "feature must be claim-backed")

    def test_spelled_out_number_needs_a_claim(self):
        plan = load_plan()
        plan["scenes"][1]["text"][0]["content"] = "Six hundred teams ship with Shipcast"
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.numbers_backed"].passed)
        plan["scenes"][1]["text"][0]["content"] = "One command. Your changelog, heard."
        checks, _ = run_lint(plan)
        self.assertTrue(checks["plan.numbers_backed"].passed)

    def test_weak_variant_hook_fails_selection(self):
        plan = load_plan()
        plan["variants"][2]["hook"] = "h7"
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.hook_selection"].passed)
        self.assertFalse(checks["plan.hook_grounded"].passed)

    def test_beat_grid_flags_off_beat_cuts_without_gating(self):
        plan = load_plan()
        self.assertNotIn("beat_grid", run_lint(plan)[1])
        plan["music"] = {"bpm": 120}
        checks, info = run_lint(plan)
        self.assertEqual(len(info["beat_grid"]["off_beat"]), 1, info["beat_grid"])
        self.assertIn("@ 2.80s (-0.20s)", info["beat_grid"]["off_beat"][0])
        self.assertEqual({k: c.message for k, c in checks.items() if c.passed is False}, {})
        plan["music"]["offset_s"] = 0.3
        self.assertEqual(len(run_lint(plan)[1]["beat_grid"]["off_beat"]), 3)

    def test_treatment_advisory_flags_gaps_without_gating(self):
        plan = load_plan()
        self.assertEqual(run_lint(plan)[1]["treatment"], [])
        plan["treatment"].update(file="missing.md", motif=" ", palette=["#111214", "red"], revisions=["R1"])
        checks, info = run_lint(plan)
        self.assertEqual(len(info["treatment"]), 4, info["treatment"])
        self.assertEqual({k: c.message for k, c in checks.items() if c.passed is False}, {})
        plan = load_plan()
        plan["treatment"]["visual_truth"] = {
            "process": "", "encodings": [], "reference": "", "liberties": []
        }
        checks, info = run_lint(plan)
        self.assertEqual(len(info["treatment"]), 4, info["treatment"])
        self.assertEqual({k: c.message for k, c in checks.items() if c.passed is False}, {})
        plan = load_plan()
        del plan["treatment"]["visual_truth"]
        self.assertIn("missing visual_truth", run_lint(plan)[1]["treatment"][0])
        del plan["treatment"]
        self.assertIn("no treatment", run_lint(plan)[1]["treatment"][0])

    def test_rushed_text_fails_reading_time(self):
        plan = load_plan()
        plan["scenes"][1]["text"][0]["out"] = 1.0
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.reading_time"].passed)

    def test_dead_stretch_fails_pattern_interrupts(self):
        plan = load_plan()
        plan["scenes"][3]["events"] = []
        plan["scenes"][3]["text"][0]["in"] = 0.0
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.pattern_interrupts"].passed)

    def test_cliche_copy_fails(self):
        plan = load_plan()
        plan["share"]["linkedin"] = "Excited to share Shipcast, a game-changer for teams."
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.banned_phrases"].passed)

    def test_missing_cta_and_unsafe_text(self):
        plan = load_plan()
        plan["scenes"][4]["text"] = [{"content": "Thanks for watching", "in": 0.3, "out": 4.0,
                                      "box": [0.1, 0.85, 0.76, 0.1]}]
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.cta"].passed)
        self.assertFalse(checks["plan.safe_zone"].passed)

    def test_ungrounded_lexicon_fails(self):
        plan = load_plan()
        plan["project"]["lexicon"].append("blockchain")
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.lexicon_grounded"].passed)

    def test_duration_sum_must_match(self):
        plan = load_plan()
        plan["duration_s"] = 24
        checks, _ = run_lint(plan)
        self.assertFalse(checks["plan.duration_sum"].passed)

    def test_hook_score_rewards_brevity_and_grounding(self):
        base = {"text": "Your git log, now a podcast", "scores": dict.fromkeys(
            ("curiosity", "specificity", "stakes", "visual_proof", "pattern_break"), 4)}
        generic = copy.deepcopy(base) | {"text": "This tool will change how you work forever and ever"}
        self.assertGreater(hook_score(base, ["git log"], set()), hook_score(generic, ["git log"], set()))


class CaptionTest(unittest.TestCase):
    def test_variant_captions_round_trip_and_validate(self):
        plan = load_plan()
        cues = variant_cues(plan, "B")
        self.assertEqual(cues[0].lines, ["500 commits. One episode. 40 seconds."])
        parsed = captions.parse_srt(captions.render_srt(cues))
        self.assertEqual(len(parsed), len(cues))
        self.assertAlmostEqual(parsed[-1].end, 20.0, places=3)

    def test_bad_srt_is_flagged(self):
        tmp = FIXTURES / "_bad.srt"
        tmp.write_text("1\n00:00:01,000 --> 00:00:01,200\n" + "x" * 60 + "\n")
        try:
            checks = {c.id: c for c in captions.validate(tmp, 10.0)}
        finally:
            tmp.unlink()
        self.assertTrue(checks["captions.present"].passed)
        self.assertFalse(checks["captions.readability"].passed)


if __name__ == "__main__":
    unittest.main()
