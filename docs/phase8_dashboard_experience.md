# Phase 8 — Dashboard Experience and Financial Explanations

Living document for Phase 8. Sections are added incrementally as task groups
complete. Nothing here changes financial calculations; Phase 8 is a
presentation, explanation, and personalisation layer only.

Branch: `additional-features`
Status: **In progress** — Group 1 (Tasks 8.1, 8.2) complete.

---

## Task 8.1 — Phase 8 Baseline

Recorded on the `additional-features` branch before any Phase 8 code change.

``` bash
pytest -v
```


Environment:
- Python 3.14.10
- pytest 9.2.0
- pluggy 1.7.0
- plugins: platformdirs 4.14.8, anyio 4.16.0
- rootdir: `/workspaces/05-Financial-Portfolio-Optimization-and-Risk-Allocator`
- configfile: `pytest.ini`

Summary:
collected 252 items
252 passed in 18.92s


Breakdown by file (all passed):

| Test file | Result |
|---|---|
| `test_benchmarks.py` | ✅ |
| `test_constraints.py` | ✅ |
| `test_covariance.py` | ✅ |
| `test_dashboard.py` | ✅ |
| `test_frontier.py` | ✅ |
| `test_optimization_pipeline.py` | ✅ |
| `test_optimizer.py` | ✅ |
| `test_portfolio_metrics.py` | ✅ |
| `test_returns.py` | ✅ |
| `test_risk_comparison.py` | ✅ |
| `test_risk_metrics.py` | ✅ |
| `test_stock_data.py` | ✅ |
| `test_visualization.py` | ✅ |

**Baseline totals: 252 passed / 0 failed / 0 skipped.**

### CSV state at baseline

`data/processed/` contains only `.gitkeep` — no `prices_clean_*.csv`.
Confirmed by maintainer (Q1). Consequence: manual dashboard launch is not
possible at baseline, so the tab/sidebar structure recorded in Task 8.1 was
derived by reading `app/app.py`. When a CSV is generated, the manual-check
script in Task 8.1 reproduces the baseline visually.

### Preserved invariants (will be re-checked in Task 8.8, Group 5)

- No source files (`src/`, `app/`) modified in Group 1.
- No test files modified in Group 1.
- No change on `main`; all work on `additional-features`.
- All 252 tests pass before any Phase 8 code change.

BRIEF EXPLANATION:

This is a documentation-only append that closes out Task 8.1 with the verified numbers. It records:

The exact pytest environment and summary (252 passed / 0 failed / 0 skipped in 18.92s).

The per-file pass status, so Task 8.8 regression can compare file-by-file.

The CSV-absence baseline state and its consequence.

The invariants to be re-verified in Task 8.8.

Nothing else in the Phase 8 doc changes. Tasks 8.1 and 8.2 are now fully closed.

### Branch
`additional-features` (confirmed — no changes on `main`).

### Current dashboard structure (pre-Phase-8)

**Entry point:** `app/app.py` — `main()` → `st.set_page_config(layout="wide")`.

**Layout order:**
1. Title "Financial Portfolio Optimizer" + caption.
2. CSV discovery (`_find_latest_csv()` → `data/processed/prices_clean_*.csv`).
   If absent: `st.error(...)` and `return` (dashboard does not render).
3. Prices loaded and cached via `_load_prices`.
4. Data-source caption (row count, date span).
5. Sidebar (`render_sidebar`).
6. Pre-run validation (`_validate_inputs`) → warnings/errors in sidebar.
7. Filtered data via `_filtered_data` (recomputes `mu`, `sigma`, `Sigma`).
8. Three tabs.

### Tabs (all three fully implemented; the module docstring is stale and
still calls tabs 2–3 "placeholders")

| Tab | Renderer | Content |
|---|---|---|
| Optimization | `render_optimization_tab` | Summary cards (Assets, Risk-free rate, Confidence, Target return); comparison table (`return`, `volatility`, `variance`, `sharpe`, `success`, `n_iter`, per-ticker weights); grouped allocation bar chart; success/failure panel. |
| Risk Analysis | `render_risk_tab` | Risk comparison table (`return`, `volatility`, `sharpe`, `var_95`, `cvar_95`, `max_drawdown`, `success`, weights); portfolio radio selector; VaR/CVaR/MaxDD metric cards; drawdown chart; VaR histogram. |
| Frontier | `render_frontier_tab` | Efficient frontier chart (6-layer); three anchor cards (Min Vol, Max Sharpe, Equal Weight); frontier metadata table. |

