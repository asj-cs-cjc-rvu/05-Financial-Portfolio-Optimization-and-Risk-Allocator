"""
app/explanations.py
Phase 8 — Task 8.5: explanation content for every displayed metric.

Content-only. No calculation logic lives here. Every entry is a dict with
two keys: "Beginner" (plain language, one practical example) and "Advanced"
(technical definition plus formula or interpretation note).

Keys are the same identifiers used by `app.user_experience`:
  return, volatility, variance, sharpe, var_95, cvar_95, max_drawdown,
  n_iter, success, weights, and the optimization concepts:
  mean_return, covariance, correlation, efficient_frontier, objective,
  constraint, target_return, investment_amount, horizon, risk_tolerance.
"""

from __future__ import annotations

EXPLANATIONS: dict[str, dict[str, str]] = {
    "return": {
        "Beginner": (
            "**Expected yearly gain** — how much your portfolio is expected "
            "to grow in a typical year, based on past data. "
            "*Example:* 10% means that, on average, every $1,000 invested is "
            "expected to become about $1,100 after one year. "
            "It is an estimate, not a promise."
        ),
        "Advanced": (
            "**Expected return (annualised)** — the weighted average of asset "
            "mean returns over the lookback window: `μ_p = wᵀ μ`. Computed "
            "from daily log returns with `mean × 252`. It is the centre "
            "of the portfolio return distribution, not a forecast."
        ),
    },
    "volatility": {
        "Beginner": (
            "**How much it typically swings** — the size of the up-and-down "
            "moves you should expect. Higher numbers mean a bumpier ride. "
            "*Example:* a portfolio with 15% typical swing might gain 15% "
            "one year and lose 10% the next — the average is still positive, "
            "but the journey is uneven."
        ),
        "Advanced": (
            "**Volatility** — annualised standard deviation of portfolio "
            "returns: `σ_p = √(wᵀ Σ w)`. Uses daily sample covariance "
            "(`ddof=1`) scaled by `√252`. It is the primary risk unit "
            "Markowitz optimisation trades off against return."
        ),
    },
    "variance": {
        "Beginner": "Variance is volatility squared — the math version of the same idea. Not shown in Beginner mode.",
        "Advanced": (
            "**Variance** — `σ²_p = wᵀ Σ w`. Quadratic form of the "
            "portfolio weights against the annualised covariance matrix. "
            "Units are (fraction)² — less interpretable than volatility but "
            "the direct objective in mean-variance optimisation."
        ),
    },
    "sharpe": {
        "Beginner": (
            "**Reward-for-risk score** — how much extra return you get for "
            "each unit of bumpiness. Higher is better. "
            "*Example:* a score of 1.0 is considered solid. A score of 2.0 "
            "means you're being paid twice as much per unit of risk. "
            "Negative scores mean you'd have done better in the risk-free "
            "asset over this window."
        ),
        "Advanced": (
            "**Sharpe ratio** — `S = (μ_p − r_f) / σ_p`. Excess annualised "
            "return per unit of annualised volatility. Undefined when "
            "`σ_p = 0` (guarded). The Maximum-Sharpe portfolio maximises "
            "this ratio subject to the budget and long-only constraints."
        ),
    },
    "var_95": {
        "Beginner": (
            "**Bad-day loss estimate** — on your worst 1-in-20 days (or "
            "1-in-10 or 1-in-100, depending on the confidence you chose), "
            "you should expect to lose *at least* this much in a single day. "
            "*Example:* a 2.5% VaR at 95% means that on about 5% of trading "
            "days, the daily loss is expected to be 2.5% or worse."
        ),
        "Advanced": (
            "**Value-at-Risk** — the `1 − α` quantile of the daily portfolio "
            "return distribution, reported as a positive loss magnitude. "
            "Empirical, historical calculation (`numpy.quantile`); no "
            "parametric assumption. VaR says nothing about the size of losses "
            "*beyond* the threshold — see CVaR."
        ),
    },
    "cvar_95": {
        "Beginner": (
            "**Worst-case average loss** — if today *is* one of those bad "
            "days, how bad is it typically? CVaR is always worse than VaR "
            "by design. "
            "*Example:* if VaR is 2.5% and CVaR is 4.0%, it means on the "
            "worst 5% of days the average loss is 4.0%, not just 2.5%."
        ),
        "Advanced": (
            "**Conditional Value-at-Risk (Expected Shortfall)** — the mean "
            "of the returns below the VaR threshold: `E[R | R ≤ −VaR]`. "
            "Coherent risk measure; captures tail severity that VaR misses. "
            "Falls back to VaR when the tail is too small to average."
        ),
    },
    "max_drawdown": {
        "Beginner": (
            "**Worst peak-to-bottom drop** — the biggest fall from a high "
            "point to a low point over the period. "
            "*Example:* −30% means the worst stretch of the portfolio lost "
            "roughly a third of its value before recovering. Shown as a "
            "negative percentage."
        ),
        "Advanced": (
            "**Maximum drawdown** — `min_t (V_t / max_{s ≤ t} V_s − 1)` on "
            "the cumulative return series. Non-positive by construction. "
            "Path-dependent, so it is *not* recoverable from `μ` and `Σ` "
            "alone; it requires the return series."
        ),
    },
    "n_iter": {
        "Beginner": "Not shown in Beginner mode — an internal solver counter.",
        "Advanced": (
            "**Solver iterations** — how many iterations `scipy.optimize.minimize` "
            "(SLSQP) took to converge. Useful for diagnosing slow convergence "
            "or non-converging problems; not a performance metric."
        ),
    },
    "success": {
        "Beginner": (
            "**Solved?** — whether the optimizer found a portfolio that meets "
            "the rules (weights sum to 1, no shorting). ✅ means yes."
        ),
        "Advanced": (
            "**Solver success flag** — `result.success` from SLSQP after "
            "constraint post-validation. A ❌ row remains in the table for "
            "transparency but its weights may violate constraints."
        ),
    },
    "weights": {
        "Beginner": (
            "**How your money is split** — the fraction of your portfolio "
            "in each ticker. A weight of 0.40 means 40% of the portfolio is "
            "in that asset. All weights sum to 1.00 (or 100%). "
            "*Example:* with $10,000 invested, a 0.40 weight is $4,000."
        ),
        "Advanced": (
            "**Allocation weights** — vector `w` with `wᵢ ≥ 0` and "
            "`Σ wᵢ = 1` (long-only, fully invested). The optimisation "
            "variable; all metrics are functions of `w`."
        ),
    },
    "mean_return": {
        "Beginner": (
            "**Average yearly return per asset** — used to estimate what a "
            "portfolio's overall return will be once you decide the weights. "
            "Not a forecast; a historical average."
        ),
        "Advanced": (
            "**Mean return vector μ** — per-asset annualised expected "
            "returns (`mean × 252` on daily log returns). Input to the "
            "mean-variance objective."
        ),
    },
    "covariance": {
        "Beginner": (
            "**How assets move together** — some assets zig when others zag, "
            "which reduces portfolio risk. The covariance matrix is how the "
            "optimizer knows this."
        ),
        "Advanced": (
            "**Covariance matrix Σ** — `n × n` annualised matrix; diagonal "
            "entries are asset variances, off-diagonal are covariances. "
            "Portfolio variance is the quadratic form `wᵀ Σ w`."
        ),
    },
    "correlation": {
        "Beginner": (
            "**Direction and strength of co-movement** — correlations near "
            "+1 move in lockstep, near −1 move oppositely, near 0 are "
            "unrelated. Lower correlations usually mean a smoother portfolio."
        ),
        "Advanced": (
            "**Correlation matrix** — `ρᵢⱼ = Σᵢⱼ / (σᵢ σⱼ)`. Range "
            "`[−1, +1]`. Used in the correlation heatmap; complements the "
            "covariance matrix for interpretation."
        ),
    },
    "efficient_frontier": {
        "Beginner": (
            "**The best trade-off curve** — every point on it is the best "
            "possible return for its risk level. Points below the curve are "
            "worse: same return with more risk, or same risk for less return."
        ),
        "Advanced": (
            "**Efficient frontier** — set of `(σ, μ)` points that solve "
            "min-variance given a target return, for a grid of targets in "
            "`[μ_min, μ_max]`. Points are (partially) sample-dependent; "
            "not a predictive curve."
        ),
    },
    "objective": {
        "Beginner": (
            "**What the optimizer is trying to achieve** — for Min Volatility, "
            "smallest possible swings; for Max Sharpe, best reward-for-risk; "
            "for Target Return, smallest risk for a specific return goal."
        ),
        "Advanced": (
            "**Optimisation objective** — one of: minimise variance "
            "(MinVolatility), maximise Sharpe (MaxSharpe), or minimise "
            "variance subject to a target-return equality (TargetReturn). "
            "All solved with SLSQP."
        ),
    },
    "constraint": {
        "Beginner": (
            "**Rules the portfolio must follow** — here: no shorting "
            "(every weight is zero or positive) and every dollar is "
            "invested (weights sum to 100%)."
        ),
        "Advanced": (
            "**Optimisation constraints** — budget equality "
            "`Σ wᵢ − 1 = 0` and box bounds `0 ≤ wᵢ ≤ 1` (long-only), plus an "
            "optional target-return equality `wᵀ μ − target = 0`."
        ),
    },
    "target_return": {
        "Beginner": (
            "**Your return goal** — a specific yearly return you want the "
            "portfolio to reach, with the smallest possible risk. Must be "
            "between the lowest and highest individual asset averages."
        ),
        "Advanced": (
            "**Target-return portfolio** — solves min `wᵀ Σ w` subject to "
            "`wᵀ μ = target` and budget/long-only constraints. Infeasible "
            "targets (outside `[μ_min, μ_max]`) return a failure row with "
            "NaN weights."
        ),
    },
    "investment_amount": {
        "Beginner": (
            "**How much you'd like to invest** — used to translate the "
            "portfolio's weights into actual dollars. "
            "*Example:* $10,000 × a 0.25 weight = $2,500 in that asset."
        ),
        "Advanced": (
            "**Investment amount** — a presentation-only scalar used to "
            "convert allocation weights to monetary amounts "
            "(`dollars_i = amount × wᵢ`). Does not affect optimisation."
        ),
    },
    "horizon": {
        "Beginner": (
            "**Investment horizon** — how long you plan to keep the money "
            "invested. Shorter horizons make volatile portfolios more "
            "painful if you need to sell during a dip."
        ),
        "Advanced": (
            "**Investment horizon** — a categorical context field (short / "
            "medium / long). Not an input to any calculation; used only to "
            "tailor explanation context."
        ),
    },
    "risk_tolerance": {
        "Beginner": (
            "**Risk tolerance** — your comfort with swings. Lower tolerance "
            "means looking harder at Min Volatility; higher tolerance can "
            "lean towards Max Sharpe."
        ),
        "Advanced": (
            "**Risk tolerance** — a categorical context field. Not an input "
            "to the optimiser; displayed as guidance alongside the results."
        ),
    },
}


def get_explanation(key: str, mode: str) -> str:
    """
    Return the explanation text for `key` in `mode`.

    Raises KeyError on unknown key so tests fail loudly. Unknown *mode* falls
    back to "Beginner" rather than raising — the mode layer already validates
    mode values, so this is defensive only.
    """
    if key not in EXPLANATIONS:
        raise KeyError(f"No explanation registered for {key!r}")
    if mode not in ("Beginner", "Advanced"):
        mode = "Beginner"
    return EXPLANATIONS[key][mode]


def list_explanation_keys() -> list[str]:
    """Return all keys with at least one non-empty mode entry."""
    return [k for k, v in EXPLANATIONS.items()
            if v.get("Beginner") and v.get("Advanced")]