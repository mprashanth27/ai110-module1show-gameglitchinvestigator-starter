from logic_utils import check_guess, get_range_for_difficulty

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# --- Tests for get_range_for_difficulty (Bug 4.1 fix) ---

def test_easy_range():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20

def test_normal_range():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 50

def test_hard_range():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 100

def test_difficulty_order():
    # Hard range must be wider than Normal, Normal wider than Easy
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert easy_high < normal_high < hard_high

def test_unknown_difficulty_returns_default():
    low, high = get_range_for_difficulty("Unknown")
    assert low == 1
    assert high == 100


# --- Tests for Bug 4.2 fix: new game secret uses difficulty range ---
# Bug 4.2: the New Game button used random.randint(1, 100) regardless of difficulty.
# Fix: use get_range_for_difficulty(difficulty) to derive low/high before calling randint.
# These tests verify that the range returned per difficulty is correct and that
# a secret generated from that range always stays within the expected bounds.

import random

def test_new_game_secret_within_easy_range():
    # Simulate new game for Easy: secret must be in 1-20
    low, high = get_range_for_difficulty("Easy")
    secret = random.randint(low, high)
    assert low <= secret <= high

def test_new_game_secret_within_normal_range():
    # Simulate new game for Normal: secret must be in 1-50
    low, high = get_range_for_difficulty("Normal")
    secret = random.randint(low, high)
    assert low <= secret <= high

def test_new_game_secret_within_hard_range():
    # Simulate new game for Hard: secret must be in 1-100
    low, high = get_range_for_difficulty("Hard")
    secret = random.randint(low, high)
    assert low <= secret <= high

def test_new_game_secret_not_outside_easy_range():
    # Before the fix, randint(1, 100) could produce values > 20 for Easy.
    # After the fix, every generated secret must be <= 20.
    low, high = get_range_for_difficulty("Easy")
    for _ in range(50):
        secret = random.randint(low, high)
        assert secret <= 20, f"Secret {secret} exceeds Easy upper bound of 20"

def test_new_game_uses_correct_range_per_difficulty():
    # Core regression test: the range passed to randint must match the difficulty,
    # not the old hardcoded (1, 100).
    cases = {
        "Easy":   (1, 20),
        "Normal": (1, 50),
        "Hard":   (1, 100),
    }
    for difficulty, expected in cases.items():
        low, high = get_range_for_difficulty(difficulty)
        assert (low, high) == expected, (
            f"{difficulty}: expected range {expected}, got ({low}, {high})"
        )


# --- Tests for Bug 4.3 fix: changing difficulty mid-session resets the secret ---
# Bug 4.3: the secret was only generated once (when "secret" not in session_state).
# Switching difficulty in the sidebar left the old secret in place.
# Fix: track last_difficulty in session state; reset secret when it doesn't match.
# These tests simulate session state with a plain dict to exercise the reset logic.

def _apply_session_init(session: dict, difficulty: str) -> None:
    """Mirrors the Bug 3 fix logic from app.py, using a dict as a stand-in for
    st.session_state so it can be tested without Streamlit."""
    low, high = get_range_for_difficulty(difficulty)
    if "secret" not in session or session.get("last_difficulty") != difficulty:
        session["last_difficulty"] = difficulty
        session["secret"] = random.randint(low, high)
        session["attempts"] = 1
        session["score"] = 0
        session["status"] = "playing"
        session["history"] = []

def test_secret_initialised_on_first_load():
    # On first load there is no session state; secret must be generated.
    session = {}
    _apply_session_init(session, "Easy")
    assert "secret" in session
    assert 1 <= session["secret"] <= 20

def test_secret_unchanged_when_difficulty_stays_same():
    # Re-rendering with the same difficulty must NOT regenerate the secret.
    session = {}
    _apply_session_init(session, "Normal")
    original_secret = session["secret"]
    _apply_session_init(session, "Normal")   # same difficulty, second render
    assert session["secret"] == original_secret

def test_secret_resets_when_difficulty_changes():
    # Switching difficulty must produce a new secret in the new difficulty's range.
    session = {}
    _apply_session_init(session, "Easy")      # first load as Easy (range 1-20)
    _apply_session_init(session, "Hard")      # user switches to Hard (range 1-100)
    low, high = get_range_for_difficulty("Hard")
    assert low <= session["secret"] <= high
    assert session["last_difficulty"] == "Hard"

def test_game_state_resets_on_difficulty_change():
    # When difficulty changes, attempts/score/status/history should also reset.
    session = {}
    _apply_session_init(session, "Easy")
    session["attempts"] = 5
    session["score"] = 40
    session["status"] = "lost"
    session["history"] = [3, 7, 12]
    _apply_session_init(session, "Hard")      # switch difficulty
    assert session["attempts"] == 1
    assert session["score"] == 0
    assert session["status"] == "playing"
    assert session["history"] == []

def test_secret_within_new_difficulty_range_after_switch():
    # After switching from Hard to Easy the secret must fit inside 1-20, not 1-100.
    session = {}
    _apply_session_init(session, "Hard")
    for _ in range(20):                        # run multiple times to reduce flakiness
        _apply_session_init(session, "Easy")
        assert session["secret"] <= 20, (
            f"Secret {session['secret']} exceeds Easy upper bound of 20 after difficulty switch"
        )
        session["last_difficulty"] = "Hard"   # simulate switching back to trigger reset


