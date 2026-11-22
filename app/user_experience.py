"""
app/user_experience.py
Phase 8 — Task 8.3 / 8.4: experience-mode presentation layer.

This module is presentation-only. It never calls `src.*`, never touches
`inputs` or `data`, and never changes any numerical result. The mode value
is consumed solely by label lookups, expander placement, and the
Explanations sub-tab.

Mode value lives in `st.session_state["experience_mode"]` and is one of
`EXPERIENCE_MODES`. Default is "Beginner".
"""

from __future__ import annotations

from typing import Literal

import streamlit as st

ExperienceMode = Literal["Beginner", "Advanced"]

EXPERIENCE_MODES: tuple[ExperienceMode, ExperienceMode] = ("Beginner", "Advanced")
DEFAULT_MODE: ExperienceMode = "Beginner"
_MODE_KEY = "experience_mode"
_TOGGLE_KEY = "experience_mode_toggle"


# ---------------------------------------------------------------------------
# Terminology: metric / portfolio display labels per mode
# ---------------------------------------------------------------------------

# Metric keys correspond to real columns produced by src.optimization
# (return, volatility, variance, sharpe, n_iter, success) and src.risk
# (var_95, cvar_95, max_drawdown). Do NOT rename calculation columns here —
# only the *display* column label changes.
_METRIC_LABELS: dict[str, dict[ExperienceMode, str]] = {
    "return":       {"Beginner": "Expected yearly gain",     "Advanced": "Expected return (annualised)"},
    "volatility":   {"Beginner": "How much it swings",       "Advanced": "Volatility (annualised σ)"},
    "variance":     {"Beginner": "Variance",                 "Advanced": "Variance (σ²)"},
    "sharpe":       {"Beginner": "Reward-for-risk score",    "Advanced": "Sharpe ratio"},
    "var_95":       {"Beginner": "Bad-day loss estimate",    "Advanced": "VaR"},
    "cvar_95":      {"Beginner": "Worst-case average loss",  "Advanced": "CVaR (Expected Shortfall)"},
    "max_drawdown": {"Beginner": "Worst peak-to-bottom drop","Advanced": "Maximum drawdown"},
    "n_iter":       {"Beginner": "Iterations",               "Advanced": "Iterations"},
    "success":      {"Beginner": "Solved?",                  "Advanced": "Solver success"},
}

# Weight-column label per ticker is identical in both modes (the ticker
# symbol itself is the label). Portfolio-name labels change:
_PORTFOLIO_LABELS: dict[str, dict[ExperienceMode, str]] = {
    "EqualWeight":    {"Beginner": "Even split",           "Advanced": "Equal-weight portfolio"},
    "MinVolatility":  {"Beginner": "Safest mix",           "Advanced": "Minimum-volatility portfolio"},
    "MaxSharpe":      {"Beginner": "Best reward-for-risk", "Advanced": "Maximum-Sharpe portfolio"},
    "TargetReturn":   {"Beginner": "Your target mix",      "Advanced": "Target-return portfolio"},
}

# Metrics that are HIDDEN in Beginner mode (all metrics remain in Advanced).
_BEGINNER_HIDDEN_METRICS: frozenset[str] = frozenset({"variance", "n_iter"})


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_mode() -> ExperienceMode:
    """Return the current mode, initialising session state if missing."""
    if _MODE_KEY not in st.session_state:
        st.session_state[_MODE_KEY] = DEFAULT_MODE
    return st.session_state[_MODE_KEY]


def set_mode(mode: ExperienceMode) -> None:
    """Set the mode in session state. Raises on unknown value."""
    if mode not in EXPERIENCE_MODES:
        raise ValueError(f"Unknown experience mode: {mode!r}")
    st.session_state[_MODE_KEY] = mode


def render_mode_toggle() -> ExperienceMode:
    """
    Render the Beginner/Advanced toggle and return the active mode.

    Uses `st.radio` for accessibility (visible choice, keyboard-navigable).
    Persisted in session state so it survives reruns.
    """
    if _MODE_KEY not in st.session_state:
        st.session_state[_MODE_KEY] = DEFAULT_MODE

    choice = st.radio(
        "Experience mode",
        options=list(EXPERIENCE_MODES),
        index=list(EXPERIENCE_MODES).index(st.session_state[_MODE_KEY]),
        horizontal=True,
        key=_TOGGLE_KEY,
        help=(
            "Beginner uses plain language and the most important results. "
            "Advanced shows full technical detail and all controls. "
            "Switching mode never changes your calculations."
        ),
    )
    # Keep state in sync even if the widget is the source of truth.
    st.session_state[_MODE_KEY] = choice
    return choice