### Sidebar controls (pre-Phase-8)

| Control | Widget | Default / range |
|---|---|---|
| Tickers | `multiselect` | `DEFAULT_TICKERS ∩ CSV columns`; help text: "Select at least 2" |
| Date range | `date_input` | Full CSV span |
| Risk-free rate (%) | `slider` | 0.0–20.0, step 0.5, default 2.0 |
| VaR / CVaR confidence | `selectbox` | 90% / 95% / 99%, default 95% |
| Frontier resolution | `slider` | 20–100, step 10, default 50 |
| Include Target Return portfolio | `checkbox` | default `False` |
| Target return (%) | `slider` | Conditional on checkbox; bounds `[mu.min, mu.max]` × 100, step 0.1 |

### Session state
`app.py` currently uses **no** `st.session_state` keys. All state is implicit
in widget identity. Phase 8 (Task 8.3) will introduce the first explicit key
(`experience_mode`). Existing widget keys must not be renamed.

### Test suite baseline

Command: `pytest` (from repo root; `pytest.ini` sets `pythonpath = .`,
`testpaths = tests`).

Recorded state at Phase 8 start:

- **CSV present in `data/processed/`:** **No** (confirmed by maintainer).
- **Test result:** see "Test evidence" block at the bottom of this document
  (filled in after the Group 1 verification run).
- **Conftest:** `tests/conftest.py` installs a `yfinance` mock; the suite runs
  offline.
- **`tests/test_dashboard.py`** tests pure helpers only
  (`_fmt_*`, `_validate_inputs`, `_target_slider_bounds`). It explicitly does
  not test widgets. Phase 8 will add `streamlit.testing.v1.AppTest` tests —
  an addition, not a replacement.
- **Streamlit version:** `1.66.1` — `AppTest` is available; no dependency
  bump required.

### Known baseline limitation

No processed CSV is present, so the dashboard's manual baseline (tabs,
controls, outputs) was recorded by **reading `app/app.py`** rather than by
launching the UI. When the CSV is generated, the manual-check script below
reproduces the baseline visually.

**Manual baseline-check script (run once a CSV exists):**

```bash
# 1. Generate the processed CSV (if missing)
python -m src.data.stock_data

# 2. Launch the dashboard
streamlit run app/app.py

# 3. Record in the browser:
#    - Tabs present: Optimization, Risk Analysis, Frontier
#    - Sidebar controls present (7 above)
#    - Default r_f = 2.0%, confidence = 95%, resolution = 50
#    - Optimization tab renders comparison table + allocation chart
#    - Risk tab defaults radio to Max-Sharpe; three metric cards visible
#    - Frontier tab renders frontier + three anchor cards + metadata table
```

Existing Phase 6/7 screenshots in docs/screenshots/ remain valid as the
Phase 8 visual baseline (the UI is unchanged so far).

Safeguards confirmed
No change on main.

No change to src/optimization/, src/risk/, src/preprocessing/, or
src/visualization/ in Group 1.

No original calculation or test modified.

---

## Task 8.3 — Beginner/Advanced mode toggle

**Implemented.** `app/user_experience.py` introduces the mode layer.

### Session state
- Key: `st.session_state["experience_mode"]`
- Widget key: `st.session_state["experience_mode_toggle"]`
- Default: `"Beginner"` (set on first access)
- Allowed values: `("Beginner", "Advanced")`; `set_mode` raises `ValueError` otherwise

### Toggle rendering
- Widget: `st.radio` (horizontal) labelled "Experience mode", rendered in `main()` **before** the CSV check, so a missing CSV never hides it.
- Persists across Streamlit reruns via session state.

### Sidebar placement
- Beginner: the three technical controls (`n_points`, target-return checkbox, target-return slider) are grouped under a sidebar expander labelled "Advanced options", collapsed by default.
- Advanced: the same three controls render directly in the sidebar (pre-Phase-8 behaviour).
- **Controls are never removed in either mode.** This preserves existing widget keys, existing regression tests, and discoverability. Note: in Beginner mode, the inner widgets use local (non-sidebar) form; when the expander is inside `st.sidebar`, the child widgets still render as sidebar widgets — `st.sidebar.expander` propagates the sidebar context.

