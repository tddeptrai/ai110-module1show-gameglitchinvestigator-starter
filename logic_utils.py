"""
Pure game logic for the number guessing game.

Nothing in this module touches Streamlit, so every function here can be
unit-tested directly with pytest. app.py imports these functions and
handles all of the UI and session state.
"""


def get_range_for_difficulty(difficulty: str):
    """
    Return (low, high) inclusive range for a given difficulty.

    How it works:
        Looks up the difficulty name and returns the smallest and largest
        number the secret can be. Harder levels use a wider range, so there
        are more numbers to search through. Any unknown difficulty falls
        back to the Normal range (1-100).

    Example:
        get_range_for_difficulty("Easy")  ->  (1, 20)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        # FIX #3: Hard now has the widest range.
        return 1, 200
    return 1, 100


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)

    How it works:
        1. Rejects missing or blank input ("Enter a guess.").
        2. Strips surrounding spaces, then tries int(raw). Anything that is
           not a whole number (letters, decimals like "3.7") is rejected
           instead of being silently converted.
        3. If low/high are given, rejects numbers outside that range.
        4. Otherwise returns (True, the_number, None).

    The caller only needs to check `ok`: when it is False, `error_message`
    explains what went wrong and `guess_int` is None.

    Examples:
        parse_guess("42", 1, 100)   ->  (True, 42, None)
        parse_guess("3.7")          ->  (False, None, "Please enter a whole number.")
        parse_guess("150", 1, 100)  ->  (False, None, "Guess must be between 1 and 100.")
    """
    # Step 1: nothing typed yet.
    if raw is None:
        return False, None, "Enter a guess."

    raw = raw.strip()
    if raw == "":
        return False, None, "Enter a guess."

    # Step 2: must be a whole number.
    # FIX #13: Reject decimals instead of truncating, and enforce the range.
    try:
        value = int(raw)
    except ValueError:
        return False, None, "Please enter a whole number."

    # Step 3: must be inside the difficulty's range (only checked when a range is given).
    if low is not None and high is not None and not (low <= value <= high):
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"

    How it works:
        Compares two integers. The outcome is a fixed label the rest of the
        program uses for scoring and win/loss logic. The message is the hint
        shown to the player and tells them which way to move next:
        a guess that is too high means they should go LOWER, and vice versa.

    Examples:
        check_guess(50, 50)  ->  ("Win", "🎉 Correct!")
        check_guess(60, 50)  ->  ("Too High", "📉 Go LOWER!")
        check_guess(40, 50)  ->  ("Too Low", "📈 Go HIGHER!")
    """
    # FIX #1 / #2: Hints point the right way; both values are always ints.
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Update score based on outcome and attempt number.

    How it works:
        - Win: award 100 points for a first-try win, minus 10 for every extra
          attempt it took (attempt 1 -> 100, attempt 2 -> 90, ...). The award
          never drops below 10, so a win always gains something.
        - Wrong guess ("Too High" or "Too Low"): lose 5 points.
        - Any other outcome: score is unchanged.

    `attempt_number` is 1-based: it is the attempt that produced `outcome`.
    Returns the new total; it does not modify anything in place.

    Examples:
        update_score(0, "Win", 1)        ->  100
        update_score(100, "Too Low", 3)  ->  95
    """
    if outcome == "Win":
        # FIX #12: A first-try win (attempt 1) earns the full 100 points.
        points = 100 - 10 * (attempt_number - 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX #11: Any wrong guess costs 5 points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
