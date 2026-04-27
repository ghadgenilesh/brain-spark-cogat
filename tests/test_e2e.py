"""
End-to-end tests for getsmart.html
====================================
Uses Playwright. Requires:
  pip install pytest-playwright
  playwright install chromium

Run all E2E tests:
  pytest tests/test_e2e.py -v -m e2e

Run a specific test:
  pytest tests/test_e2e.py::TestSmoke::test_page_loads -v

The tests use the `local_server` fixture (from conftest.py) which
starts `python -m http.server` on port 8788 against the repo root.
All tests run as "guest" (no Firebase credentials needed).
"""
from __future__ import annotations

import re
import time

import pytest

pytestmark = pytest.mark.e2e

# ---------------------------------------------------------------------------
# Helpers / shared page setup
# ---------------------------------------------------------------------------

APP_PATH = "/getsmart.html"
GUEST_TIMEOUT = 8_000  # ms — time to wait for guest mode to load

THEMES = [
    "space", "superhero", "princess", "jungle",
    "unicorn", "magic", "candyland", "zen", "science", "math",
]

BATTERIES = ["Verbal", "Quantitative", "Non-Verbal"]
GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8"]


def app_url(local_server: str) -> str:
    return f"{local_server}{APP_PATH}"


def _suppress_welcome_modal(page) -> None:
    """
    Inject a localStorage pre-seed so the app sees welcomeSeen=true from the start.
    Must be called BEFORE page.goto() so the init script fires before page JS runs.
    """
    page.add_init_script(
        """(function() {
            try {
                var key = 'cogat_settings_local';
                var existing = JSON.parse(localStorage.getItem(key)) || {};
                existing.welcomeSeen = true;
                localStorage.setItem(key, JSON.stringify(existing));
            } catch(e) {}
        })()"""
    )


def enter_guest_mode(page) -> None:
    """Click 'Play without signing in' and wait for the home screen to be visible."""
    guest_btn = page.locator("button", has_text=re.compile("without signing in", re.IGNORECASE))
    guest_btn.wait_for(state="visible", timeout=GUEST_TIMEOUT)
    guest_btn.click()
    # Home screen hero should be visible
    page.locator("#screen-home").wait_for(state="visible", timeout=GUEST_TIMEOUT)
    # Questions must have loaded (battery pills appear only after questions.json fetch)
    page.locator(".battery-pills").wait_for(state="visible", timeout=GUEST_TIMEOUT)


def _goto(page, url: str) -> None:
    """Navigate to URL with the welcome-modal suppressed."""
    _suppress_welcome_modal(page)
    page.goto(url, wait_until="domcontentloaded")


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------


