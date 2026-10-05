# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

  At first glance the game looked finished: it had a title, a difficulty dropdown, a text box, Submit/New Game buttons and a "Developer Debug Info" panel. Once I started playing, it was clear something was off. The prompt always said "between 1 and 100" no matter which difficulty I picked, and "Attempts left" started at 7 instead of 8 on Normal. Following the hints never got me closer to the secret, and after winning or losing, clicking "New Game" left me stuck on the "Game over" message.

- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

  1. The hints were backwards: guessing too high said "Go HIGHER!" and guessing too low said "Go LOWER!".
  2. Hard difficulty used the range 1–50, which is smaller (easier) than Normal's 1–100.
  3. "Attempts left" didn't update after a guess until the next click, and typing invalid input like "abc" still used up an attempt.
  4. "New Game" didn't reset the game status, so after a win or loss the game could never be played again.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| **Bug 1 (reversed hints):** Normal difficulty, secret is 50 (seen in Developer Debug Info), guess `60` and click Submit | Hint says the guess is too high and tells me to go **lower** ("📉 Go LOWER!") | Hint says "📈 Go HIGHER!", which points away from the secret, so following the hints never reaches it | No error; the app runs normally and shows the wrong hint in the yellow warning box |
| **Bug 3 (Hard range):** Select **Hard** in the sidebar difficulty dropdown, then compare with **Normal** | Hard should be the most difficult level, with a wider range than Normal (1–100) | Sidebar shows "Range: 1 to 50" for Hard, a smaller range than Normal, so Hard is actually easier than Normal | No error; the sidebar caption just shows "Range: 1 to 50" |
| **Bug 7 ("Attempts left" lags):** Normal difficulty, type a valid guess like `30` and click Submit once | "Attempts left" drops by one immediately after the guess is counted | The box still shows the same "Attempts left" number as before the guess; it only updates on the *next* click. Developer Debug Info also shows the old attempt count | No error; the status box is drawn before the guess is processed, so it shows stale values |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  I used Claude (Claude Code) to read through `app.py`, list the bugs, mark them with comments, apply fixes, and write tests.

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

  Claude pointed out that on every even attempt the app converted the secret to a string, so the comparison in `check_guess` became a text comparison where `"9" > "50"` is True. It suggested removing the string conversion and always comparing integers. I verified it by setting the secret to 50 in the Developer Debug Info, guessing 60 and then 9, and checking that the second hint now said "Go HIGHER!". There is also an app test (`test_bug2_even_attempt_hint_uses_numeric_comparison`) that fails on the original code and passes on the fixed code.

- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

  The first version of the test for bug #7 ("Attempts left" lags behind) only checked that the box showed 7, then 6, after each guess. When we ran the new tests against a copy of the original buggy code, that test still passed, because two old bugs (attempts starting at 1, and the box being drawn before the guess was counted) canceled each other out. So the test wasn't really catching the bug. We changed it to also check that the displayed number matches the real attempt count in session state after each guess, then confirmed it fails on the buggy code and passes on the fixed code.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

  I considered a bug fixed only when I could reproduce it before the change and not after. For each bug I played the game with the Developer Debug Info open so I could see the secret and attempt count, then wrote a pytest test that targets that exact bug. The strongest check was running the tests against a copy of the original buggy code: a good test should fail there and pass on the fixed version. If a test passed on both versions, it wasn't proving anything and needed to be rewritten.

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.

  `test_bug8_new_game_after_win_lets_you_play_again` sets the secret to 50, guesses 50 to win, then clicks "New Game" and checks that the status is back to "playing". On the original code it failed because "New Game" reset the secret and attempts but never reset `status`, so the app stayed stuck on "You already won". It showed me that resetting state in several separate places makes it easy to forget something, which is why the fix puts every reset in one `start_new_game()` function.

- Did AI help you design or understand any tests? How?

  Yes. Claude explained that the original starter tests could never pass because they compared `check_guess(...)` to a string like `"Win"` while the function returns a pair `("Win", "🎉 Correct!")`. It also showed me how to use Streamlit's `AppTest` to test UI bugs (clicking buttons, typing guesses, reading the "Attempts left" box) and how to use pytest's `monkeypatch` to control the random secret so the New Game range test is predictable. Running all 36 tests with `python -m pytest` (plain `pytest` wasn't on my PATH) gave me confidence the fixes didn't break anything else.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

  Every time you click a button or type something, Streamlit runs your entire Python script again from the top. That means normal variables are wiped and recreated on every click, like the page has amnesia. `st.session_state` is a small dictionary that survives those reruns, so anything the game needs to remember (the secret number, attempts, score, history) has to live there. The order of the script also matters: anything drawn on the page before the guess is processed shows old values, which is exactly why "Attempts left" lagged one guess behind until we drew it at the end of the run.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

  Writing one regression test per bug and checking that it fails on the old code before trusting it. It's a simple way to prove a test actually tests something. I also liked marking every bug with a numbered comment first, then fixing them one by one, because it kept the work organized and made it easy to match fixes, tests and this reflection to the same bug numbers.

- What is one thing you would do differently next time you work with AI on a coding task?

  I would ask for smaller changes and review each one before moving on, instead of accepting a large batch of fixes at once. I'd also commit to Git after each step so I could compare or roll back changes more easily. Finally, I'd run and play the app myself more often, instead of relying only on the AI's summary of what it changed.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  AI-generated code can look polished and "production-ready" while hiding many small logic and state bugs that only show up when you actually use it. I now treat AI code as a first draft that needs to be read carefully, played with, and backed by tests before I trust it.
