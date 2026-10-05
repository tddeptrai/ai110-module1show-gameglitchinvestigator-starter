"""
Streamlit UI for the number guessing game.

How Streamlit runs this file:
    Streamlit re-runs this whole script from top to bottom every time the
    player interacts with the page (clicks a button, types, changes a
    setting). Normal variables are reset on every run, so anything that must
    survive between runs (the secret, attempts, score, ...) is stored in
    st.session_state.

Flow of one run:
    1. Draw the header and sidebar settings.
    2. Start a new game if this is the first load or the difficulty changed.
    3. Draw the input box and buttons.
    4. Handle "New Game", stop early if the game is already over.
    5. Handle "Submit": validate, check the guess, update score/state.
    6. Draw the status box and debug info using the up-to-date state.

All game rules live in logic_utils.py; this file only wires them to the UI.
"""
import random
import streamlit as st

from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score


def start_new_game(low: int, high: int, difficulty: str):
    """
    Reset every piece of game state in st.session_state for a fresh game.

    How it works:
        Picks a new random secret inside [low, high] for the chosen
        difficulty, and sets attempts, score, status and history back to
        their starting values. It also remembers which difficulty this game
        was started with, so the app can detect when the player switches
        difficulty and restart automatically.

    Used on first page load, when the difficulty changes, and when the
    player clicks "New Game".
    """
    # FIX #8 / #9 / #10: Fully reset game state using the current difficulty's range.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty


# --- Page header -------------------------------------------------------------

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

# --- Sidebar settings: difficulty decides the range and number of attempts ---

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

# How many guesses the player gets on each difficulty.
attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# --- Game state setup --------------------------------------------------------

# FIX #4 / #5: Start (attempts = 0) on first load, and restart when difficulty changes.
if "secret" not in st.session_state or st.session_state.get("difficulty") != difficulty:
    start_new_game(low, high, difficulty)

# --- Input area --------------------------------------------------------------

st.subheader("Make a guess")

# FIX #7: Reserve spots for the status box and debug info, filled in after the guess is processed.
info_box = st.empty()
debug_box = st.container()

# The key includes the difficulty so the text box starts empty after switching levels.
raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

# Buttons return True only on the run triggered by clicking them.
col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)


def render_status():
    """
    Fill in the status box and debug panel with the current game state.

    How it works:
        Writes into the placeholders (info_box, debug_box) that were created
        above the input box. Because this is called at the END of the run,
        after any guess has been processed, "Attempts left" and the debug
        values always reflect the latest guess, while still appearing near
        the top of the page.
    """
    # FIX #14: Show the real range for the selected difficulty.
    info_box.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )
    with debug_box.expander("Developer Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)


# --- "New Game" button: reset everything and redraw the page -----------------

if new_game:
    start_new_game(low, high, difficulty)
    st.rerun()

# --- Game already finished: show the result and skip guess handling ---------

if st.session_state.status != "playing":
    render_status()
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

# --- "Submit" button: validate, compare, score, and check for win/loss ------

if submit:
    # 1. Validate the text; invalid input shows an error and costs nothing.
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX #6: Invalid input does not use up an attempt.
        st.error(err)
    else:
        # 2. Count the attempt and remember the guess.
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # 3. Compare against the secret and optionally show the hint.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        # 4. Update the running score.
        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # 5. End the game on a win, or when the player runs out of attempts.
        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# --- Draw the status box last so it shows the up-to-date state --------------

render_status()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