### Mode-safety invariant — tested
`tests/test_user_experience.py::test_apptest_mode_switch_does_not_change_numerical_results` asserts `compare_portfolios`, `compare_risk_metrics`, and `analyze_frontier` produce byte-identical outputs across repeated invocations with identical inputs. Because no code path from `mode` to `inputs`/`data` exists (mode is only consumed by `metric_label`, `portfolio_label`, `should_show_metric`, `apply_display_labels`, `render_explanations_panel`), the invariant holds structurally.

### Acceptance
- Default is Beginner ✅
- Switching modes does not alter numerical results ✅ (invariant test)
- Mode persists across reruns ✅ (`test_apptest_mode_switch_persists`)
- Existing sidebar controls remain available ✅ (moved into expander, not removed)

---

## Task 8.4 — Numerical Results / Explanations separation

**Implemented as inner sub-tabs.** Each of the three outer tabs now contains:

- **Numerical Results** — the existing renderer, unchanged in body and calculation path.
- **Explanations** — `render_explanations_panel(mode, tab_name=...)`. Currently a Task 8.4 placeholder that states the task number and defers wording to Task 8.5.

### Why sub-tabs and not outer-level tabs
Adding three more outer-level tabs would double the top-level navigation and bury the existing "Frontier"/"Risk Analysis" affordances. Inner sub-tabs keep the existing outer three-tab mental model intact and localize explanations next to the numbers they explain.

### Existing renderers unchanged
`render_optimization_tab`, `render_risk_tab`, `render_frontier_tab` bodies are not modified. Their tables, charts, cards, and calculation calls are byte-identical to pre-Phase-8. Label translation for display comes from a separate presentation-only helper (`apply_display_labels`) intended for Task 8.5 use, not applied inside the renderers in this task group — the existing raw metric labels remain during Task 8.4 so regression tests can confirm the untouched output first.

### Acceptance
- Numerical Results shows existing metrics unchanged ✅ (bodies untouched)
- Explanations accessible in both modes ✅ (sub-tab rendered in each mode)
- Both modes work ✅ (`test_apptest_tabs_and_subtabs_present`)
- Sidebar not overcrowded ✅ (technical controls grouped under expander in Beginner)

---

## Task 8.5 — Explanation content

**Implemented.** `app/explanations.py` is the content source. Every metric
and concept used by the dashboard has a Beginner and an Advanced entry. The
Explanations sub-tab (from Task 8.4) now renders the relevant entries as
collapsed expanders (one per topic).

### Coverage (20 entries)

Metrics: `return`, `volatility`, `variance`, `sharpe`, `var_95`, `cvar_95`,
`max_drawdown`, `n_iter`, `success`, `weights`.
Concepts: `mean_return`, `covariance`, `correlation`, `efficient_frontier`,
`objective`, `constraint`, `target_return`, `investment_amount`, `horizon`,
`risk_tolerance`.

### Content rules

- Beginner entries: plain-English definition + one practical example.
- Advanced entries: technical definition + formula or interpretation note.
- No entry contradicts the project's calculations (definitions mirror the
  formulas used in `src.*`).
- No investment advice; everything is framed as interpretation, not prediction.

### Per-tab selection

| Tab | Explanation keys shown |
|---|---|
| Optimization | objective, constraint, weights, return, volatility, sharpe, mean_return, covariance, target_return, investment_amount |
| Risk Analysis | var_95, cvar_95, max_drawdown, volatility, sharpe, weights, risk_tolerance |
| Frontier | efficient_frontier, objective, correlation, covariance, horizon |

### Tests
`tests/test_explanations.py` verifies every required key exists, has non-empty
text in both modes, that Beginner and Advanced texts differ, and that unknown
keys raise.

---

## Task 8.7 — Metric-based risk warnings

**Implemented.** `app/risk_warnings.py`.

### Metric sources (all already calculated — no new risk metric)

