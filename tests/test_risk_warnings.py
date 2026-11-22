"""Phase 8 — Task 8.7 tests for app/risk_warnings.py."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

import app.risk_warnings as rw


# ---------------------------------------------------------------------------
# HHI
# ---------------------------------------------------------------------------


def test_hhi_equal_two_assets_is_half():
    assert rw.herfindahl_index(pd.Series([0.5, 0.5])) == pytest.approx(0.5)


def test_hhi_single_asset_is_one():
    assert rw.herfindahl_index(pd.Series([1.0])) == pytest.approx(1.0)


def test_hhi_ten_equal_is_tenth():
    assert rw.herfindahl_index(pd.Series([0.1] * 10)) == pytest.approx(0.10)


def test_hhi_ignores_nan():
    assert rw.herfindahl_index(pd.Series([0.5, float("nan"), 0.5])) == pytest.approx(0.5)


def test_hhi_all_nan_is_nan():
    assert math.isnan(rw.herfindahl_index(pd.Series([float("nan")])))


# ---------------------------------------------------------------------------
# Volatility
# ---------------------------------------------------------------------------


def test_volatility_below_threshold_no_warning():
    assert rw.volatility_warning(0.15) is None


def test_volatility_warning_at_threshold():
    w = rw.volatility_warning(rw.VOLATILITY_HIGH)
    assert w is not None and w.severity == "warning"


def test_volatility_extreme_at_threshold():
    w = rw.volatility_warning(rw.VOLATILITY_EXTREME)
    assert w is not None and w.severity == "extreme"


def test_volatility_nan_no_warning():
    assert rw.volatility_warning(float("nan")) is None


def test_volatility_non_positive_no_warning():
    assert rw.volatility_warning(0.0) is None
    assert rw.volatility_warning(-0.1) is None


# ---------------------------------------------------------------------------
# VaR
# ---------------------------------------------------------------------------


def test_var_below_threshold_no_warning():
    assert rw.var_warning(0.010, 0.95) is None


def test_var_warning_at_threshold():
    w = rw.var_warning(rw.VAR_DAILY_HIGH, 0.95)
    assert w is not None and w.severity == "warning"


def test_var_extreme_at_threshold():
    w = rw.var_warning(rw.VAR_DAILY_EXTREME, 0.95)
    assert w is not None and w.severity == "extreme"


def test_var_threshold_scales_with_confidence():
    # Same raw VaR; at 99% confidence the effective threshold is higher
    # (scaled by 99/95), so a value just above the 95% threshold should
    # still warn at 95% but not at 99%.
    raw = rw.VAR_DAILY_HIGH * 1.01
    assert rw.var_warning(raw, 0.95) is not None
    assert rw.var_warning(raw, 0.99) is None


# ---------------------------------------------------------------------------
# CVaR
# ---------------------------------------------------------------------------


def test_cvar_no_var_returns_none():
    assert rw.cvar_warning(0.04, None, 0.95) is None


def test_cvar_thin_tail_no_warning():
    # CVaR barely above VaR → thin tail → no warning
    assert rw.cvar_warning(0.031, 0.030, 0.95) is None


def test_cvar_ratio_warning():
    w = rw.cvar_warning(0.045, 0.030, 0.95)  # ratio 1.5 → warning
    assert w is not None and w.severity == "warning"


def test_cvar_ratio_extreme():
    w = rw.cvar_warning(0.070, 0.030, 0.95)  # ratio 2.33 → extreme
    assert w is not None and w.severity == "extreme"


# ---------------------------------------------------------------------------
# Max drawdown
# ---------------------------------------------------------------------------


def test_drawdown_small_no_warning():
    assert rw.drawdown_warning(-0.10) is None


def test_drawdown_warning_at_threshold():
    w = rw.drawdown_warning(rw.DRAWDOWN_HIGH)  # -0.25
    assert w is not None and w.severity == "warning"


def test_drawdown_extreme_at_threshold():
    w = rw.drawdown_warning(rw.DRAWDOWN_EXTREME)  # -0.50
    assert w is not None and w.severity == "extreme"


def test_drawdown_zero_no_warning():
    assert rw.drawdown_warning(0.0) is None


def test_drawdown_nan_no_warning():
    assert rw.drawdown_warning(float("nan")) is None


# ---------------------------------------------------------------------------
# Concentration
# ---------------------------------------------------------------------------


def test_concentration_two_asset_triggers_warning():
    w = rw.concentration_warning(pd.Series([0.5, 0.5]))
    assert w is not None and w.severity == "warning"


def test_concentration_single_asset_extreme():
    w = rw.concentration_warning(pd.Series([1.0]))
    assert w is not None and w.severity == "extreme"


def test_concentration_equal_ten_no_warning():
    assert rw.concentration_warning(pd.Series([0.1] * 10)) is None


# ---------------------------------------------------------------------------
# evaluate_all — ordering and composition
# ---------------------------------------------------------------------------


def test_evaluate_all_returns_extreme_first():
    warnings = rw.evaluate_all(
        volatility=rw.VOLATILITY_EXTREME,
        var=0.010,            # below warning threshold
        cvar=0.011,
        max_drawdown=-0.10,   # below warning threshold
        weights=pd.Series([0.5, 0.5]),  # warning-level concentration
        confidence=0.95,
    )
    assert warnings, "expected at least one warning"
    assert warnings[0].severity == "extreme"
    # All subsequent must be non-extreme (warnings)
    assert all(w.severity == "warning" for w in warnings[1:])


def test_evaluate_all_all_below_threshold():
    warnings = rw.evaluate_all(
        volatility=0.10,
        var=0.005,
        cvar=0.006,
        max_drawdown=-0.05,
        weights=pd.Series([0.1] * 10),
        confidence=0.95,
    )
    assert warnings == []


def test_evaluate_all_handles_nan_inputs():
    warnings = rw.evaluate_all(
        volatility=float("nan"),
        var=float("nan"),
        cvar=float("nan"),
        max_drawdown=float("nan"),
        weights=pd.Series([float("nan")]),
        confidence=0.95,
    )
    assert warnings == []


# ---------------------------------------------------------------------------
# Warnings carry their triggering value
# ---------------------------------------------------------------------------


def test_warning_has_metric_and_value():
    w = rw.volatility_warning(0.55)
    assert w is not None
    assert w.metric == "volatility"
    assert w.value == pytest.approx(0.55)
    assert "volatility" in w.detail.lower() or "Annualised" in w.detail


def test_warning_short_differs_from_detail():
    w = rw.var_warning(0.05, 0.95)
    assert w is not None
    assert w.short != w.detail