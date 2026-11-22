"""Phase 8 — Task 8.6 tests for app/personalisation.py."""
from __future__ import annotations

import math

import pandas as pd
import pytest

import app.personalisation as pers


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


def test_personalisation_is_empty_when_all_blank():
    p = pers.Personalisation()
    assert p.is_empty()


def test_personalisation_not_empty_with_amount():
    assert not pers.Personalisation(amount=1000.0).is_empty()


def test_personalisation_not_empty_with_reflection_only():
    assert not pers.Personalisation(target_return_reflection=0.10).is_empty()


# ---------------------------------------------------------------------------
# validate_personalisation
# ---------------------------------------------------------------------------


def test_all_blank_valid():
    e, w = pers.validate_personalisation(None, "", "", "")
    assert e == [] and w == []


def test_negative_amount_is_error():
    e, _ = pers.validate_personalisation(-100.0, "", "", "")
    assert any("negative" in x for x in e)


def test_zero_amount_is_warning_not_error():
    e, w = pers.validate_personalisation(0.0, "", "", "")
    assert e == []
    assert any("0" in x for x in w)


def test_very_large_amount_is_warning_not_error():
    e, w = pers.validate_personalisation(200_000_000.0, "", "", "")
    assert e == []
    assert any("large" in x for x in w)


def test_amount_at_hard_limit_boundary():
    e, _ = pers.validate_personalisation(pers.AMOUNT_HARD_LIMIT + 1, "", "", "")
    assert any("sanity" in x or "ceiling" in x or "exceeds" in x for x in e)


def test_non_finite_amount_is_error():
    e, _ = pers.validate_personalisation(float("inf"), "", "", "")
    assert any("finite" in x for x in e)


def test_non_numeric_amount_is_error():
    e, _ = pers.validate_personalisation("not-a-number", "", "", "")
    assert any("number" in x for x in e)


def test_unknown_horizon_is_error():
    e, _ = pers.validate_personalisation(None, "Forever", "", "")
    assert any("horizon" in x.lower() for x in e)


def test_unknown_risk_tolerance_is_error():
    e, _ = pers.validate_personalisation(None, "", "Extreme", "")
    assert any("risk tolerance" in x.lower() for x in e)


def test_unknown_objective_is_error():
    e, _ = pers.validate_personalisation(None, "", "", "Wealth")
    assert any("objective" in x.lower() for x in e)


def test_valid_full_set():
    e, w = pers.validate_personalisation(
        5000.0, "Medium (3–10 years)", "Medium", "Growth"
    )
    assert e == [] and w == []


# ---------------------------------------------------------------------------
# weights_to_dollars
# ---------------------------------------------------------------------------


def test_weights_to_dollars_simple():
    w = pd.Series([0.5, 0.3, 0.2], index=["A", "B", "C"])
    out = pers.weights_to_dollars(w, 10000.0)
    assert out["A"] == pytest.approx(5000.0)
    assert out["B"] == pytest.approx(3000.0)
    assert out["C"] == pytest.approx(2000.0)


def test_weights_to_dollars_none_amount_returns_empty():
    w = pd.Series([0.5, 0.5], index=["A", "B"])
    out = pers.weights_to_dollars(w, None)
    assert len(out) == 0


def test_weights_to_dollars_negative_amount_returns_empty():
    w = pd.Series([0.5, 0.5], index=["A", "B"])
    out = pers.weights_to_dollars(w, -100.0)
    assert len(out) == 0


def test_weights_to_dollars_nan_weights_become_zero():
    w = pd.Series([0.5, float("nan"), 0.5], index=["A", "B", "C"])
    out = pers.weights_to_dollars(w, 1000.0)
    assert out["A"] == pytest.approx(500.0)
    assert out["B"] == pytest.approx(0.0)
    assert out["C"] == pytest.approx(500.0)


def test_weights_to_dollars_preserves_index():
    w = pd.Series([0.6, 0.4], index=["X", "Y"])
    out = pers.weights_to_dollars(w, 100.0)
    assert list(out.index) == ["X", "Y"]


