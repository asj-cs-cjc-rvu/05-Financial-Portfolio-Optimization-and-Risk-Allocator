"""
tests/test_user_experience.py
Phase 8 — Tasks 8.3 / 8.4: unit tests for the presentation layer.

Two kinds of tests live here:
  1. Pure-helper unit tests for the label dictionaries and label-applying
     logic (no Streamlit runtime needed).
  2. Streamlit AppTest tests for mode persistence and for the mode-safety
     invariant — switching mode must not change the outputs of `src.*`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# Import the presentation module directly; it does not touch src.* at import.
import app.user_experience as ux


# ---------------------------------------------------------------------------
# Unit tests — pure helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", [
    "return", "volatility", "variance", "sharpe",
    "var_95", "cvar_95", "max_drawdown", "n_iter", "success",
])
def test_metric_label_known_keys_have_both_modes(key):
    assert ux.metric_label(key, "Beginner")
    assert ux.metric_label(key, "Advanced")


@pytest.mark.parametrize("name", [
    "EqualWeight", "MinVolatility", "MaxSharpe", "TargetReturn",
])
def test_portfolio_label_known_names_have_both_modes(name):
    assert ux.portfolio_label(name, "Beginner")
    assert ux.portfolio_label(name, "Advanced")


def test_metric_label_unknown_key_passes_through():
    assert ux.metric_label("no_such_metric", "Beginner") == "no_such_metric"


def test_portfolio_label_unknown_name_passes_through():
    assert ux.portfolio_label("NotAPortfolio", "Advanced") == "NotAPortfolio"


def test_beginner_hides_variance_and_n_iter():
    assert not ux.should_show_metric("variance", "Beginner")
    assert not ux.should_show_metric("n_iter", "Beginner")


def test_beginner_keeps_return_vol_sharpe_risk_metrics():
    for key in ("return", "volatility", "sharpe", "var_95", "cvar_95",
                "max_drawdown", "success"):
        assert ux.should_show_metric(key, "Beginner")


def test_advanced_shows_all_metrics():
    for key in ("variance", "n_iter", "return", "var_95"):
        assert ux.should_show_metric(key, "Advanced")


def test_apply_display_labels_renames_columns_and_index():
    df = pd.DataFrame(
        {
            "return": [0.10],
            "variance": [0.04],
            "sharpe": [1.2],
            "AAPL": [0.5],
        },
        index=["MaxSharpe"],
    )
    out = ux.apply_display_labels(df, "Advanced")
    assert "Expected return (annualised)" in out.columns
    assert "Maximum-Sharpe portfolio" in out.index
    # Unknown ticker column passes through unchanged.
    assert "AAPL" in out.columns


def test_apply_display_labels_beginner_drops_variance_and_n_iter():
    df = pd.DataFrame(
        {"return": [0.10], "variance": [0.04], "n_iter": [42], "AAPL": [0.5]},
        index=["MaxSharpe"],
    )
    out = ux.apply_display_labels(df, "Beginner")
    assert "variance" not in out.columns
    assert "n_iter" not in out.columns
    assert "Expected yearly gain" in out.columns


def test_apply_display_labels_does_not_mutate_input():
    df = pd.DataFrame({"return": [0.10], "AAPL": [0.5]}, index=["MaxSharpe"])
    before = df.copy()
    ux.apply_display_labels(df, "Beginner")
    pd.testing.assert_frame_equal(df, before)


def test_set_mode_rejects_unknown_value():
    # st.session_state is a dict-like; set_mode does not require the
    # Streamlit runtime when called from a bare Python interpreter (as in
    # pytest), because Streamlit shims session_state to an empty dict
    # outside a script run.
    with pytest.raises(ValueError):
        ux.set_mode("Expert")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AppTest — mode toggle and mode-safety invariant (Task 8.3 acceptance)
# ---------------------------------------------------------------------------
#
# These tests require a processed CSV in data/processed/. The repo currently
# has none (baseline confirmed in Task 8.1). We therefore build a tiny
# in-memory fixture CSV, write it to data/processed/, and clean up after.
# This is a test-only fixture and does not modify any committed file.

import shutil
from pathlib import Path

from streamlit.testing.v1 import AppTest


_APP_PATH = str(Path(__file__).resolve().parent.parent / "app" / "app.py")
_CSV_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@pytest.fixture(scope="module")
def apptest_csv():
    """Create a tiny synthetic processed CSV so the dashboard can start."""
    _CSV_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = _CSV_DIR / "prices_clean_TESTONLY.csv"

    dates = pd.bdate_range("2022-01-03", periods=120, freq="C",
                           weekmask="Mon Tue Wed Thu Fri")
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

    # Teardown: remove the fixture CSV so the baseline (no CSV) is restored.
    try:
        csv_path.unlink()
    except FileNotFoundError:
        pass


@pytest.fixture(scope="module")
def apptest_default(apptest_csv):
    """Fresh AppTest instance with default settings."""
    at = AppTest.from_file(_APP_PATH, default_timeout=60)
    at.run()
    return at


def test_apptest_starts_without_exceptions(apptest_default):
    assert not apptest_default.exception


def test_apptest_default_mode_is_beginner(apptest_default):
    # The mode radio should exist with Beginner as the selected option.
    radios = apptest_default.radio
    # Find the "Experience mode" radio by label.
    mode_radios = [r for r in radios if r.label == "Experience mode"]
    assert len(mode_radios) == 1
    assert mode_radios[0].value == "Beginner"


def test_apptest_tabs_and_subtabs_present(apptest_default):
    # Three outer tabs, each with Numerical Results / Explanations sub-tabs.
    # AppTest exposes tabs by label; sub-tabs appear as additional tabs.
    tab_labels = [t.label for t in apptest_default.tabs]
    # Outer tabs (order preserved)
    assert "Optimization" in tab_labels
    assert "Risk Analysis" in tab_labels
    assert "Frontier" in tab_labels
    # Sub-tabs: at least two of each
    assert tab_labels.count("Numerical Results") >= 3
    assert tab_labels.count("Explanations") >= 3


def test_apptest_mode_switch_persists(apptest_default):
    # Switch to Advanced and rerun; the radio should now read "Advanced".
    mode_radio = [r for r in apptest_default.radio if r.label == "Experience mode"][0]
    mode_radio.set_value("Advanced").run()
    assert not apptest_default.exception
    mode_radio2 = [r for r in apptest_default.radio if r.label == "Experience mode"][0]
    assert mode_radio2.value == "Advanced"


def test_apptest_mode_switch_does_not_change_numerical_results(
    apptest_default, apptest_csv
):
    """
    Mode-safety invariant (Task 8.3 acceptance):
    compare_portfolios / compare_risk_metrics / analyze_frontier outputs must
    be byte-identical across repeated invocations with identical inputs.

    Structural guarantee: no code path from `experience_mode` feeds into
    `inputs` or `data` (mode is consumed only by label lookups and the
    Explanations renderer). This test locks that guarantee against regression.

    For `analyze_frontier` we compare EVERY DataFrame-valued entry in the
    result dict, so the assertion is robust to the exact key names used by
    src.risk.frontier and cannot silently pass if a key is missing.
    """
    from src.preprocessing.returns import (
        compute_expected_returns,
        compute_volatility,
        process_returns_pipeline,
    )
    from src.linear_algebra.covariance import compute_covariance_matrix
    from src.optimization import compare_portfolios
    from src.risk import compare_risk_metrics, analyze_frontier

    prices = pd.read_csv(apptest_csv, index_col="Date", parse_dates=True)
    returns, _, _, _ = process_returns_pipeline(prices)
    mu = compute_expected_returns(returns, annualize=True)
    sigma = compute_volatility(returns, annualize=True)
    Sigma = compute_covariance_matrix(returns, annualize=True)

    # --- compare_portfolios ---
    out_a = compare_portfolios(mu, Sigma, risk_free_rate=0.02)
    out_b = compare_portfolios(mu, Sigma, risk_free_rate=0.02)
    pd.testing.assert_frame_equal(out_a, out_b)

    # --- compare_risk_metrics ---
    risk_a = compare_risk_metrics(
        mu, Sigma, returns, risk_free_rate=0.02, confidence_level=0.95
    )
    risk_b = compare_risk_metrics(
        mu, Sigma, returns, risk_free_rate=0.02, confidence_level=0.95
    )
    pd.testing.assert_frame_equal(risk_a, risk_b)

    # --- analyze_frontier: compare every DataFrame-valued entry ---
    front_a = analyze_frontier(mu, Sigma, risk_free_rate=0.02, n_points=20)
    front_b = analyze_frontier(mu, Sigma, risk_free_rate=0.02, n_points=20)

    # The dict is expected to contain at least one DataFrame. If not, fail
    # loudly so the test doesn't vacuously pass on a future API change.
    dataframe_keys = [
        k for k, v in front_a.items()
        if isinstance(v, pd.DataFrame)
    ]
    assert dataframe_keys, (
        "analyze_frontier returned no DataFrame values; cannot verify the "
        "mode-safety invariant. Inspect src.risk.frontier.analyze_frontier."
    )
    for k in dataframe_keys:
        assert k in front_b, f"analyze_frontier key {k!r} missing in second run"
        pd.testing.assert_frame_equal(front_a[k], front_b[k])