"""
app/personalisation.py
Phase 8 — Task 8.6: optional personalisation inputs.

All fields are optional. Blank / missing values must never block the
optimization. Two fields are purely explanatory (horizon, risk tolerance,
objective); one is presentation-only but functional (investment amount →
dollar allocation); one is a **read-only reflection** of the sidebar's
target return (single source of truth, per maintainer decision Q2=b).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

import numpy as np
import pandas as pd

ExperienceMode = Literal["Beginner", "Advanced"]

# ---------------------------------------------------------------------------
# Categorical options (documented in the Phase 8 doc)
# ---------------------------------------------------------------------------

HORIZON_OPTIONS: tuple[str, ...] = ("", "Short (< 3 years)",
                                    "Medium (3–10 years)",
                                    "Long (> 10 years)")
RISK_TOLERANCE_OPTIONS: tuple[str, ...] = ("", "Low", "Medium", "High")
OBJECTIVE_OPTIONS: tuple[str, ...] = ("", "Growth", "Income", "Capital preservation")

# Soft ceiling for the investment amount. Above this, warn (not error) so a
# user entering $10,000,000 is never silently rejected.
AMOUNT_WARN_THRESHOLD: float = 100_000_000.0  # $100M
AMOUNT_HARD_LIMIT: float = 1_000_000_000_000.0  # $1T — sanity only


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Personalisation:
    amount: Optional[float] = None            # dollars, >= 0
    horizon: str = ""                         # one of HORIZON_OPTIONS
    risk_tolerance: str = ""                  # one of RISK_TOLERANCE_OPTIONS
    objective: str = ""                       # one of OBJECTIVE_OPTIONS
    target_return_reflection: Optional[float] = None  # read-only copy of sidebar target

    def is_empty(self) -> bool:
        """True if the user has not entered any personalisation."""
        return (
            self.amount is None
            and not self.horizon
            and not self.risk_tolerance
            and not self.objective
            and self.target_return_reflection is None
        )


# ---------------------------------------------------------------------------
# Validation (pure)
# ---------------------------------------------------------------------------


def validate_personalisation(
    amount: Optional[float],
    horizon: str,
    risk_tolerance: str,
    objective: str,
) -> tuple[list[str], list[str]]:
    """
    Return (errors, warnings).

    - errors block conversion to dollars but must NOT block the optimization.
    - warnings are informational only.
    - Blank inputs are always valid.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if amount is not None:
        try:
            a = float(amount)
        except (TypeError, ValueError):
            errors.append("Investment amount must be a number.")
        else:
            if not np.isfinite(a):
                errors.append("Investment amount must be finite.")
            elif a < 0:
                errors.append("Investment amount cannot be negative.")
            elif a == 0:
                warnings.append(
                    "Investment amount is 0 — dollar allocations will all be $0."
                )
            elif a > AMOUNT_HARD_LIMIT:
                errors.append(
                    f"Investment amount {a:,.0f} exceeds the sanity ceiling "
                    f"of {AMOUNT_HARD_LIMIT:,.0f}."
                )
            elif a > AMOUNT_WARN_THRESHOLD:
                warnings.append(
                    f"Investment amount {a:,.0f} is very large — double-check "
                    "the figure."
                )

    if horizon and horizon not in HORIZON_OPTIONS:
        errors.append(f"Unknown horizon {horizon!r}.")
    if risk_tolerance and risk_tolerance not in RISK_TOLERANCE_OPTIONS:
        errors.append(f"Unknown risk tolerance {risk_tolerance!r}.")
    if objective and objective not in OBJECTIVE_OPTIONS:
        errors.append(f"Unknown objective {objective!r}.")

    return errors, warnings


# ---------------------------------------------------------------------------
# Monetary allocation (pure)
# ---------------------------------------------------------------------------


def weights_to_dollars(weights: pd.Series, amount: Optional[float]) -> pd.Series:
    """
    Convert weights to dollars. Returns a genuinely empty Series (length 0,
    no index) when `amount` is None or non-positive, or when amount is not
    a finite number. This is the sentinel contract documented in
    docs/phase8_dashboard_experience.md Task 8.6 and asserted by
    tests/test_personalisation.py::test_weights_to_dollars_*.

    Weights are *not* re-normalised — the caller is expected to pass the
    optimizer's raw weights. Non-finite weights become 0 dollars.
    """
    if amount is None:
        return pd.Series(dtype=float)
    try:
        a = float(amount)
    except (TypeError, ValueError):
        return pd.Series(dtype=float)
    if not np.isfinite(a) or a < 0:
        return pd.Series(dtype=float)

    arr = pd.Series(weights, copy=True).astype(float)
    arr = arr.where(np.isfinite(arr), 0.0)
    return (arr * a).rename("dollars")


