"""
Generator unit tests for gen_questions.py
==========================================
Validates the output of the generator script itself, independent of
whatever is currently committed in questions.json.

Run with:  pytest tests/test_gen_questions.py -v
(First run is slow — it executes the generator. Results are cached
 for the rest of the pytest session via the `generated_questions` fixture
 defined in conftest.py.)
"""
from collections import Counter
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.slow]

REPO_ROOT = Path(__file__).parent.parent

VALID_GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8"]
VALID_DIFFICULTIES = ["easy", "medium", "hard"]
VALID_TYPES = [
    "verbal-analogies",
    "verbal-classification",
    "sentence-completion",
    "number-series",
    "number-analogies",
    "number-puzzles",
    "figure-matrices",
    "paper-folding",
    "figure-classification",
]
BATTERY_MAP = {
    "verbal-analogies": "verbal",
    "verbal-classification": "verbal",
    "sentence-completion": "verbal",
    "number-series": "quantitative",
    "number-analogies": "quantitative",
    "number-puzzles": "quantitative",
    "figure-matrices": "non-verbal",
    "paper-folding": "non-verbal",
    "figure-classification": "non-verbal",
}


# ── Helpers ───────────────────────────────────────────────────────────────


def _battery_for(qtype):
    return BATTERY_MAP.get(qtype)


# ── Volume & uniqueness ────────────────────────────────────────────────────


class TestVolume:
    def test_generates_10000_questions(self, generated_questions):
        assert len(generated_questions) == 10_000, (
            f"Expected 10 000 questions, got {len(generated_questions)}"
        )

    def test_no_duplicate_ids(self, generated_questions):
        ids = [q["id"] for q in generated_questions]
        dupes = {k: v for k, v in Counter(ids).items() if v > 1}
        assert not dupes, f"Duplicate IDs: {dupes}"

    def test_ids_are_sequential_from_1(self, generated_questions):
        nums = sorted(int(q["id"][3:]) for q in generated_questions)
        assert nums[0] == 1, f"First ID number is {nums[0]}, expected 1"
        assert nums[-1] == len(generated_questions), (
            f"Last ID number is {nums[-1]}, expected {len(generated_questions)}"
        )
        gaps = [n for n, (a, b) in enumerate(zip(nums, nums[1:]), 1) if b - a != 1]
        assert not gaps, f"ID gaps at positions: {gaps[:10]}"

    def test_all_texts_unique(self, generated_questions):
        texts = [q["text"] for q in generated_questions]
        dupes = {t: v for t, v in Counter(texts).items() if v > 1}
        assert not dupes, (
            f"{len(dupes)} duplicate question texts found (first 5):\n"
            + "\n".join(f"  ({v}x) {t[:80]!r}" for t, v in list(dupes.items())[:5])
        )


# ── Schema compliance ──────────────────────────────────────────────────────


class TestSchema:
    REQUIRED = {"id", "grade", "battery", "type", "difficulty", "text", "svg", "options", "answer", "explanation", "tags"}

    def test_all_required_fields_present(self, generated_questions):
        violations = []
        for q in generated_questions:
            missing = self.REQUIRED - set(q.keys())
            if missing:
                violations.append(f"id={q.get('id')}: {sorted(missing)}")
        assert not violations, f"{len(violations)} schema violations:\n" + "\n".join(violations[:10])

    def test_option_count_is_four(self, generated_questions):
        bad = [q["id"] for q in generated_questions if len(q.get("options", [])) != 4]
        assert not bad, f"{len(bad)} questions do not have exactly 4 options: {bad[:10]}"

    def test_option_labels_abcd(self, generated_questions):
        expected = ["A", "B", "C", "D"]
        bad = []
        for q in generated_questions:
            labels = [o.get("label") for o in q.get("options", [])]
            if labels != expected:
                bad.append(q["id"])
        assert not bad, f"{len(bad)} questions have wrong option labels: {bad[:10]}"

    def test_answer_index_in_bounds(self, generated_questions):
        bad = [q["id"] for q in generated_questions if not isinstance(q.get("answer"), int) or not (0 <= q["answer"] <= 3)]
        assert not bad, f"{len(bad)} questions have out-of-bounds answer: {bad[:10]}"

    def test_texts_non_empty(self, generated_questions):
        bad = [q["id"] for q in generated_questions if not str(q.get("text", "")).strip()]
        assert not bad, f"{len(bad)} questions have empty text: {bad[:10]}"

    def test_explanations_non_empty(self, generated_questions):
        bad = [q["id"] for q in generated_questions if not str(q.get("explanation", "")).strip()]
        assert not bad, f"{len(bad)} questions have empty explanation: {bad[:10]}"


# ── Field value correctness ────────────────────────────────────────────────