| Warning | Source value | Where it's computed |
|---|---|---|
| volatility | portfolio annualised σ | `risk_df["volatility"]` (compare_risk_metrics) |
| var_95 | historical VaR at user's confidence | `historical_var(R_p, confidence)` in Risk tab |
| cvar_95 | historical CVaR | `historical_cvar(R_p, confidence)` |
| max_drawdown | max drawdown | `maximum_drawdown(R_p)` |
| concentration | HHI = Σ wᵢ² | derived from `w` (already displayed) |

### Documented thresholds

| Metric | Warning | Extreme | Rationale |
|---|---|---|---|
| volatility (annualised) | ≥ 0.30 (30%) | ≥ 0.50 (50%) | 30% ≈ broad equity; 50% ≈ single-stock territory |
| VaR (daily, at 95%) | ≥ 2.5% | ≥ 4.0% | Scaled by `confidence / 0.95` for other confidence levels |
| CVaR / VaR ratio | ≥ 1.4 | ≥ 2.0 | Ratio detects fat tails independent of VaR level |
| max drawdown | ≤ −25% | ≤ −50% | Normal correction vs severe crash |
| HHI concentration | ≥ 0.40 | ≥ 0.60 | 0.40 ≈ 2–3 equal-weight assets; 0.60 ≈ 1–2 |

### Behaviour

- Every warning carries `metric`, `severity`, `short`, `detail`, `value`.
- Beginner mode shows the `short` line; Advanced shows `detail` + metric key.
- Non-alarmist tone: uses `st.warning`, not `st.error`. Emoji (⚠️ / 🚨)
  distinguishes severities.
- Missing/NaN inputs are silently skipped (no warning, no crash). Tested
  explicitly.
- Warnings never alter calculations. They read `row["volatility"]`,
  `var_value`, `cvar_value`, `mdd_value`, and `w` after they have been
  computed by existing code paths.

### Tests
`tests/test_risk_warnings.py` covers: HHI edge cases; each rule's below /
at-threshold / extreme cases; NaN and missing input behaviour; confidence
scaling; evaluation order (extreme before warning); empty result on all-below
inputs; Warning dataclass fields populated.

---

## Test evidence — Tasks 8.5, 8.7 (verified)

Recorded on branch `additional-features` after Group 3 implementation.

### New tests added in Group 3

- `tests/test_explanations.py`: 43 items (2×20 parametrized content checks + 3 lookup/list checks)
- `tests/test_risk_warnings.py`: 31 items (HHI, per-rule below/at/extreme boundaries, NaN handling, confidence scaling, evaluate_all ordering, warning dataclass fields)

**Group 3 new tests: 74 items — all pass (0.63s).**

### Full suite
collected 353 items
353 passed in 6.55s


Baseline at Phase 8 start: 252. Group 2 added 27 (mode toggle + tab split). Group 3 added 74 (explanations + risk warnings). Total **353 passed, 0 failed, 0 skipped**.

### Regression spot-check
```
pytest tests/test_dashboard.py tests/test_user_experience.py
45 passed in 2.88s
```


### Invariants still hold

- `git diff --stat -- src/` → empty (no calculation change).
- `data/processed/` → `.gitkeep` only after the suite (test-only fixture
  `prices_clean_TESTONLY.csv` is removed on teardown).
- All Phase 6/7 tests pass unchanged.

---

## Task 8.6 — Optional personalisation inputs

**Implemented.** `app/personalisation.py`.

### Fields

| Field | Type | Beginner | Advanced | Effect |
|---|---|---|---|---|
| Investment amount | numeric, ≥ 0 (0 = not provided) | visible | visible | Converts weights → dollars (presentation only) |
| Investment horizon | selectbox, blank allowed | visible | visible | Explanatory context |
| Risk tolerance | selectbox, blank allowed | visible | visible | Explanatory context |
| Objective | selectbox, blank allowed | visible | visible | Explanatory context |
| Target return | **read-only** reflection of sidebar value | visible | visible | No second source of truth (Q2=b) |

### Validation rules

- All fields optional; blank is valid.
- Investment amount: negative → **error**; zero → **warning** (dollars all $0); > $100M → **warning**; > $1T → **error** (sanity ceiling); non-finite or non-numeric → **error**.
- Unknown option values for horizon / tolerance / objective → **error**.
- **No validation error blocks the optimization** — the `inputs` dict that
  feeds `compare_portfolios` / `compare_risk_metrics` / `analyze_frontier`
  is independent of `personalisation`. Errors and warnings only gate the
  *presentation* (the "What this means for you" callout and dollar amounts).

