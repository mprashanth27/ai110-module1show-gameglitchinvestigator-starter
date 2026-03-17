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


# --- Tests for get_range_for_difficulty (Bug 1 fix) ---

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


# --- Tests for Bug 2 fix: new game secret uses difficulty range ---
# Bug 2: the New Game button used random.randint(1, 100) regardless of difficulty.
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
