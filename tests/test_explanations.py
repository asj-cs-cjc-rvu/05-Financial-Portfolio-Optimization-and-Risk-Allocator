"""Phase 8 — Task 8.5 tests for app/explanations.py."""
from __future__ import annotations

import pytest

from app.explanations import EXPLANATIONS, get_explanation, list_explanation_keys


_REQUIRED_KEYS = [
    "return", "volatility", "variance", "sharpe",
    "var_95", "cvar_95", "max_drawdown", "n_iter", "success", "weights",
    "mean_return", "covariance", "correlation", "efficient_frontier",
    "objective", "constraint", "target_return",
    "investment_amount", "horizon", "risk_tolerance",
]


@pytest.mark.parametrize("key", _REQUIRED_KEYS)
def test_every_required_key_has_both_modes_nonempty(key):
    assert key in EXPLANATIONS, f"{key} missing from EXPLANATIONS"
    assert get_explanation(key, "Beginner")
    assert get_explanation(key, "Advanced")


@pytest.mark.parametrize("key", _REQUIRED_KEYS)
def test_beginner_and_advanced_texts_differ(key):
    b = get_explanation(key, "Beginner")
    a = get_explanation(key, "Advanced")
    assert b != a, f"{key}: Beginner and Advanced texts are identical"


def test_unknown_key_raises():
    with pytest.raises(KeyError):
        get_explanation("no_such_key", "Beginner")


def test_unknown_mode_falls_back_to_beginner():
    assert get_explanation("return", "Bogus") == get_explanation("return", "Beginner")


def test_list_explanation_keys_covers_required():
    listed = set(list_explanation_keys())
    for key in _REQUIRED_KEYS:
        assert key in listed