def metric_label(key: str, mode: ExperienceMode) -> str:
    """Return the display label for a metric key in the given mode."""
    labels = _METRIC_LABELS.get(key)
    if labels is None:
        return key  # unknown key — pass through, never crash the UI
    return labels[mode]


def portfolio_label(name: str, mode: ExperienceMode) -> str:
    """Return the display label for a portfolio row-name in the given mode."""
    labels = _PORTFOLIO_LABELS.get(name)
    if labels is None:
        return name
    return labels[mode]          # ← FIXED: inner dict is keyed by mode


def should_show_metric(key: str, mode: ExperienceMode) -> bool:
    """Whether a metric column is visible in the given mode."""
    if mode == "Advanced":
        return True
    return key not in _BEGINNER_HIDDEN_METRICS


def apply_display_labels(df, mode: ExperienceMode):
    """
    Return a copy of `df` with metric/portfolio display labels applied.
    Calculation columns and values are unchanged; only index/column *labels*
    that map to known keys are renamed. Unknown labels pass through.

    Beginner mode also drops the metrics in `_BEGINNER_HIDDEN_METRICS`.
    """
    out = df.copy()

    # Rename columns that match a known metric key.
    rename_cols = {}
    for col in out.columns:
        if col in _METRIC_LABELS:
            rename_cols[col] = _METRIC_LABELS[col][mode]
    out = out.rename(columns=rename_cols)

    # Rename row-index entries that match a known portfolio name.
    rename_idx = {}
    for name in out.index:
        if name in _PORTFOLIO_LABELS:
            rename_idx[name] = _PORTFOLIO_LABELS[name][mode]
    out = out.rename(index=rename_idx)

    # Drop Beginner-hidden metrics (only if still present under original key).
    if mode == "Beginner":
        drop = [c for c in out.columns if c in _BEGINNER_HIDDEN_METRICS]
        if drop:
            out = out.drop(columns=drop)

    return out


# ---------------------------------------------------------------------------
# Explanations sub-tab (Task 8.4 stub — real content lands in Task 8.5)
# ---------------------------------------------------------------------------


def render_explanations_panel(
    mode: ExperienceMode,
    *,
    tab_name: str,
    keys: list[str] | None = None,
    personalisation=None,
) -> None:
    """
    Render the Explanations sub-tab.

    Phase 8 (Task 8.6): `personalisation` is an optional
    `app.personalisation.Personalisation` instance. When provided in
    Beginner mode, a "What this means for you" callout is appended.
    """
    from app.explanations import get_explanation
    from app.personalisation import render_beginner_context_callout

    defaults_by_tab = {
        "Optimization": [
            "objective", "constraint", "weights", "return", "volatility",
            "sharpe", "mean_return", "covariance", "target_return",
            "investment_amount",
        ],
        "Risk Analysis": [
            "var_95", "cvar_95", "max_drawdown", "volatility", "sharpe",
            "weights", "risk_tolerance",
        ],
        "Frontier": [
            "efficient_frontier", "objective", "correlation", "covariance",
            "horizon",
        ],
    }
    resolved = keys if keys is not None else defaults_by_tab.get(tab_name, [])

    st.subheader(f"Explanations — {tab_name}")
    if not resolved:
        st.info("No explanations registered for this tab.")
        return

    intro = (
        "Plain-English explanations of every number on this tab, with a "
        "practical example each."
        if mode == "Beginner"
        else "Technical definitions and interpretation notes for every metric "
             "on this tab."
    )
    st.caption(intro)

    if personalisation is not None:
        render_beginner_context_callout(personalisation, mode)

    for key in resolved:
        try:
            text = get_explanation(key, mode)
        except KeyError:
            continue
        with st.expander(_expand_label(key, mode), expanded=False):
            st.markdown(text)


def _expand_label(key: str, mode: ExperienceMode) -> str:
    """Human-readable expander label for the explanation entry."""
    # Reuse metric/portfolio label helpers when key is a metric, else
    # Title-Case the identifier.
    if key in _METRIC_LABELS:
        return metric_label(key, mode)
    return key.replace("_", " ").title()