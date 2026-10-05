"""Regression tests for the app/UI bugs (#2, #4-#10, #14), driven through Streamlit's AppTest."""
import random
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 30


@pytest.fixture
def app():
    return AppTest.from_file(APP_PATH, default_timeout=TIMEOUT).run()


def guess(at, value):
    """Type a guess and click Submit."""
    at.text_input[0].input(str(value))
    at.button[0].click().run()


def click_new_game(at):
    at.button[1].click().run()


def info_text(at):
    return at.info[0].value


# --- BUG #2: secret became a string on even attempts ------------------------

def test_bug2_even_attempt_hint_uses_numeric_comparison(app):
    app.session_state.secret = 50
    guess(app, 60)  # attempt 1
    guess(app, 9)   # attempt 2 (even): "9" > "50" as strings used to say Too High
    assert "HIGHER" in app.warning[0].value


def test_bug2_can_win_on_even_attempt(app):
    app.session_state.secret = 50
    guess(app, 60)  # attempt 1
    guess(app, 50)  # attempt 2 (even)
    assert app.session_state.status == "won"


# --- BUG #4: changing difficulty kept the old secret -------------------------

def test_bug4_switching_difficulty_picks_secret_in_new_range(app):
    app.session_state.secret = 87  # valid for Normal, impossible for Easy
    app.selectbox[0].select("Easy").run()
    assert 1 <= app.session_state.secret <= 20


# --- BUG #5: attempts started at 1 -------------------------------------------

def test_bug5_attempts_start_at_zero(app):
    assert app.session_state.attempts == 0
    assert "Attempts left: 8" in info_text(app)  # Normal allows 8


# --- BUG #6: invalid input used up an attempt --------------------------------

@pytest.mark.parametrize("bad_input", ["abc", "3.7", "", "999"])
def test_bug6_invalid_input_does_not_use_attempt(app, bad_input):
    guess(app, bad_input)
    assert app.session_state.attempts == 0
    assert app.session_state.history == []
    assert len(app.error) == 1


# --- BUG #7: "Attempts left" lagged one guess behind -------------------------

def test_bug7_attempts_left_updates_immediately_after_guess(app):
    app.session_state.secret = 50
    for expected_left in (7, 6, 5):
        guess(app, 10)
        # The displayed count must match the real state right after the guess,
        # not the value from before the guess was processed.
        displayed_left = 8 - app.session_state.attempts
        assert f"Attempts left: {displayed_left}" in info_text(app)
        assert f"Attempts left: {expected_left}" in info_text(app)


# --- BUG #8: New Game did not reset status -----------------------------------

def test_bug8_new_game_after_win_lets_you_play_again(app):
    app.session_state.secret = 50
    guess(app, 50)
    assert app.session_state.status == "won"

    click_new_game(app)
    assert app.session_state.status == "playing"


def test_bug8_new_game_after_loss_lets_you_play_again(app):
    app.session_state.secret = 50
    for _ in range(8):  # Normal: 8 attempts
        guess(app, 1)
    assert app.session_state.status == "lost"

    click_new_game(app)
    assert app.session_state.status == "playing"


# --- BUG #9: New Game ignored difficulty range ------------------------------

def test_bug9_new_game_uses_difficulty_range(app, monkeypatch):
    app.selectbox[0].select("Hard").run()
    calls = []

    def fake_randint(a, b):
        calls.append((a, b))
        return b

    monkeypatch.setattr(random, "randint", fake_randint)
    click_new_game(app)

    assert calls[-1] == (1, 200)
    assert app.session_state.secret == 200


# --- BUG #10: New Game only partly reset state ------------------------------

def test_bug10_new_game_resets_attempts_score_and_history(app):
    app.session_state.secret = 50
    guess(app, 10)
    guess(app, 20)
    assert app.session_state.attempts == 2

    click_new_game(app)
    assert app.session_state.attempts == 0
    assert app.session_state.score == 0
    assert app.session_state.history == []


def test_bug10_new_game_matches_fresh_load(app):
    fresh_attempts = app.session_state.attempts
    click_new_game(app)
    assert app.session_state.attempts == fresh_attempts


# --- BUG #14: prompt hardcoded "1 and 100" -----------------------------------

@pytest.mark.parametrize("difficulty, expected", [
    ("Easy", "between 1 and 20"),
    ("Normal", "between 1 and 100"),
    ("Hard", "between 1 and 200"),
])
def test_bug14_prompt_shows_difficulty_range(app, difficulty, expected):
    app.selectbox[0].select(difficulty).run()
    assert expected in info_text(app)