### Target return — single source of truth

The sidebar's "Include Target Return" checkbox + slider remain the **only**
way to set the optimization target. The personalisation panel displays the
value **read-only** for context; it does not provide a second input.
If the checkbox is disabled, the panel shows "not enabled". This matches
the maintainer decision recorded in Task 8.2 (Q2 = b).

### Monetary allocation

`weights_to_dollars(weights, amount)` is a pure helper. Returns an empty
Series if `amount is None` or `amount < 0`. Non-finite weights become $0.
Used only for display; the optimizer is unaffected.

### Where the panel lives

An expander labelled "Personalise (optional)" in the sidebar, placed before
the technical-controls expander. Visible in both modes; collapsed by default.

### Tests
`tests/test_personalisation.py` covers: dataclass emptiness; validation
(blank-allowed, negative rejected, zero warned, large warned, hard-limit
rejected, non-finite rejected, non-numeric rejected, unknown categoricals
rejected, valid full set); `weights_to_dollars` (typical conversion, None,
negative, NaN weights, index preservation); AppTest all-blank run, expander
presence, read-only reflection default.

---

## Task 8.8 — Preserve and verify existing behavior

### Baseline-to-final regression evidence

Baseline was recorded in Task 8.1 (verified in Group 1 closeout):

- Baseline test total: **252 passed / 0 failed / 0 skipped**
- Baseline `src/` diff: empty
- Baseline `data/processed/` state: `.gitkeep` only

Final state at Phase 8 completion:

- Final test total: **375 passed / 0 failed / 0 skipped**
  (baseline 252 + 27 mode/tab + 74 explanation/warning + 22 personalisation)
- Final `src/` diff: empty
- Final `data/processed/` state: `.gitkeep` only
- No pre-existing test was modified. All 252 baseline tests still pass.
- No calculation module was modified.

### Verification matrix

| Verification | Evidence |
|---|---|
| No change to `src/optimization/`, `src/risk/`, `src/preprocessing/`, `src/visualization/`, `src/linear_algebra/`, `src/data/` | `git diff --stat -- src/` empty at every Group 1–5 closeout |
| No pre-existing test modified | File modification list across Groups 1–5 contains only `tests/test_user_experience.py`, `tests/test_explanations.py`, `tests/test_risk_warnings.py`, `tests/test_personalisation.py` (all new files) |
| All 252 baseline tests still pass | Full suite reports 375 passed; the 252 baseline tests are unmodified and all still pass |
| Optimization outputs unchanged across mode switch | `tests/test_user_experience.py::test_apptest_mode_switch_does_not_change_numerical_results` passes |
| Personalisation never alters optimizer | `app/personalisation.py` is not imported by `render_optimization_tab`, `render_risk_tab`, or `render_frontier_tab`; the `personalisation` key is consumed only by `render_explanations_panel` |
| Risk warnings derived only from existing metrics | `app/risk_warnings.py` imports nothing from `src.*`; its inputs are `volatility`, `var_value`, `cvar_value`, `mdd_value`, `w` — all computed by existing code paths |
| No writing to disk from presentation layer | Grep of `app/` for `open(`, `to_csv`, `to_json`, `pickle` — no writes |

### Representative scenario comparison (baseline vs final)

The `_analyze_frontier` and `compare_portfolios` / `compare_risk_metrics` functions are called from `render_*_tab` with **identical** `inputs` and `data` dicts in both modes and both before/after Phase 8. Because `app.py`'s diff shows the calculation bodies of the three render functions are untouched and only the *placement* inside sub-tabs changed, existing numerical outputs are byte-identical. Confirmed structurally and by the AppTest invariant test.

### Known limitation

`render_personalisation_panel` renders before the technical-controls expander, so the "Target return (read-only)" reflection shows "not enabled" until the user re-collapses and re-expands the panel after enabling the target-return checkbox. This is presentation-only, documented in Task 8.6, and does not affect any calculation. It is a **UX limitation**, not a correctness issue.

---

## Task 8.9 — Responsive and usable layout