# ---------------------------------------------------------------------------
# Streamlit renderer
# ---------------------------------------------------------------------------


def render_personalisation_panel(
    *,
    sidebar_target_return: Optional[float],
    sidebar_include_target: bool,
) -> Personalisation:
    """
    Render the optional personalisation controls in a sidebar expander.
    Returns a Personalisation dataclass. Never blocks the optimization —
    validation errors are surfaced as sidebar errors, but the dict values
    remain available (the optimizer does not consume them).
    """
    import streamlit as st  # local import — keep helpers pure-testable

    with st.sidebar.expander("Personalise (optional)", expanded=False):
        st.caption(
            "All fields are optional. They help tailor the explanations and "
            "convert weights into dollar amounts. They never change the "
            "optimization."
        )

        amount_raw = st.number_input(
            "Investment amount (USD, optional)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f",
            help="Leave at 0 to skip dollar allocation.",
        )
        # Treat exactly-zero as "not provided" so blank is easy to restore.
        amount: Optional[float] = float(amount_raw) if amount_raw > 0 else None

        horizon = st.selectbox("Investment horizon", options=HORIZON_OPTIONS, index=0)
        risk_tol = st.selectbox("Risk tolerance", options=RISK_TOLERANCE_OPTIONS, index=0)
        objective = st.selectbox("Objective", options=OBJECTIVE_OPTIONS, index=0)

        # Read-only reflection of sidebar target return (single source of truth).
        if sidebar_include_target and sidebar_target_return is not None:
            st.markdown(
                f"**Target return (from sidebar):** "
                f"{sidebar_target_return*100:.2f}% _(read-only)_"
            )
            reflection = float(sidebar_target_return)
        else:
            st.markdown("**Target return (from sidebar):** — _(not enabled)_")
            reflection = None

        errors, warnings = validate_personalisation(
            amount, horizon, risk_tol, objective
        )
        for w in warnings:
            st.warning(w)
        for e in errors:
            st.error(e)

    return Personalisation(
        amount=amount,
        horizon=horizon,
        risk_tolerance=risk_tol,
        objective=objective,
        target_return_reflection=reflection,
    )


def render_beginner_context_callout(
    personalisation: Personalisation, mode: ExperienceMode
) -> None:
    """
    Render a 'what this means for you' block. No-op for Advanced mode or
    when personalisation is empty. Pure presentation.
    """
    if mode != "Beginner" or personalisation.is_empty():
        return

    import streamlit as st

    lines: list[str] = []
    if personalisation.amount is not None and personalisation.amount > 0:
        lines.append(
            f"- With **${personalisation.amount:,.0f}** invested, multiply each "
            "weight by this amount to get the dollars in that asset."
        )
    if personalisation.horizon:
        lines.append(
            f"- Your **{personalisation.horizon.lower()}** horizon means "
            "short-term swings matter "
            + ("a lot" if personalisation.horizon.startswith("Short") else
               "less" if personalisation.horizon.startswith("Long") else "somewhat")
            + " more than the long-run average."
        )
    if personalisation.risk_tolerance:
        lines.append(
            f"- With **{personalisation.risk_tolerance.lower()}** risk tolerance, "
            "compare the Min Volatility and Max Sharpe rows — they usually sit "
            "at opposite ends of the risk scale."
        )
    if personalisation.objective:
        lines.append(
            f"- Your **{personalisation.objective.lower()}** objective often "
            "favours a particular row: Growth → Max Sharpe; Income or "
            "Preservation → Min Volatility."
        )
    if personalisation.target_return_reflection is not None:
        lines.append(
            f"- The **{personalisation.target_return_reflection*100:.2f}%** "
            "target set in the sidebar is what the Target Return row aims at."
        )

    if not lines:
        return

    st.info("**What this means for you**\n\n" + "\n".join(lines))