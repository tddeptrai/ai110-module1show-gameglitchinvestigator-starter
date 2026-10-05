"""Regression tests for the logic bugs (#1, #2, #3, #11, #12, #13) in logic_utils.py."""
from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score


# --- BUG #1: hints were reversed ------------------------------------------

def test_bug1_too_high_hint_says_go_lower():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_bug1_too_low_hint_says_go_higher():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# --- BUG #2: numbers were compared as strings ("9" > "50") ------------------

def test_bug2_single_digit_guess_vs_two_digit_secret_is_too_low():
    # As strings, "9" > "50" is True, which used to report "Too High".
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


def test_bug2_two_digit_guess_vs_three_digit_secret_is_too_high():
    # As strings, "150" < "99" is True, which used to report "Too Low".
    outcome, _ = check_guess(150, 99)
    assert outcome == "Too High"


# --- BUG #3: Hard range was smaller than Normal ------------------------------

def test_bug3_hard_range_is_wider_than_normal():
    n_low, n_high = get_range_for_difficulty("Normal")
    h_low, h_high = get_range_for_difficulty("Hard")
    assert (h_high - h_low) > (n_high - n_low)


def test_bug3_ranges_grow_with_difficulty():
    sizes = [hi - lo for lo, hi in map(get_range_for_difficulty, ["Easy", "Normal", "Hard"])]
    assert sizes == sorted(sizes)


# --- BUG #11: "Too High" on even attempts added points -----------------------

def test_bug11_too_high_on_even_attempt_loses_points():
    assert update_score(0, "Too High", 2) == -5


def test_bug11_too_high_and_too_low_cost_the_same():
    for attempt in range(1, 9):
        assert update_score(0, "Too High", attempt) == update_score(0, "Too Low", attempt)


# --- BUG #12: win bonus had an extra one-attempt penalty ---------------------

def test_bug12_first_try_win_scores_100():
    assert update_score(0, "Win", 1) == 100


def test_bug12_second_try_win_scores_90():
    assert update_score(0, "Win", 2) == 90


def test_bug12_win_points_never_below_10():
    assert update_score(0, "Win", 50) == 10


# --- BUG #13: decimals truncated, no range check -----------------------------

def test_bug13_decimal_is_rejected_not_truncated():
    ok, value, err = parse_guess("3.7")
    assert not ok
    assert value is None
    assert err


def test_bug13_guess_above_range_is_rejected():
    ok, _, err = parse_guess("150", 1, 100)
    assert not ok
    assert "between 1 and 100" in err


def test_bug13_negative_guess_is_rejected():
    ok, _, _ = parse_guess("-5", 1, 100)
    assert not ok


def test_bug13_range_edges_are_accepted():
    assert parse_guess("1", 1, 100) == (True, 1, None)
    assert parse_guess("100", 1, 100) == (True, 100, None)


def test_bug13_whitespace_is_ignored():
    assert parse_guess("  42 ", 1, 100) == (True, 42, None)