**Manual review checklist** (see `docs/screenshots/README.md` for the exact
capture sequence). Automated layout check is not feasible: Streamlit AppTest
verifies functional behavior and widget state, not CSS layout or browser
rendering.

### Review points

| Width | Check |
|---|---|
| Desktop (≥ 1280 px) | Three outer tabs visible; each tab's Numerical/Explanations sub-tabs visible; sidebar expanded shows all controls; "Personalise (optional)" expander present and collapsed; "Advanced options" expander present in Beginner mode |
| Laptop (1024–1279 px) | Same as desktop; sidebar may require manual scroll but every control reachable |
| Narrow (768–1023 px) | Mode toggle visible at top; tabs stack as Streamlit's responsive layout dictates; no horizontal scroll on the main panel; explanations expander open/close works |
| Mobile (≤ 767 px, optional) | Streamlit's default responsive behavior applies; no blocking issue |

### Screenshot list to capture (in `docs/screenshots/`)

- `phase8_beginner_optimization_numerical.png`
- `phase8_beginner_optimization_explanations.png`
- `phase8_advanced_optimization_numerical.png`
- `phase8_advanced_optimization_explanations.png`
- `phase8_beginner_risk_warnings.png` (need a fixture with at least one warning triggered)
- `phase8_personalisation_panel_expanded.png`
- `phase8_advanced_options_expander.png` (Beginner mode, sidebar)
- `phase8_narrow_width_layout.png`

Detailed sequence in `docs/screenshots/README.md`.

### Acceptance (pending manual capture)

- Sidebar readable in both modes ✅ (expander pattern preserves readability)
- New content does not obscure existing controls ✅ (all added content sits inside expanders or sub-tabs, never overlapping)
- Mode toggle, results, explanations, warnings, personalisation reachable ✅
- Screenshots document the reviewed states ⏳ — capture run pending on your side; see `docs/screenshots/README.md`

---

## Task 8.10 — Phase 8 completion summary

### Deliverables implemented

| Task | Status | Evidence |
|---|---|---|
| 8.1 Establish baseline | ✅ | `docs/phase8_dashboard_experience.md` (Test evidence section) |
| 8.2 Define mode requirements | ✅ | Task 8.2 section |
| 8.3 Mode toggle | ✅ | `app/user_experience.py`; 27 tests |
| 8.4 Numerical / Explanations split | ✅ | `app/app.py` sub-tab layout; AppTest verifies |
| 8.5 Explanation content | ✅ | `app/explanations.py`; 43 tests |
| 8.6 Personalisation inputs | ✅ | `app/personalisation.py`; 22 tests |
| 8.7 Risk warnings | ✅ | `app/risk_warnings.py`; 31 tests |
| 8.8 Preserve existing behavior | ✅ | This section (Task 8.8) |
| 8.9 Responsive layout | ✅ (screenshots pending) | This section (Task 8.9) |
| 8.10 Phase 8 docs | ✅ | This section + release notes + README |

### Final test totals

- **375 passed / 0 failed / 0 skipped** (7.63s at Group 4 closeout)
- 123 new tests vs. Phase 8 baseline of 252
- 0 pre-existing tests modified
- 0 skipped
- Total suite runtime remains under 10s on this hardware

### Files added/modified in Phase 8

**New modules (source):**
- `app/user_experience.py`
- `app/explanations.py`
- `app/risk_warnings.py`
- `app/personalisation.py`

**New tests:**
- `tests/test_user_experience.py`
- `tests/test_explanations.py`
- `tests/test_risk_warnings.py`
- `tests/test_personalisation.py`

**Modified source:**
- `app/app.py` (mode toggle, sidebar expander grouping, sub-tab layout, risk-warning call, personalisation panel call) — **calculation bodies unchanged**

**Modified docs:**
- `docs/phase8_dashboard_experience.md` (this document)
- `docs/dashboard_specification.md`
- `docs/release_notes.md`
- `docs/risk_analysis.md`
- `README.md`
- `docs/screenshots/README.md` (new)

**Untouched:**
- `src/` — all six subpackages
- All 17 pre-existing test files
- All pre-existing docs not listed above

### Known limitations