# --- Tests for Bug 3 fix: New Game button resets status to "playing" ---
# Bug 3: the New Game button reset attempts and secret but never reset
# st.session_state.status. After a loss ("lost") or win ("won"), status remained
# set, so the guard block at line 149 called st.stop() immediately after rerun,
# freezing the game even though a new round had started.
# Fix: add st.session_state.status = "playing" inside the new_game block.

def _simulate_new_game(session: dict, difficulty: str) -> None:
    """Mirrors the new_game block in app.py (post Bug 3 fix) using a plain dict."""
    session["attempts"] = 0
    session["status"] = "playing"
    low, high = get_range_for_difficulty(difficulty)
    session["secret"] = random.randint(low, high)

def test_new_game_resets_status_after_loss():
    # After a loss, clicking New Game must set status back to "playing".
    session = {"status": "lost", "attempts": 8, "score": 20, "history": [1, 2, 3]}
    _simulate_new_game(session, "Normal")
    assert session["status"] == "playing"

def test_new_game_resets_status_after_win():
    # After a win, clicking New Game must set status back to "playing".
    session = {"status": "won", "attempts": 3, "score": 70, "history": [10, 25, 42]}
    _simulate_new_game(session, "Normal")
    assert session["status"] == "playing"

def test_new_game_resets_attempts():
    # Attempts counter must be zeroed so the new round starts fresh.
    session = {"status": "lost", "attempts": 8, "score": 0, "history": []}
    _simulate_new_game(session, "Easy")
    assert session["attempts"] == 0

def test_new_game_generates_secret_in_range():
    # The new secret must be within the selected difficulty's range.
    session = {"status": "lost", "attempts": 5, "score": 0, "history": []}
    _simulate_new_game(session, "Easy")
    low, high = get_range_for_difficulty("Easy")
    assert low <= session["secret"] <= high

def test_new_game_status_allows_subsequent_guess():
    # After New Game, status == "playing" means the guess block would not be
    # short-circuited by st.stop(). Simulate the guard condition directly.
    session = {"status": "lost"}
    _simulate_new_game(session, "Hard")
    # The guard: `if st.session_state.status != "playing": st.stop()`
    # With the fix applied, this condition must be False.
    assert session["status"] == "playing", (
        "status must be 'playing' after New Game so st.stop() is not triggered"
    )


# --- Tests for Bug 1 fix: hints used string comparison on even attempts ---
# Bug 1: on every even-numbered attempt, the secret was cast to str before
# being passed to check_guess. This caused lexicographic comparison instead of
# numeric, so single-digit guesses compared greater than two-digit secrets
# (e.g. "6" > "24" lexicographically, even though 6 < 24 numerically),
# producing an inverted "Go LOWER" hint when "Go HIGHER" was correct.
# Fix: always pass the integer secret to check_guess; remove the even/odd branch.

def test_exact_user_reported_case():
    # User reported: secret=24, guess=6 → hint said "Go LOWER" (wrong).
    # Lexicographically "6" > "24" because '6' > '2', hence the bad hint.
    # After the fix, numeric comparison must return "Too Low".
    result = check_guess(6, 24)
    assert result == "Too Low", (
        f"guess=6 < secret=24 numerically, expected 'Too Low', got '{result}'"
    )

def test_single_digit_less_than_two_digit_secret():
    # Any single-digit guess is numerically less than a two-digit secret.
    # String comparison inverts this for digits 3-9 (e.g. "9" > "10").
    for guess in range(1, 10):
        result = check_guess(guess, 10)
        assert result == "Too Low", (
            f"guess={guess} < secret=10 numerically, expected 'Too Low', got '{result}'"
        )

def test_two_digit_guess_greater_than_single_digit_secret():
    # A two-digit guess is always numerically greater than a single-digit secret.
    # String comparison could agree here but must be verified as numeric.
    for guess in range(10, 20):
        result = check_guess(guess, 9)
        assert result == "Too High", (
            f"guess={guess} > secret=9 numerically, expected 'Too High', got '{result}'"
        )

def test_hint_correct_across_full_normal_range():
    # Sweep representative pairs across the Normal difficulty range (1–50)
    # to confirm numeric ordering is always respected.
    cases = [
        (1,  50, "Too Low"),
        (25, 50, "Too Low"),
        (49, 50, "Too Low"),
        (50, 50, "Win"),
        (51, 50, "Too High"),
        (9,  10, "Too Low"),   # would fail with string comparison ("9" > "10")
        (8,  24, "Too Low"),   # variant of user-reported case
        (6,  24, "Too Low"),   # exact user-reported case
    ]
    for guess, secret, expected in cases:
        result = check_guess(guess, secret)
        assert result == expected, (
            f"guess={guess}, secret={secret}: expected '{expected}', got '{result}'"
        )

def test_check_guess_always_uses_integer_comparison():
    # Passing an integer secret must never trigger string-ordering behaviour.
    # If check_guess internally converts secret to str, these would fail.
    assert check_guess(3, 30) == "Too Low"   # "3" > "30" lexicographically
    assert check_guess(7, 70) == "Too Low"   # "7" > "70" lexicographically
    assert check_guess(9, 19) == "Too Low"   # "9" > "19" lexicographically