class TestFieldValues:
    def test_all_grades_valid(self, generated_questions):
        bad = [q["id"] for q in generated_questions if q.get("grade") not in VALID_GRADES]
        assert not bad, f"Invalid grades in: {bad[:10]}"

    def test_all_difficulties_valid(self, generated_questions):
        bad = [q["id"] for q in generated_questions if q.get("difficulty") not in VALID_DIFFICULTIES]
        assert not bad, f"Invalid difficulties in: {bad[:10]}"

    def test_all_types_valid(self, generated_questions):
        bad = [q["id"] for q in generated_questions if q.get("type") not in VALID_TYPES]
        assert not bad, f"Invalid types in: {bad[:10]}"

    def test_battery_type_consistency(self, generated_questions):
        bad = []
        for q in generated_questions:
            expected = _battery_for(q.get("type", ""))
            if expected and q.get("battery") != expected:
                bad.append(f"id={q['id']} type={q['type']} battery={q['battery']} (expected {expected})")
        assert not bad, f"{len(bad)} battery/type mismatches:\n" + "\n".join(bad[:10])


# ── Coverage / distribution ────────────────────────────────────────────────


class TestDistribution:
    def test_all_grades_represented(self, generated_questions):
        present = {q["grade"] for q in generated_questions}
        missing = set(VALID_GRADES) - present
        assert not missing, f"Grades missing from output: {sorted(missing)}"

    def test_all_types_represented(self, generated_questions):
        present = {q["type"] for q in generated_questions}
        missing = set(VALID_TYPES) - present
        assert not missing, f"Types missing from output: {sorted(missing)}"

    def test_all_difficulties_represented(self, generated_questions):
        present = {q["difficulty"] for q in generated_questions}
        missing = set(VALID_DIFFICULTIES) - present
        assert not missing, f"Difficulties missing from output: {sorted(missing)}"

    def test_grade_distribution_is_balanced(self, generated_questions):
        """No grade should have fewer than 5% or more than 20% of all questions."""
        total = len(generated_questions)
        counts = Counter(q["grade"] for q in generated_questions)
        low_threshold = int(total * 0.05)
        high_threshold = int(total * 0.20)
        for grade in VALID_GRADES:
            n = counts[grade]
            assert n >= low_threshold, f"Grade {grade!r} underrepresented: {n} (< {low_threshold})"
            assert n <= high_threshold, f"Grade {grade!r} overrepresented: {n} (> {high_threshold})"

    def test_difficulty_distribution_is_balanced(self, generated_questions):
        """No difficulty should be less than 20% or more than 50%."""
        total = len(generated_questions)
        counts = Counter(q["difficulty"] for q in generated_questions)
        for diff in VALID_DIFFICULTIES:
            pct = counts[diff] / total
            assert pct >= 0.20, f"Difficulty {diff!r} underrepresented: {pct:.1%}"
            assert pct <= 0.50, f"Difficulty {diff!r} overrepresented: {pct:.1%}"

    def test_all_grade_type_combos_covered(self, generated_questions):
        present = {(q["grade"], q["type"]) for q in generated_questions}
        missing = [
            (g, t)
            for g in VALID_GRADES
            for t in VALID_TYPES
            if (g, t) not in present
        ]
        assert not missing, (
            f"{len(missing)} grade/type combinations not covered:\n"
            + "\n".join(f"  grade={g} type={t}" for g, t in sorted(missing))
        )


# ── Determinism ────────────────────────────────────────────────────────────


class TestDeterminism:
    """Running the generator twice with seed=42 must produce identical output."""

    def test_generator_is_deterministic(self, generated_questions, tmp_path):
        """Re-run the generator and compare the first 100 questions."""
        import json
        import sys

        src = (REPO_ROOT / "gen_questions.py").read_text(encoding="utf-8")
        patched = src.replace(
            'f"/Users/nilesh/Projects/brainspark/questions_{timestamp}.json"',
            f'str(tmp_path / f"questions_{{timestamp}}.json")',
        )
        ns2 = {"__name__": "__not_main__", "tmp_path": tmp_path}
        exec(compile(patched, "gen_questions.py", "exec"), ns2)  # noqa: S102

        files = list(tmp_path.glob("questions_*.json"))
        second_run = []
        with files[0].open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    second_run.append(json.loads(line))

        # Compare first 100 questions by id + text + answer
        for i in range(min(100, len(generated_questions), len(second_run))):
            q1, q2 = generated_questions[i], second_run[i]
            assert q1["id"] == q2["id"], f"Position {i}: id mismatch {q1['id']} vs {q2['id']}"
            assert q1["text"] == q2["text"], f"Position {i}: text mismatch"
            assert q1["answer"] == q2["answer"], f"Position {i}: answer mismatch"


# ── BATTERY_MAP completeness ───────────────────────────────────────────────


def test_battery_map_covers_all_types():
    """gen_questions.py BATTERY_MAP must include every type in VALID_TYPES."""
    missing = set(VALID_TYPES) - set(BATTERY_MAP.keys())
    assert not missing, f"BATTERY_MAP is missing types: {sorted(missing)}"


def test_battery_map_values_are_valid_batteries():
    invalid = {k: v for k, v in BATTERY_MAP.items() if v not in {"verbal", "quantitative", "non-verbal"}}
    assert not invalid, f"BATTERY_MAP has invalid battery values: {invalid}"