# ---------------------------------------------------------------------------
# AppTest — all-blank works, read-only target reflection
# ---------------------------------------------------------------------------
#
# Reuses the same fixture-CSV pattern as test_user_experience.py so the
# baseline "no CSV" state is restored after the suite.

import shutil
from pathlib import Path
import numpy as np

from streamlit.testing.v1 import AppTest


_APP_PATH = str(Path(__file__).resolve().parent.parent / "app" / "app.py")
_CSV_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@pytest.fixture(scope="module")
def _apptest_csv():
    _CSV_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = _CSV_DIR / "prices_clean_TESTONLY.csv"
    dates = pd.bdate_range("2022-01-03", periods=120)
    rng = np.random.default_rng(0)
    rets = rng.normal(0.0005, 0.01, size=(len(dates), 3))
    prices = pd.DataFrame(
        100.0 * np.exp(np.cumsum(rets, axis=0)),
        index=dates,
        columns=["AAPL", "MSFT", "GOOG"],
    )
    prices.index.name = "Date"
    prices.to_csv(csv_path)
    yield csv_path
    try:
        csv_path.unlink()
    except FileNotFoundError:
        pass


@pytest.fixture(scope="module")
def _apptest(_apptest_csv):
    at = AppTest.from_file(_APP_PATH, default_timeout=60)
    at.run()
    return at


def test_all_blank_runs_without_exceptions(_apptest):
    """Acceptance: app works with all personalisation fields blank."""
    assert not _apptest.exception


def test_personalisation_expander_present(_apptest):
    expander_labels = [e.label for e in _apptest.expander]
    assert any("Personalise" in lbl for lbl in expander_labels)


def test_target_reflection_shows_not_enabled_by_default(_apptest):
    # Default: sidebar "Include Target Return" is False.
    # The read-only reflection line should say "not enabled".
    all_markdown = " ".join(m.value for m in _apptest.markdown)
    assert "not enabled" in all_markdown.lower() or "—" in all_markdown

# ---------------------------------------------------------------------------
# Regression: personalisation must reach the Explanations panel
# ---------------------------------------------------------------------------
#
# Bug caught at Phase 8 closeout: `render_sidebar` did not include the
# personalisation dict in its return value, so `inputs.get("personalisation")`
# was always None and the Beginner-mode "What this means for you" callout
# never fired. These tests fail if that regression returns.


def test_render_sidebar_return_dict_contains_personalisation():
    """
    `render_sidebar`'s return dict must include the 'personalisation' key,
    so the downstream Explanations panel receives it via
    `inputs.get('personalisation')`.
    """
    from app.personalisation import Personalisation
    from app.user_experience import render_explanations_panel

    # Source inspection is the cheapest reliable check for this specific
    # wiring bug without spinning up Streamlit (AppTest can set widgets but
    # does not easily assert that a *downstream kwarg* was non-None).
    import inspect
    import app.app as app_module

    src = inspect.getsource(app_module.render_sidebar)
    assert '"personalisation": personalisation' in src, (
        "render_sidebar must include 'personalisation': personalisation in "
        "its return dict — otherwise the Beginner-mode callout never fires."
    )


def test_beginner_context_callout_fires_when_personalisation_nonempty(monkeypatch):
    """
    When personalisation is non-empty and mode is Beginner, the callout
    must call st.info (one st.info call containing 'What this means for you').
    When mode is Advanced, no callout is emitted.
    """
    from app.personalisation import Personalisation, render_beginner_context_callout
    from app import personalisation as pers_module

    calls = []

    class _Stub:
        @staticmethod
        def info(msg, *a, **k):
            calls.append(msg)

    # render_beginner_context_callout does a local `import streamlit as st`
    # inside the function body; patch the module attribute it will resolve.
    import streamlit
    monkeypatch.setattr(streamlit, "info", _Stub.info)

    p = Personalisation(amount=10000.0)
    render_beginner_context_callout(p, "Beginner")
    assert len(calls) == 1
    assert "What this means for you" in calls[0]

    calls.clear()
    render_beginner_context_callout(p, "Advanced")
    assert calls == []  # Advanced mode never emits the callout

    calls.clear()
    render_beginner_context_callout(Personalisation(), "Beginner")
    assert calls == []  # empty personalisation never emits the callout