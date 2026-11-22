"""
app/risk_warnings.py
Phase 8 — Task 8.7: metric-based risk warnings.

Rules are pure functions over already-calculated metrics:
  - portfolio volatility (annualised)
  - VaR at the chosen confidence
  - CVaR at the chosen confidence
  - maximum drawdown
  - portfolio concentration (Herfindahl-Hirschman Index of weights)

Every emitted warning must name the triggering metric and explain the
practical implication. Thresholds are documented in this file and in
docs/phase8_dashboard_experience.md. No rule computes a new risk metric;
all inputs are already produced by src.risk / src.optimization.

The renderer is a thin wrapper over the rules. Warnings are non-alarmist
and are not predictions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np
import pandas as pd

ExperienceMode = Literal["Beginner", "Advanced"]

# ---------------------------------------------------------------------------
# Documented thresholds (referenced in Phase 8 doc and test suite)
# ---------------------------------------------------------------------------

# Annualised volatility of the portfolio (decimal). 30% ≈ S&P 500 bull-market
# regime; 50% ≈ single-stock/emerging-market territory.
VOLATILITY_HIGH = 0.30
VOLATILITY_EXTREME = 0.50

# Portfolio concentration: HHI = Σ wᵢ². For n equal weights, HHI = 1/n.
# 1 asset = 1.0; 2 assets = 0.5; 4 = 0.25; 10 = 0.10.
# HHI ≥ 0.40 ≈ a 2-3 asset portfolio; HHI ≥ 0.60 ≈ 1-2 assets.
CONCENTRATION_HIGH = 0.40
CONCENTRATION_EXTREME = 0.60

# Daily VaR thresholds at 95% confidence. Portfolio-level.
# 2.5% daily ≈ ~40% annualised volatility.
VAR_DAILY_HIGH = 0.025
VAR_DAILY_EXTREME = 0.040

# Max drawdown (negative). −25% is a normal correction; −50% a severe crash.
DRAWDOWN_HIGH = -0.25
DRAWDOWN_EXTREME = -0.50


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Warning:
    """A single warning tied to a triggering metric."""
    metric: str          # "volatility" | "var_95" | "cvar_95" |
                         # "max_drawdown" | "concentration"
    severity: str        # "warning" | "extreme"
    short: str           # one-line Beginner wording
    detail: str          # Advanced wording with number & interpretation
    value: float         # the triggering value (for transparency)


# ---------------------------------------------------------------------------
# Rules — pure functions
# ---------------------------------------------------------------------------


def _is_finite(x: object) -> bool:
    try:
        return x is not None and np.isfinite(float(x))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


def herfindahl_index(weights: pd.Series | Iterable[float]) -> float:
    """
    Return HHI = Σ wᵢ². Weights should sum to ~1; NaNs contribute 0.
    Returns NaN if no finite weights are present.
    """
    if isinstance(weights, pd.Series):
        arr = weights.to_numpy(dtype=float)
    else:
        arr = np.asarray(list(weights), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return float("nan")
    return float(np.sum(arr * arr))


def volatility_warning(volatility: float) -> Warning | None:
    if not _is_finite(volatility) or volatility <= 0:
        return None
    if volatility >= VOLATILITY_EXTREME:
        return Warning(
            metric="volatility",
            severity="extreme",
            short=(
                "This portfolio swings a lot — it can drop sharply in a "
                "single year."
            ),
            detail=(
                f"Annualised volatility is {volatility*100:.1f}%, above the "
                f"extreme threshold of {VOLATILITY_EXTREME*100:.0f}%. "
                "Expect multi-year path dependence; risk of large interim "
                "losses if you need the money soon."
            ),
            value=volatility,
        )
    if volatility >= VOLATILITY_HIGH:
        return Warning(
            metric="volatility",
            severity="warning",
            short=(
                "This portfolio is on the bumpy side — expect sizable "
                "up-and-down years."
            ),
            detail=(
                f"Annualised volatility is {volatility*100:.1f}%, above the "
                f"warning threshold of {VOLATILITY_HIGH*100:.0f}%. "
                "A normal year could show double-digit moves in either "
                "direction."
            ),
            value=volatility,
        )
    return None


def var_warning(var: float, confidence: float) -> Warning | None:
    if not _is_finite(var) or var <= 0:
        return None
    # Thresholds are calibrated at 95%. Scale linearly toward higher
    # confidence so 99% doesn't fire spuriously and 90% doesn't under-fire.
    scale = confidence / 0.95 if 0 < confidence < 1 else 1.0
    high = VAR_DAILY_HIGH * scale
    extreme = VAR_DAILY_EXTREME * scale
    if var >= extreme:
        return Warning(
            metric="var_95",
            severity="extreme",
            short=(
                "On a bad day, losses can be large — make sure you could "
                "ride this out."
            ),
            detail=(
                f"Daily VaR at {confidence*100:.0f}% is {var*100:.2f}% of "
                "portfolio value. Thresholds are scaled from 95% "
                f"({VAR_DAILY_EXTREME*100:.1f}% extreme)."
            ),
            value=var,
        )
    if var >= high:
        return Warning(
            metric="var_95",
            severity="warning",
            short=(
                "On about 1 day in 20, the portfolio is expected to lose "
                "at least this much."
            ),
            detail=(
                f"Daily VaR at {confidence*100:.0f}% is {var*100:.2f}% of "
                f"portfolio value (threshold {high*100:.2f}%)."
            ),
            value=var,
        )
    return None


def cvar_warning(cvar: float, var: float | None, confidence: float) -> Warning | None:
    """
    CVaR severity based on the *additional* tail loss beyond VaR. If cvar
    is comparable to VaR, the tail is thin. If cvar >> var, the tail is fat.
    """
    if not _is_finite(cvar) or cvar <= 0:
        return None
    if _is_finite(var) and var > 0:
        ratio = cvar / var
        if ratio >= 2.0:
            return Warning(
                metric="cvar_95",
                severity="extreme",
                short=(
                    "When losses are big, they get very big — the worst days "
                    "are much worse than the typical bad day."
                ),
                detail=(
                    f"CVaR is {ratio:.1f}× VaR ({cvar*100:.2f}% vs "
                    f"{var*100:.2f}%). Tail is heavy; 'average worst day' "
                    "substantially exceeds the VaR threshold."
                ),
                value=cvar,
            )
        if ratio >= 1.4:
            return Warning(
                metric="cvar_95",
                severity="warning",
                short=(
                    "Bad days are meaningfully worse than the bad-day "
                    "threshold suggests."
                ),
                detail=(
                    f"CVaR is {ratio:.1f}× VaR ({cvar*100:.2f}% vs "
                    f"{var*100:.2f}%)."
                ),
                value=cvar,
            )
    return None


def drawdown_warning(max_drawdown: float) -> Warning | None:
    if not _is_finite(max_drawdown):
        return None
    # max_drawdown is non-positive. Convert to magnitude for thresholds.
    mdd = -float(max_drawdown)
    if mdd <= 0:
        return None
    if mdd >= -DRAWDOWN_EXTREME:
        return Warning(
            metric="max_drawdown",
            severity="extreme",
            short=(
                "This portfolio has lost more than half its value at its "
                "worst point — that is a severe crash."
            ),
            detail=(
                f"Maximum drawdown reached {max_drawdown*100:.1f}% "
                f"(extreme threshold {DRAWDOWN_EXTREME*100:.0f}%)."
            ),
            value=max_drawdown,
        )
    if mdd >= -DRAWDOWN_HIGH:
        return Warning(
            metric="max_drawdown",
            severity="warning",
            short=(
                "This portfolio has had a large peak-to-bottom drop — plan "
                "for the recovery time."
            ),
            detail=(
                f"Maximum drawdown reached {max_drawdown*100:.1f}% "
                f"(warning threshold {DRAWDOWN_HIGH*100:.0f}%)."
            ),
            value=max_drawdown,
        )
    return None


def concentration_warning(weights: pd.Series) -> Warning | None:
    hhi = herfindahl_index(weights)
    if not _is_finite(hhi) or hhi <= 0:
        return None
    if hhi >= CONCENTRATION_EXTREME:
        return Warning(
            metric="concentration",
            severity="extreme",
            short=(
                "This portfolio is very concentrated — one or two assets "
                "drive almost all of the risk."
            ),
            detail=(
                f"HHI concentration index = {hhi:.2f} "
                f"(extreme threshold {CONCENTRATION_EXTREME}). "
                "Equivalent to ~1–2 equally-weighted assets."
            ),
            value=hhi,
        )
    if hhi >= CONCENTRATION_HIGH:
        return Warning(
            metric="concentration",
            severity="warning",
            short=(
                "This portfolio is fairly concentrated — a few assets "
                "dominate."
            ),
            detail=(
                f"HHI concentration index = {hhi:.2f} "
                f"(warning threshold {CONCENTRATION_HIGH}). "
                "Equivalent to ~2–3 equally-weighted assets."
            ),
            value=hhi,
        )
    return None


def evaluate_all(
    *,
    volatility: float,
    var: float,
    cvar: float,
    max_drawdown: float,
    weights: pd.Series,
    confidence: float,
) -> list[Warning]:
    """
    Run every rule, discard None, and return warnings ordered by severity
    (extreme first) then by metric name for stable display.
    """
    candidates = [
        volatility_warning(volatility),
        var_warning(var, confidence),
        cvar_warning(cvar, var, confidence),
        drawdown_warning(max_drawdown),
        concentration_warning(weights),
    ]
    warnings = [w for w in candidates if w is not None]
    # Stable ordering: extreme before warning, then metric name.
    warnings.sort(key=lambda w: (0 if w.severity == "extreme" else 1, w.metric))
    return warnings


# ---------------------------------------------------------------------------
# Renderer (thin)
# ---------------------------------------------------------------------------


def render_risk_warnings(
    *,
    warnings: list[Warning],
    mode: ExperienceMode,
) -> None:
    """Render the warning list to Streamlit. Caller passes pre-computed warnings."""
    import streamlit as st  # local import: keeps rules pure-testable

    if not warnings:
        st.success("No metric-based risk warnings triggered for this portfolio.")
        return

    st.subheader("Risk warnings")
    for w in warnings:
        icon = "🚨" if w.severity == "extreme" else "⚠️"
        text = w.short if mode == "Beginner" else f"{w.detail} (triggered by `{w.metric}`)"
        # st.warning for both severities; icon + ordering communicates the
        # difference. Using st.warning (not st.error) keeps the tone
        # non-alarmist per the project safeguards.
        st.warning(f"{icon} {text}")