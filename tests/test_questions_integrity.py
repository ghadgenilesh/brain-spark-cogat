"""
Data-integrity tests for questions.json
========================================
All tests are pure Python (no browser, no network).
Run with:  pytest tests/test_questions_integrity.py -v
"""
import re
from collections import Counter, defaultdict

import pytest

pytestmark = pytest.mark.unit

# ── Constants mirrored from gen_questions.py ──────────────────────────────

VALID_GRADES = {"K", "1", "2", "3", "4", "5", "6", "7", "8"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_BATTERIES = {"verbal", "quantitative", "non-verbal"}
VALID_TYPES = {
    "verbal-analogies",
    "verbal-classification",
    "sentence-completion",
    "number-series",
    "number-analogies",
    "number-puzzles",
    "figure-matrices",
    "paper-folding",
    "figure-classification",
}
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
OPTION_LABELS = ["A", "B", "C", "D"]
ID_PATTERN = re.compile(r"^GEN\d{5}$")  # used by generator tests; see _id_is_valid() for data tests
NON_VERBAL_TYPES = {"figure-matrices", "paper-folding", "figure-classification"}

REQUIRED_FIELDS = {"id", "grade", "battery", "type", "difficulty", "text", "options", "answer", "explanation", "tags"}

# Both the legacy Q##### format and the generator GEN##### format are acceptable.
# The pattern is determined at load time from the actual data.
ID_PATTERNS = [
    re.compile(r"^GEN\d{5}$"),
    re.compile(r"^Q\d{5}$"),
]


def _id_is_valid(id_str: str) -> bool:
    return any(p.match(id_str) for p in ID_PATTERNS)

# ── Individual question validators ────────────────────────────────────────


def _validate_one(q, idx):
    """Return a list of error strings for a single question dict."""
    errors = []
    qid = q.get("id", f"[index {idx}]")
    prefix = f"Question {qid}"

    # Required fields present
    missing = REQUIRED_FIELDS - set(q.keys())
    if missing:
        errors.append(f"{prefix}: missing fields {sorted(missing)}")
        return errors  # nothing else meaningful to check

    # ID format
    if not _id_is_valid(str(q["id"])):
        errors.append(f"{prefix}: id does not match GEN##### or Q##### pattern: {q['id']!r}")

    # Grade
    if q["grade"] not in VALID_GRADES:
        errors.append(f"{prefix}: invalid grade {q['grade']!r}")

    # Difficulty
    if q["difficulty"] not in VALID_DIFFICULTIES:
        errors.append(f"{prefix}: invalid difficulty {q['difficulty']!r}")

    # Battery
    if q["battery"] not in VALID_BATTERIES:
        errors.append(f"{prefix}: invalid battery {q['battery']!r}")

    # Type
    if q["type"] not in VALID_TYPES:
        errors.append(f"{prefix}: invalid type {q['type']!r}")

    # Battery-type consistency
    if q["type"] in BATTERY_MAP and q["battery"] != BATTERY_MAP[q["type"]]:
        errors.append(
            f"{prefix}: battery {q['battery']!r} does not match type {q['type']!r} "
            f"(expected {BATTERY_MAP[q['type']]!r})"
        )

    # Text non-empty
    if not isinstance(q["text"], str) or not q["text"].strip():
        errors.append(f"{prefix}: text is empty or not a string")

    # Explanation non-empty
    if not isinstance(q["explanation"], str) or not q["explanation"].strip():
        errors.append(f"{prefix}: explanation is empty or not a string")

    # Options
    opts = q["options"]
    if not isinstance(opts, list):
        errors.append(f"{prefix}: options is not a list")
    elif len(opts) != 4:
        errors.append(f"{prefix}: expected 4 options, got {len(opts)}")
    else:
        for i, opt in enumerate(opts):
            expected_label = OPTION_LABELS[i]
            if not isinstance(opt, dict):
                errors.append(f"{prefix}: option[{i}] is not a dict")
                continue
            if opt.get("label") != expected_label:
                errors.append(
                    f"{prefix}: option[{i}].label is {opt.get('label')!r}, expected {expected_label!r}"
                )
            if "text" not in opt:
                errors.append(f"{prefix}: option[{i}] missing 'text'")
            elif not isinstance(opt["text"], str) or not opt["text"].strip():
                errors.append(f"{prefix}: option[{i}].text is empty")

    # Answer index in bounds
    answer = q["answer"]
    if not isinstance(answer, int):
        errors.append(f"{prefix}: answer is not an int: {answer!r}")
    elif not (0 <= answer <= 3):
        errors.append(f"{prefix}: answer index {answer} out of range [0, 3]")

    # Tags: should contain grade, battery (the broad category), and difficulty
    tags = q.get("tags", [])
    if not isinstance(tags, list):
        errors.append(f"{prefix}: tags is not a list")
    else:
        if q["grade"] not in tags:
            errors.append(f"{prefix}: tags missing grade {q['grade']!r}: {tags}")
        if q["difficulty"] not in tags:
            errors.append(f"{prefix}: tags missing difficulty {q['difficulty']!r}: {tags}")

    return errors


# ── Session-level pre-computed data ──────────────────────────────────────


@pytest.fixture(scope="module")
def all_errors(questions):
    """Collect all per-question errors once for the module."""
    errs = []
    for idx, q in enumerate(questions):
        errs.extend(_validate_one(q, idx))
    return errs


# ── Tests ─────────────────────────────────────────────────────────────────


class TestRequiredFields:
    def test_no_missing_fields(self, questions, all_errors):
        missing_errors = [e for e in all_errors if "missing fields" in e]
        assert not missing_errors, f"{len(missing_errors)} questions have missing fields:\n" + "\n".join(missing_errors[:20])

    def test_no_extra_unexpected_keys(self, questions):
        allowed = REQUIRED_FIELDS | {"svg"}
        violations = []
        for q in questions:
            extra = set(q.keys()) - allowed
            if extra:
                violations.append(f"id={q.get('id')}: unexpected keys {sorted(extra)}")
        assert not violations, f"{len(violations)} questions have unexpected keys:\n" + "\n".join(violations[:20])


class TestIds:
    def test_all_ids_match_pattern(self, questions, all_errors):
        id_errors = [e for e in all_errors if "id does not match" in e]
        assert not id_errors, "\n".join(id_errors[:20])

    def test_no_duplicate_ids(self, questions):
        ids = [q.get("id") for q in questions]
        counts = Counter(ids)
        dupes = {k: v for k, v in counts.items() if v > 1}
        assert not dupes, f"Duplicate IDs found: {dupes}"

    def test_ids_are_sequential(self, questions):
        """IDs should have no gaps in their numeric part."""
        nums = []
        for q in questions:
            id_str = str(q.get("id", ""))
            if _id_is_valid(id_str):
                # Extract the numeric suffix regardless of prefix length
                numeric = re.search(r"\d+$", id_str)
                if numeric:
                    nums.append(int(numeric.group()))
        nums.sort()
        if nums:
            expected = list(range(1, nums[-1] + 1))
            missing = sorted(set(expected) - set(nums))
            assert not missing, (
                f"{len(missing)} ID numbers are missing (first 10): "
                + str(missing[:10])
            )


class TestEnumeratedFields:
    def test_valid_grades(self, questions, all_errors):
        grade_errors = [e for e in all_errors if "invalid grade" in e]
        assert not grade_errors, "\n".join(grade_errors[:20])

    def test_valid_difficulties(self, questions, all_errors):
        diff_errors = [e for e in all_errors if "invalid difficulty" in e]
        assert not diff_errors, "\n".join(diff_errors[:20])

    def test_valid_batteries(self, questions, all_errors):
        bat_errors = [e for e in all_errors if "invalid battery" in e]
        assert not bat_errors, "\n".join(bat_errors[:20])

    def test_valid_types(self, questions, all_errors):
        type_errors = [e for e in all_errors if "invalid type" in e]
        assert not type_errors, "\n".join(type_errors[:20])

    def test_battery_type_consistency(self, questions, all_errors):
        consistency_errors = [e for e in all_errors if "does not match type" in e]
        assert not consistency_errors, (
            f"{len(consistency_errors)} battery/type mismatches:\n" + "\n".join(consistency_errors[:20])
        )


class TestOptions:
    def test_all_questions_have_four_options(self, questions, all_errors):
        opt_errors = [e for e in all_errors if "expected 4 options" in e]
        assert not opt_errors, "\n".join(opt_errors[:20])

    def test_option_labels_are_abcd(self, questions, all_errors):
        label_errors = [e for e in all_errors if "option[" in e and ".label" in e]
        assert not label_errors, "\n".join(label_errors[:20])

    def test_option_texts_non_empty(self, questions, all_errors):
        text_errors = [e for e in all_errors if "option[" in e and ".text is empty" in e]
        assert not text_errors, "\n".join(text_errors[:20])

    def test_answer_index_in_bounds(self, questions, all_errors):
        ans_errors = [e for e in all_errors if "answer index" in e or "answer is not an int" in e]
        assert not ans_errors, "\n".join(ans_errors[:20])

    def test_correct_option_text_is_not_empty(self, questions):
        """The option pointed to by 'answer' must have a non-empty text."""
        violations = []
        for q in questions:
            opts = q.get("options", [])
            ans = q.get("answer")
            if isinstance(ans, int) and 0 <= ans < len(opts):
                if not opts[ans].get("text", "").strip():
                    violations.append(q.get("id"))
        assert not violations, f"Correct option text is empty for: {violations[:20]}"


class TestTextContent:
    def test_question_texts_non_empty(self, questions, all_errors):
        text_errors = [e for e in all_errors if "text is empty" in e and "option" not in e]
        assert not text_errors, "\n".join(text_errors[:20])

    def test_explanations_non_empty(self, questions, all_errors):
        expl_errors = [e for e in all_errors if "explanation is empty" in e]
        assert not expl_errors, "\n".join(expl_errors[:20])

    def test_no_raw_template_blanks_in_answers(self, questions):
        """The correct answer option should never contain the blank placeholder ___."""
        violations = []
        for q in questions:
            opts = q.get("options", [])
            ans = q.get("answer")
            if isinstance(ans, int) and 0 <= ans < len(opts):
                if "___" in opts[ans].get("text", ""):
                    violations.append(q.get("id"))
        assert not violations, (
            f"Answer option contains '___' placeholder in: {violations[:10]}"
        )

    def test_duplicate_question_texts(self, questions):
        """Exact duplicate question text indicates copy-paste error."""
        texts = [q.get("text", "") for q in questions]
        counts = Counter(texts)
        dupes = {t: v for t, v in counts.items() if v > 1 and t}
        # Warn only — variants are intentional, but flag egregious duplicates (>5 identical)
        severe = {t: v for t, v in dupes.items() if v > 5}
        assert not severe, (
            f"{len(severe)} question texts appear more than 5 times:\n"
            + "\n".join(f"  ({v}x) {t[:80]!r}" for t, v in list(severe.items())[:10])
        )


class TestTags:
    def test_tags_contain_grade(self, questions, all_errors):
        tag_errors = [e for e in all_errors if "tags missing grade" in e]
        assert not tag_errors, "\n".join(tag_errors[:20])

    def test_tags_contain_difficulty(self, questions, all_errors):
        tag_errors = [e for e in all_errors if "tags missing difficulty" in e]
        assert not tag_errors, "\n".join(tag_errors[:20])


class TestCoverageMatrix:
    """Every (grade × battery × difficulty) cell must have at least one question."""

    def test_all_grade_battery_difficulty_combos_covered(self, questions):
        present = {
            (q["grade"], q["battery"], q["difficulty"])
            for q in questions
            if q.get("grade") in VALID_GRADES
            and q.get("battery") in VALID_BATTERIES
            and q.get("difficulty") in VALID_DIFFICULTIES
        }
        missing = []
        for grade in VALID_GRADES:
            for battery in VALID_BATTERIES:
                for diff in VALID_DIFFICULTIES:
                    if (grade, battery, diff) not in present:
                        missing.append((grade, battery, diff))
        assert not missing, (
            f"{len(missing)} grade/battery/difficulty combinations have zero questions:\n"
            + "\n".join(f"  grade={g} battery={b} difficulty={d}" for g, b, d in sorted(missing))
        )

    def test_all_types_covered(self, questions):
        present_types = {q.get("type") for q in questions}
        missing = VALID_TYPES - present_types
        assert not missing, f"These question types have no questions: {sorted(missing)}"

    def test_minimum_questions_per_battery(self, questions):
        """Each battery should have a reasonable number of questions."""
        counts = Counter(q.get("battery") for q in questions)
        for battery in VALID_BATTERIES:
            assert counts[battery] >= 10, (
                f"Battery {battery!r} has only {counts[battery]} questions (expected ≥ 10)"
            )

    def test_minimum_questions_per_grade(self, questions):
        counts = Counter(q.get("grade") for q in questions)
        for grade in VALID_GRADES:
            assert counts[grade] >= 3, (
                f"Grade {grade!r} has only {counts[grade]} questions (expected ≥ 3)"
            )