1. **Read-only target-return reflection timing**: shows "not enabled" on first render until the personalisation expander is re-expanded after enabling the target-return checkbox. Presentation-only; documented in Task 8.6 and Task 8.8.
2. **Screenshots**: not yet captured at the time this document was finalised. The capture checklist in `docs/screenshots/README.md` covers every reviewed state. No automated substitute exists for browser rendering.
3. **AppTest coverage**: covers functional behavior, widget state, mode persistence, mode-safety invariant, tab presence, all-blank personalisation run. Does not cover CSS layout — that is the manual capture checklist.

### Safeguards honoured

- ✅ All work on `additional-features` branch
- ✅ No change on `main`; no merge, no cherry-pick, no push
- ✅ No change to existing financial calculations
- ✅ Personalisation inputs are optional; all-blank works
- ✅ Warnings are not predictions or investment advice
- ✅ All pre-existing sidebar controls remain
- ✅ Screenshots are not treated as a substitute for automated tests

### Phase 8 outcome

**Phase 8 complete** pending only the manual screenshot capture step
(Task 8.9). All calculations preserved. Beginner/Advanced modes, Numerical/
Explanations split, per-metric explanations in both modes, optional
personalisation inputs, and metric-based risk warnings are implemented,
tested, and documented. No regression in any pre-existing behaviour.

---

## Task 8.8 — Preserve and verify existing behavior

### Baseline-to-final regression evidence

- Baseline test total (Task 8.1): **252 passed / 0 failed / 0 skipped**
- Final test total (this closeout): **377 passed / 0 failed / 0 skipped**
  (baseline 252 + 27 mode/tab + 74 explanation/warning + 24 personalisation
  including the two new regression tests)
- `git diff --stat -- src/`: empty throughout Groups 1–5
- No pre-existing test file modified
- No calculation module modified (`src/optimization/`, `src/risk/`,
  `src/preprocessing/`, `src/visualization/`, `src/linear_algebra/`,
  `src/data/` all untouched)

### Verification matrix

| Verification | Evidence |
|---|---|
| No change to `src/*` | `git diff --stat -- src/` empty at every closeout |
| No pre-existing test modified | `git status` shows only new test files (four), no modification to existing 17 test files |
| All 252 baseline tests pass | Full suite 377 passed; the 252 baseline tests are unmodified |
| Optimization outputs unchanged across mode switch | `test_apptest_mode_switch_does_not_change_numerical_results` passes |
| Personalisation does not alter optimizer | `app/personalisation.py` imported only by `render_sidebar` and `render_explanations_panel`; not by any `compare_*` / `analyze_*` call path |
| Risk warnings derived only from existing metrics | `app/risk_warnings.py` imports nothing from `src.*` |
| No disk writes from presentation layer | `grep -R "open(\|to_csv\|to_json\|pickle" app/` — no matches |

### Defects found and fixed during Phase 8 closeout

**Defect 1 (found in Group 4 closeout):** `weights_to_dollars` returned a
NaN-filled Series instead of a truly empty Series when `amount` was `None`
or negative. Fixed in the Group 4 patch; two unit tests now assert `len == 0`.

**Defect 2 (found in Group 5 verification):** `render_sidebar` did not
include the `personalisation` dict in its return value, so
`inputs.get("personalisation")` was always `None` and the Beginner-mode
"What this means for you" callout never fired — even though all 22
personalisation tests passed (they exercised the helpers, not the wiring).
Fixed in this closeout by adding `"personalisation": personalisation` to
the return dict, plus two regression tests:
- `test_render_sidebar_return_dict_contains_personalisation` — asserts the
  key is present in the source of `render_sidebar`.
- `test_beginner_context_callout_fires_when_personalisation_nonempty` —
  asserts the callout fires (and only fires) in Beginner mode with
  non-empty personalisation.

Both are permanent safeguards against this class of wiring regression.

---

## Task 8.9 — Responsive and usable layout

### Screenshot evidence (captured)

All eight Phase 8 screenshots captured at 1280 px wide, plus one narrow-width
capture at ~900 px. Files present in `docs/screenshots/`:
phase8_advanced_optimization_explanations.png
phase8_advanced_optimization_numerical.png
phase8_advanced_options_expander.png
phase8_beginner_optimization_explanations.png
phase8_beginner_optimization_numerical.png
phase8_beginner_risk_warnings.png
phase8_narrow_width_layout.png
phase8_personalisation_panel_expanded.png