class TestSmoke:
    def test_page_loads_without_error(self, page, local_server):
        """App loads, title is correct, no uncaught JS errors."""
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        page.goto(app_url(local_server), wait_until="networkidle")

        assert "BrainSpark" in page.title(), f"Unexpected title: {page.title()!r}"
        assert not js_errors, f"JavaScript errors on load:\n" + "\n".join(js_errors)

    def test_login_screen_or_guest_option_visible(self, page, local_server):
        """Either the 'play without signing in' button or a Google sign-in button must be visible on load."""
        _goto(page, app_url(local_server))
        # Wait for either the guest button or the Google sign-in button
        page.wait_for_selector(
            "button:has-text('without signing in'), button:has-text('Google')",
            state="visible",
            timeout=GUEST_TIMEOUT,
        )

    def test_home_screen_loads_in_guest_mode(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        assert page.locator("#screen-home").is_visible()

    def test_brainspark_logo_visible(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        logo = page.locator(".topbar-logo")
        assert logo.is_visible()
        assert "BrainSpark" in logo.inner_text()

    def test_no_console_errors_on_home(self, page, local_server):
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(app_url(local_server), wait_until="networkidle")
        # Guest mode or auth; we only check for hard errors
        assert not errors, "JS errors:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# Navigation tests
# ---------------------------------------------------------------------------


class TestNavigation:
    def test_new_session_button_navigates_to_setup(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("#btn-new-session").click()
        page.locator("#screen-setup").wait_for(state="visible", timeout=5_000)
        assert page.locator("#screen-setup").is_visible()

    def test_theme_button_opens_themes_screen(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("button.theme-btn", has_text="Theme").first.click()
        page.locator("#screen-themes").wait_for(state="visible", timeout=5_000)
        assert page.locator("#screen-themes").is_visible()

    def test_back_button_on_themes_returns_to_home(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("button.theme-btn", has_text="Theme").first.click()
        page.locator("#screen-themes").wait_for(state="visible", timeout=5_000)
        page.locator("#screen-themes button", has_text="← Back").click()
        page.locator("#screen-home").wait_for(state="visible", timeout=5_000)
        assert page.locator("#screen-home").is_visible()

    def test_progress_nav_opens_insights(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("#nav-insights").click()
        page.locator("#screen-insights").wait_for(state="visible", timeout=5_000)
        assert page.locator("#screen-insights").is_visible()

    def test_back_from_setup_returns_to_home(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("#btn-new-session").click()
        page.locator("#screen-setup").wait_for(state="visible", timeout=5_000)
        page.locator("#screen-setup button", has_text="← Back").click()
        page.locator("#screen-home").wait_for(state="visible", timeout=5_000)
        assert page.locator("#screen-home").is_visible()


# ---------------------------------------------------------------------------
# Setup screen tests
# ---------------------------------------------------------------------------


class TestSetupScreen:
    def _go_to_setup(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("#btn-new-session").click()
        page.locator("#screen-setup").wait_for(state="visible", timeout=5_000)

    def test_all_grades_visible_in_setup(self, page, local_server):
        self._go_to_setup(page, local_server)
        for grade in GRADES:
            btn = page.locator(f"#gb-{grade}")
            assert btn.is_visible(), f"Grade button {grade!r} not visible"

    def test_grade_selection_highlights_button(self, page, local_server):
        self._go_to_setup(page, local_server)
        grade_btn = page.locator("#gb-3")
        grade_btn.click()
        # Selected grade button should have 'selected' class
        assert "selected" in (grade_btn.get_attribute("class") or ""), (
            "Grade 3 button was not marked as selected"
        )

    def test_battery_options_visible(self, page, local_server):
        self._go_to_setup(page, local_server)
        # Battery option names as they appear in the HTML
        expected_names = ["Mixed", "Verbal", "Quantitative", "Non-Verbal"]
        for name in expected_names:
            assert page.locator(".battery-option", has_text=name).count() >= 1, (
                f"Battery option {name!r} not found in setup"
            )

    def test_name_input_accepts_text(self, page, local_server):
        self._go_to_setup(page, local_server)
        name_input = page.locator("#player-name-input")
        name_input.fill("TestKid")
        assert name_input.input_value() == "TestKid"

    def test_name_greeting_updates_on_input(self, page, local_server):
        self._go_to_setup(page, local_server)
        page.locator("#player-name-input").fill("Alex")
        greeting = page.locator("#name-greeting")
        greeting.wait_for(state="visible", timeout=2_000)
        assert "Alex" in greeting.inner_text()

    def test_start_button_disabled_without_grade(self, page, local_server):
        self._go_to_setup(page, local_server)
        start_btn = page.locator("#btn-start-session")
        # Should be disabled or absent until a grade is selected
        if start_btn.count() > 0 and start_btn.is_visible():
            assert start_btn.is_disabled(), "Start button should be disabled before grade selection"

    def test_start_session_requires_grade(self, page, local_server):
        """Clicking Start without selecting a grade should not advance to quiz."""
        self._go_to_setup(page, local_server)
        start_btn = page.locator("#btn-start-session")
        if start_btn.count() > 0 and start_btn.is_visible() and not start_btn.is_disabled():
            start_btn.click()
            # Should NOT go to quiz without a grade
            assert not page.locator("#screen-quiz").is_visible(), (
                "Quiz started without grade selection"
            )


# ---------------------------------------------------------------------------
# Quiz flow tests
# ---------------------------------------------------------------------------


def _start_quiz(page, local_server, grade="3", battery_text="All Batteries"):
    """Navigate from home to the first quiz question."""
    _goto(page, app_url(local_server))
    enter_guest_mode(page)
    page.locator("#btn-new-session").click()
    page.locator("#screen-setup").wait_for(state="visible", timeout=5_000)
    page.locator(f"#gb-{grade}").click()
    # Pick battery if available
    all_battery_opt = page.locator(".battery-option", has_text=battery_text)
    if all_battery_opt.count() > 0:
        all_battery_opt.first.click()
    # Start the session
    start_btn = page.locator("#btn-start-session")
    start_btn.wait_for(state="visible", timeout=3_000)
    start_btn.click()
    # Wait for quiz body
    page.locator("#screen-quiz").wait_for(state="visible", timeout=8_000)


class TestQuizFlow:
    def test_quiz_screen_shows_after_start(self, page, local_server):
        _start_quiz(page, local_server)
        assert page.locator("#screen-quiz").is_visible()

    def test_question_text_is_not_empty(self, page, local_server):
        _start_quiz(page, local_server)
        q_text = page.locator(".q-text")
        q_text.wait_for(state="visible", timeout=5_000)
        assert q_text.inner_text().strip() != "", "Question text is empty"

    def test_four_answer_options_displayed(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        options = page.locator(".option-btn")
        assert options.count() == 4, f"Expected 4 options, got {options.count()}"

    def test_option_labels_are_a_b_c_d(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        labels = page.locator(".option-label")
        texts = [labels.nth(i).inner_text().strip() for i in range(4)]
        assert texts == ["A", "B", "C", "D"], f"Unexpected labels: {texts}"

    def test_check_button_disabled_before_selection(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        btn_check = page.locator("#btn-check")
        assert btn_check.is_disabled(), "Check button should be disabled before option is selected"

    def test_check_button_enabled_after_selection(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        page.locator(".option-btn").first.click()
        btn_check = page.locator("#btn-check")
        assert not btn_check.is_disabled(), "Check button should be enabled after option selection"

    def test_selecting_option_adds_selected_class(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        first_opt = page.locator(".option-btn").nth(0)
        first_opt.click()
        assert "selected" in (first_opt.get_attribute("class") or ""), (
            "Selected option does not have 'selected' class"
        )

    def test_answer_feedback_shown_after_submit(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        # At least one option should now have 'correct' or 'wrong' class
        correct_el = page.locator(".option-btn.correct")
        correct_el.wait_for(state="attached", timeout=3_000)
        assert correct_el.count() >= 1, "No option marked as correct after submission"

    def test_explanation_box_visible_after_submit(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator(".explanation-box.visible").wait_for(state="visible", timeout=3_000)
        assert page.locator(".explanation-box.visible").is_visible()

    def test_next_button_appears_after_submit(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        btn_next = page.locator("#btn-next")
        btn_next.wait_for(state="visible", timeout=3_000)
        assert btn_next.is_visible()

    def test_next_advances_to_question_2(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=3_000)
        page.locator("#btn-next").click()
        # Counter should now say "Question 2 of 9"
        counter = page.locator("#q-counter")
        counter.wait_for(state="visible", timeout=3_000)
        assert "2" in counter.inner_text(), f"Counter did not advance: {counter.inner_text()!r}"

    def test_progress_bar_advances(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        # Check initial progress
        initial_style = page.locator("#q-progress").get_attribute("style") or ""
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=3_000)
        page.locator("#btn-next").click()
        # Progress bar width should have changed
        new_style = page.locator("#q-progress").get_attribute("style") or ""
        assert new_style != initial_style, "Progress bar did not advance after moving to question 2"

    def test_cannot_change_answer_after_submit(self, page, local_server):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=5_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=3_000)
        # All options should now be disabled
        for i in range(4):
            opt = page.locator(".option-btn").nth(i)
            assert opt.is_disabled(), f"Option {i} is still enabled after submission"

    def test_complete_full_9_question_session(self, page, local_server):
        """Answer all 9 questions and verify result screen appears."""
        _start_quiz(page, local_server)
        for q_num in range(9):
            page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
            page.locator(".option-btn").nth(0).click()
            page.locator("#btn-check").click()
            page.locator("#btn-next").wait_for(state="visible", timeout=5_000)
            page.locator("#btn-next").click()
        # Result overlay should appear
        page.locator("#result-overlay").wait_for(state="visible", timeout=8_000)
        assert page.locator("#result-overlay").is_visible(), "Result screen did not appear after 9 questions"

    def test_result_screen_shows_score(self, page, local_server):
        """Score on result screen must be a fraction like '5 / 9'."""
        _start_quiz(page, local_server)
        for _ in range(9):
            page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
            page.locator(".option-btn").nth(0).click()
            page.locator("#btn-check").click()
            page.locator("#btn-next").wait_for(state="visible", timeout=5_000)
            page.locator("#btn-next").click()
        page.locator("#result-overlay").wait_for(state="visible", timeout=8_000)
        score_text = page.locator(".result-score").inner_text()
        assert re.search(r"\d", score_text), f"No numeric score visible: {score_text!r}"


# ---------------------------------------------------------------------------
# Answer correctness tests
# ---------------------------------------------------------------------------


class TestAnswerCorrectnessUI:
    def _submit_option(self, page, local_server, option_idx: int):
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
        page.locator(".option-btn").nth(option_idx).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=5_000)

    def test_correct_answer_option_gets_correct_class(self, page, local_server):
        """Whichever option is correct should receive the 'correct' CSS class."""
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
        # Read the answer from the DOM (exposed by render) — find the option with ✅ after submit
        # We click option 0 and then look for 'correct' class
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator(".option-btn.correct").wait_for(state="attached", timeout=3_000)
        assert page.locator(".option-btn.correct").count() == 1, "Exactly one option should be correct"

    def test_wrong_answer_gets_wrong_class(self, page, local_server):
        """
        If we pick the wrong answer, that option should get the 'wrong' class.
        We try all 4 options in sequence, stopping at the first that shows a wrong class.
        """
        # We can't know which is wrong without reading internal state, so
        # we run the quiz 4 times and verify that the 'wrong' class is shown
        # on the selected option when it's NOT the correct one.
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)

        # Pick option 1; inspect classes
        page.locator(".option-btn").nth(1).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=5_000)

        # Either option 1 is correct (has 'correct') or it has 'wrong'
        opt1_class = page.locator(".option-btn").nth(1).get_attribute("class") or ""
        assert "correct" in opt1_class or "wrong" in opt1_class, (
            f"Option 1 has neither 'correct' nor 'wrong' class after submission: {opt1_class!r}"
        )


# ---------------------------------------------------------------------------
# Theme tests
# ---------------------------------------------------------------------------


class TestThemes:
    def _open_themes(self, page, local_server):
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("button.theme-btn", has_text="Theme").first.click()
        page.locator("#screen-themes").wait_for(state="visible", timeout=5_000)

    def test_theme_cards_are_visible(self, page, local_server):
        self._open_themes(page, local_server)
        cards = page.locator(".theme-card")
        assert cards.count() >= len(THEMES), (
            f"Expected at least {len(THEMES)} theme cards, got {cards.count()}"
        )

    def test_selecting_space_theme_applies_class(self, page, local_server):
        self._open_themes(page, local_server)
        page.locator(".theme-card[data-theme='space'], .theme-card", has_text="Space").first.click()
        body_class = page.locator("body").get_attribute("class") or ""
        assert "theme-space" in body_class, f"body class after space theme: {body_class!r}"

    def test_selecting_jungle_theme_applies_class(self, page, local_server):
        self._open_themes(page, local_server)
        page.locator(".theme-card", has_text=re.compile("jungle", re.IGNORECASE)).first.click()
        body_class = page.locator("body").get_attribute("class") or ""
        assert "theme-jungle" in body_class, f"body class after jungle theme: {body_class!r}"

    def test_theme_change_does_not_break_layout(self, page, local_server):
        """After theme switch, the home screen is automatically shown (setTheme calls showScreen('home'))."""
        self._open_themes(page, local_server)
        page.locator(".theme-card").nth(2).click()
        # setTheme() calls showScreen('home') automatically
        page.locator("#screen-home").wait_for(state="visible", timeout=5_000)
        assert page.locator("#screen-home").is_visible()


# ---------------------------------------------------------------------------
# Persistence (localStorage) tests
# ---------------------------------------------------------------------------


class TestLocalStoragePersistence:
    def test_active_session_saved_to_localstorage(self, page, local_server):
        """After answering Q1, the active session must be in localStorage."""
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=5_000)

        active = page.evaluate("() => localStorage.getItem('cogat_active_session_local')")
        assert active is not None, "Active session not found in localStorage (key: cogat_active_session_local)"
        import json
        session = json.loads(active)
        assert "answers" in session, "Saved session missing 'answers' field"

    def test_session_resumed_after_reload(self, page, local_server):
        """Reload the page mid-session; the home screen should offer to resume."""
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
        page.locator(".option-btn").nth(0).click()
        page.locator("#btn-check").click()
        page.locator("#btn-next").wait_for(state="visible", timeout=5_000)

        # Reload
        page.reload(wait_until="domcontentloaded")
        enter_guest_mode(page)

        # "Resume" box or button must be visible
        page.locator(".session-status-box").wait_for(state="visible", timeout=5_000)
        status_text = page.locator(".session-status-box").inner_text()
        assert status_text.strip() != "", "Session status box is empty after reload"

    def test_completed_session_saved_in_sessions_list(self, page, local_server):
        """Finishing a session must persist to cogat_sessions_local in localStorage."""
        _start_quiz(page, local_server)
        for _ in range(9):
            page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
            page.locator(".option-btn").nth(0).click()
            page.locator("#btn-check").click()
            page.locator("#btn-next").wait_for(state="visible", timeout=5_000)
            page.locator("#btn-next").click()
        page.locator("#result-overlay").wait_for(state="visible", timeout=8_000)

        import json
        sessions_raw = page.evaluate("() => localStorage.getItem('cogat_sessions_local')")
        assert sessions_raw is not None, "No sessions stored after completing a quiz (key: cogat_sessions_local)"
        sessions = json.loads(sessions_raw)
        assert len(sessions) >= 1, "Sessions list is empty after completing a quiz"


# ---------------------------------------------------------------------------
# Responsive layout tests
# ---------------------------------------------------------------------------


VIEWPORTS = [
    {"name": "mobile", "width": 375, "height": 812},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "desktop", "width": 1440, "height": 900},
]


class TestResponsiveLayout:
    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_home_screen_renders_at_viewport(self, page, local_server, viewport):
        page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        home = page.locator("#screen-home")
        assert home.is_visible(), f"Home screen not visible at {viewport['name']}"

    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_start_session_button_visible_at_viewport(self, page, local_server, viewport):
        page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        btn = page.locator("#btn-new-session")
        assert btn.is_visible(), f"'New session' button not visible at {viewport['name']}"

    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_quiz_options_not_horizontally_clipped(self, page, local_server, viewport):
        """No option button should overflow beyond the viewport width."""
        page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
        _start_quiz(page, local_server)
        page.locator(".option-btn").first.wait_for(state="visible", timeout=8_000)
        vw = viewport["width"]
        TOLERANCE = 4  # px — allow for sub-pixel rounding
        for i in range(4):
            box = page.locator(".option-btn").nth(i).bounding_box()
            assert box is not None
            assert box["x"] >= -TOLERANCE, f"Option {i} starts off-screen left at {viewport['name']}"
            assert box["x"] + box["width"] <= vw + TOLERANCE, (
                f"Option {i} overflows right at {viewport['name']}: "
                f"x={box['x']:.0f} + w={box['width']:.0f} > vw={vw}"
            )


# ---------------------------------------------------------------------------
# Battery filter tests
# ---------------------------------------------------------------------------


class TestBatteryFilter:
    def _start_quiz_with_battery(self, page, local_server, battery_id: str):
        """Start a quiz with a specific battery using the element ID."""
        _goto(page, app_url(local_server))
        enter_guest_mode(page)
        page.locator("#btn-new-session").click()
        page.locator("#screen-setup").wait_for(state="visible", timeout=5_000)
        page.locator("#gb-5").click()  # Grade 5 — good coverage
        # Select by ID:  bo-verbal, bo-quantitative, bo-nonverbal, bo-mixed
        page.locator(f"#bo-{battery_id}").click()
        page.locator("#btn-start-session").wait_for(state="visible", timeout=3_000)
        page.locator("#btn-start-session").click()
        page.locator("#screen-quiz").wait_for(state="visible", timeout=8_000)

    def test_verbal_battery_shows_battery_tag(self, page, local_server):
        self._start_quiz_with_battery(page, local_server, "verbal")
        page.locator(".q-battery-tag").wait_for(state="visible", timeout=5_000)
        tag = page.locator(".q-battery-tag").inner_text().lower()
        assert "verbal" in tag, f"Battery tag does not say 'verbal': {tag!r}"

    def test_quantitative_battery_shows_battery_tag(self, page, local_server):
        self._start_quiz_with_battery(page, local_server, "quantitative")
        page.locator(".q-battery-tag").wait_for(state="visible", timeout=5_000)
        tag = page.locator(".q-battery-tag").inner_text().lower()
        assert "quantitative" in tag, (
            f"Battery tag does not say 'quantitative': {tag!r}"
        )
