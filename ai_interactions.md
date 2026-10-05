# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (agent mode) to work through the whole debugging assignment in a series of short prompts: "find bug in app.py", "mark all the bugs and its description", "fix every bug that is marked", "pytest is not working?", and "from the 14 bugs, add test cases so that they target those specific bugs". The overall goal was to find every bug in the AI-generated guessing game, fix them, move the logic into `logic_utils.py`, and prove the fixes with tests.

**What did the agent do?**

1. Read `app.py`, `logic_utils.py` and `tests/test_game_logic.py` and listed 14 bugs (reversed hints, the secret turning into a string on even attempts, Hard range smaller than Normal, New Game not resetting status, and more).
2. Added a numbered `# BUG #n:` comment above each bug in `app.py`, then checked that the file still parsed.
3. Rewrote `app.py` to fix all 14 bugs, replacing each marker with a `# FIX #n` note and adding a `start_new_game()` helper so every reset happens in one place.
4. Installed `requirements.txt` and played through the game automatically with Streamlit's `AppTest` (invalid input, a wrong guess, a win, New Game, switching to Hard).
5. Found out that `pytest` wasn't on PATH (fixed by running `python -m pytest`) and that all 3 starter tests failed with `NotImplementedError`. It moved the fixed functions into `logic_utils.py`, made `app.py` import them, and updated the starter tests to read the outcome from the `(outcome, message)` pair.
6. Wrote 33 regression tests in `tests/test_bug_regressions_logic.py` and `tests/test_bug_regressions_app.py`, plus a root `conftest.py` so tests can import the project.
7. Ran the new tests against a copy of the original buggy code to prove they catch the bugs (26 of 33 fail on the old code), and against the fixed code (all 36 pass).
8. Added docstrings and comments explaining how each function works, filled in the README walkthrough, and committed and pushed with the message "bug fix".

**What did you have to verify or fix manually?**

- **A test that proved nothing:** the first version of the bug #7 test ("Attempts left" lagging) still passed on the original buggy code, because two old bugs canceled each other out. This only showed up because we ran the tests against the old code. The test was rewritten to also check that the screen matches the real attempt count, and now it fails on the buggy version.
- **Design choices I had to accept or change:** Hard's new range of 1–200 and rejecting decimals (instead of rounding them) were the agent's decisions, not something the assignment specified.
- **Import path quirk:** the agent's first playthrough after the refactor failed with `ModuleNotFoundError: logic_utils`. That turned out to be a quirk of Streamlit's test tool, not a real bug, and the root `conftest.py` handles it.
- **Writing in my voice:** I reviewed the reflection answers the agent drafted, since they need to describe my own experience.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Single-digit guess vs. two-digit secret (bug #2: numbers compared as text, so `"9" > "50"`) | "from the 14 bugs, add test cases so that they target those specific bugs" | `test_bug2_even_attempt_hint_uses_numeric_comparison`: set the secret to 50, guess 60 (attempt 1), then 9 (attempt 2), and expect the hint to say "HIGHER" | Yes on the fixed code; fails on the original code | The bug only happened on even attempts, so the test has to make two guesses. A guess of 9 against 50 is the classic case where text comparison and number comparison disagree. |
| Invalid input: `abc`, `3.7`, empty, and out-of-range `999` (bugs #6 and #13) | Same prompt as above | `test_bug6_invalid_input_does_not_use_attempt`, run once for each of the four inputs, checking that attempts stay 0, history stays empty, and one error is shown | Yes on the fixed code; all 4 cases fail on the original code | One test run with four inputs covers each kind of bad input (letters, decimal, blank, out of range) without repeating code. |
| "Attempts left" right after a guess (bug #7) | Same prompt as above | First version: check that the box shows 7, then 6, after two guesses. Revised version: after each of three guesses, also check that the number on screen equals 8 minus the real attempt count | First version passed on **both** the fixed and buggy code; the revised version passes on fixed and fails on buggy | The first test was wrong: two original bugs (attempts starting at 1, and the box being drawn too early) canceled out. Checking the screen against the real state catches it. |
| New Game on Hard uses the 1–200 range (bug #9) | Same prompt as above | `test_bug9_new_game_uses_difficulty_range`: replace `random.randint` (using pytest's `monkeypatch`) to record its arguments and return the maximum, then check it was called with (1, 200) and the secret is 200 | Yes on the fixed code; fails on the original code | A random secret could land in range by luck, so controlling `random.randint` makes the test reliable instead of flaky. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

*Not attempted.*

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

*Not attempted.*

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