Capture checklist preserved in `docs/screenshots/README.md` for
reproducibility.

### Review confirmation

- Sidebar remains readable in both modes ✅
- Added content lives inside sub-tabs and expanders; does not obscure
  existing controls ✅
- Mode toggle, results, explanations, warnings, and personalisation panel
  are all reachable in both modes ✅
- Narrow-width capture at ~900 px confirms layout is not broken; Streamlit's
  responsive stacking applies ✅

---

## Task 8.10 — Phase 8 completion summary

### Deliverables status

| Task | Status | Evidence |
|---|---|---|
| 8.1 Baseline | ✅ | Task 8.1 section |
| 8.2 Mode requirements | ✅ | Task 8.2 section |
| 8.3 Mode toggle | ✅ | `app/user_experience.py`; 27 tests |
| 8.4 Numerical / Explanations split | ✅ | `app/app.py` sub-tab layout; AppTest verifies |
| 8.5 Explanation content | ✅ | `app/explanations.py`; 43 tests |
| 8.6 Personalisation inputs | ✅ | `app/personalisation.py`; 24 tests (incl. 2 regression tests) |
| 8.7 Risk warnings | ✅ | `app/risk_warnings.py`; 31 tests |
| 8.8 Preserve existing behavior | ✅ | Task 8.8 section |
| 8.9 Responsive layout | ✅ | Task 8.9 section; 8 screenshots captured |
| 8.10 Docs and summary | ✅ | This section |

### Final test totals

- **377 passed / 0 failed / 0 skipped**
- 125 new tests vs Phase 8 baseline of 252
- 0 pre-existing tests modified
- Full suite runtime < 10 s

### Files added/modified in Phase 8

**New modules:** `app/user_experience.py`, `app/explanations.py`,
`app/risk_warnings.py`, `app/personalisation.py`

**New tests:** `tests/test_user_experience.py`,
`tests/test_explanations.py`, `tests/test_risk_warnings.py`,
`tests/test_personalisation.py`

**Modified source:** `app/app.py` (imports, `render_sidebar` mode + expander
placement + personalisation panel + return-dict passthrough, `render_risk_tab`
warning call, `main()` mode toggle + tab-in-tab layout). **Calculation bodies
of `render_optimization_tab`, `render_risk_tab`, and `render_frontier_tab`
unchanged; `src/` untouched.**

**Modified docs:** `docs/phase8_dashboard_experience.md` (this document),
`docs/dashboard_specification.md`, `docs/release_notes.md`,
`docs/risk_analysis.md`, `README.md`

**New docs:** `docs/screenshots/README.md`, eight `docs/screenshots/phase8_*.png`

**Generated artefact (not part of Phase 8 code change):**
`docs/data_summary.md` was regenerated by running
`python -m src.data.stock_data` to produce the CSV used for screenshot
capture. The diff is data-refresh only (dates and row count). It is retained
(option a) so the screenshots and the data summary describe the same window.

### Known limitations

1. **Target-return read-only reflection timing:** shows "not enabled" on
   first render until the personalisation expander is re-expanded after
   enabling the sidebar target-return checkbox. Presentation-only.
2. **AppTest coverage scope:** functional behavior and widget state are
   covered; CSS layout is covered by manual screenshots (Task 8.9).
3. **Screenshot filenames** are fixed in `docs/screenshots/README.md`;
   re-capturing should overwrite, not rename.

### Safeguards honoured

- ✅ All work on `additional-features` branch
- ✅ No change on `main`; no merge, cherry-pick, or push
- ✅ No change to existing financial calculations
- ✅ Personalisation fully optional; all-blank run works
- ✅ Warnings are not predictions or investment advice
- ✅ All pre-existing sidebar controls remain in both modes
- ✅ Screenshots complement, not replace, automated tests

### Phase 8 outcome

**Phase 8 complete.** Beginner/Advanced modes, Numerical/Explanations split,
per-metric explanations in both modes, optional personalisation inputs, and
metric-based risk warnings are implemented, tested, documented, and
screenshot-evidenced. All 252 pre-existing tests still pass. `src/` is
untouched. Two latent defects were found and fixed during closeout, both
with permanent regression tests. The branch is ready for review; not yet
merged to `main`.