"""
Tests for harness.core.governance — the design elevation scoring gate.

Run with: python -m unittest harness.tests.test_governance -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from harness.core.governance import (
    ElevationSignal,
    ElevationScorer,
    GovernanceGate,
    DEFAULT_ELEVATION_WEIGHTS,
    HARD_FAIL_FLOOR,
)
from harness.memory import MemoryStore, MemoryCategory


def full_signals(**overrides) -> list:
    """Helper: build a full set of signals for every default weight
    dimension, all at a healthy score by default, with overrides."""
    base = {name: 85.0 for name in DEFAULT_ELEVATION_WEIGHTS}
    base.update(overrides)
    return [ElevationSignal(name=name, score=score) for name, score in base.items()]


class TestElevationScorer(unittest.TestCase):

    def test_all_high_signals_score_high(self):
        scorer = ElevationScorer()
        result = scorer.score(full_signals())
        self.assertGreaterEqual(result.total_score, 80.0)
        self.assertEqual(result.hard_fails, [])

    def test_missing_signal_is_treated_as_zero_and_hard_fail(self):
        scorer = ElevationScorer()
        signals = full_signals()
        # Drop the accessibility signal entirely
        signals = [s for s in signals if s.name != "accessibility"]

        result = scorer.score(signals)
        self.assertLess(result.total_score, 85.0)
        self.assertTrue(any("missing signal: accessibility" in f for f in result.hard_fails))

    def test_signal_below_floor_is_hard_fail_even_if_total_high(self):
        scorer = ElevationScorer()
        # brand_alignment has the highest weight (30) — max out everything
        # else so the weighted total stays high, but tank accessibility.
        signals = full_signals(accessibility=10.0)

        result = scorer.score(signals)
        self.assertTrue(any("accessibility below floor" in f for f in result.hard_fails))
        self.assertLess(HARD_FAIL_FLOOR, 85.0)  # sanity check on fixture assumptions

    def test_weighted_breakdown_sums_to_total_score(self):
        scorer = ElevationScorer()
        result = scorer.score(full_signals())
        self.assertAlmostEqual(sum(result.weighted_breakdown.values()), result.total_score, delta=0.5)

    def test_custom_weights_are_respected(self):
        custom_weights = {"brand_alignment": 100.0}
        scorer = ElevationScorer(weights=custom_weights)
        result = scorer.score([ElevationSignal(name="brand_alignment", score=90.0)])
        self.assertAlmostEqual(result.total_score, 90.0, delta=0.01)

    def test_invalid_signal_score_raises(self):
        with self.assertRaises(ValueError):
            ElevationSignal(name="brand_alignment", score=150.0)


class TestGovernanceGate(unittest.TestCase):

    def test_high_quality_redesign_passes_gate(self):
        gate = GovernanceGate(threshold=75.0)
        result = gate.evaluate(full_signals(), task_id="t1", subject="acme.com")
        self.assertTrue(result.passed)

    def test_low_score_is_blocked_even_without_hard_fail(self):
        gate = GovernanceGate(threshold=75.0)
        # All signals above the hard-fail floor (40) but below threshold (75)
        result = gate.evaluate(full_signals(**{k: 50.0 for k in DEFAULT_ELEVATION_WEIGHTS}),
                                task_id="t2", subject="acme.com")
        self.assertFalse(result.passed)
        self.assertEqual(result.hard_fails, [])  # blocked purely on score, not hard-fail

    def test_hard_fail_blocks_even_with_high_total_score(self):
        gate = GovernanceGate(threshold=75.0)
        # Everything maxed except one dimension tanked below the floor —
        # this is the "cannot buy your way out of broken accessibility"
        # case from ARCHITECTURE_PRINCIPLES.md §5.
        signals = full_signals(accessibility=5.0)
        for s in signals:
            if s.name != "accessibility":
                s.score = 100.0
        result = gate.evaluate(signals, task_id="t3", subject="acme.com")
        self.assertFalse(result.passed)
        self.assertTrue(any("accessibility" in f for f in result.hard_fails))

    def test_threshold_is_configurable(self):
        lenient_gate = GovernanceGate(threshold=10.0)
        strict_gate = GovernanceGate(threshold=95.0)

        signals = full_signals(**{k: 60.0 for k in DEFAULT_ELEVATION_WEIGHTS})

        self.assertTrue(lenient_gate.evaluate(signals, subject="a").passed)
        self.assertFalse(strict_gate.evaluate(signals, subject="a").passed)


class TestGovernanceGateMemoryIntegration(unittest.TestCase):
    """ARCHITECTURE_PRINCIPLES.md §4/§10: every evaluation, pass or fail,
    must be recorded — this is the auditable history future scoring
    recalibration needs."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_gov_memory_test_")
        self.memory = MemoryStore(path=str(Path(self.tmp_dir) / "memory.jsonl"))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_passed_evaluation_is_recorded(self):
        gate = GovernanceGate(threshold=75.0, memory=self.memory)
        gate.evaluate(full_signals(), task_id="t1", subject="acme.com")

        records = self.memory.recall(subject="acme.com", category=MemoryCategory.GATE_EVALUATION)
        self.assertEqual(len(records), 1)
        self.assertIn("passed", records[0].tags)

    def test_blocked_evaluation_is_recorded(self):
        gate = GovernanceGate(threshold=95.0, memory=self.memory)
        gate.evaluate(full_signals(**{k: 60.0 for k in DEFAULT_ELEVATION_WEIGHTS}),
                      task_id="t2", subject="acme.com")

        records = self.memory.recall(subject="acme.com", category=MemoryCategory.GATE_EVALUATION)
        self.assertEqual(len(records), 1)
        self.assertIn("blocked", records[0].tags)

    def test_can_disable_memory_recording(self):
        gate = GovernanceGate(threshold=75.0, memory=self.memory, record_to_memory=False)
        gate.evaluate(full_signals(), task_id="t3", subject="acme.com")

        records = self.memory.recall(subject="acme.com", category=MemoryCategory.GATE_EVALUATION)
        self.assertEqual(len(records), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
