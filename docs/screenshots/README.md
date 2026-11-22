# Phase 8 — Manual screenshot capture checklist

Automated tests cover functional behaviour. Screenshots are captured manually
because Streamlit AppTest does not render CSS layout. These are the states to
capture to complete Task 8.9.

## Prerequisites

```bash
# Generate a processed CSV once
python -m src.data.stock_data
```

If for any reason you cannot generate live data, a local fixture is acceptable
— use the same three assets so the shots are reproducible.

Launch
``` bash
streamlit run app/app.py
```

Open http://localhost:8501.

Capture sequence
Save each to docs/screenshots/<filename>.png from a 1280 px wide browser.

#	Filename	State to capture
1	phase8_beginner_optimization_numerical.png	Mode = Beginner; Optimization tab; Numerical Results sub-tab; "Advanced options" expander collapsed in sidebar; "Personalise (optional)" expander collapsed
2	phase8_beginner_optimization_explanations.png	Same state; switch to the Explanations sub-tab within Optimization
3	phase8_advanced_optimization_numerical.png	Mode = Advanced; Optimization tab; Numerical Results sub-tab; sidebar shows technical controls unwrapped (no "Advanced options" expander)
4	phase8_advanced_optimization_explanations.png	Same state; Explanations sub-tab
5	phase8_beginner_risk_warnings.png	Mode = Beginner; Risk Analysis tab; Num Results; ensure at least one warning is visible. Choose a small ticker set with high historical volatility, or set n_points low and select two correlated tickers. If no warnings fire naturally, pick the "Max Sharpe" portfolio for a concentrated portfolio — this usually triggers concentration warnings.
6	phase8_personalisation_panel_expanded.png	Sidebar; "Personalise (optional)" expander expanded; enter an investment amount of 10000; leave other fields blank
7	phase8_advanced_options_expander.png	Mode = Beginner; sidebar; "Advanced options" expander expanded showing n_points, Include Target Return, Target return slider
8	phase8_narrow_width_layout.png	Resize the browser window to ~900 px wide; capture the top of the page showing the mode toggle and at least one tab's sub-tabs
Known UX limitation to note in capture #6
After entering an amount and toggling Include Target Return via "Advanced
options", collapse-and-re-expand "Personalise (optional)" so the read-only
target-return line refreshes. This is documented in the Phase 8 completion
summary as a presentation-only limitation.

Confirmations
After capture, run:
``` bash
ls docs/screenshots/phase8_*.png
```

Expect eight files. Then update docs/phase8_dashboard_experience.md
Task 8.9 acceptance line from "⏳ pending" to "✅ captured" and record the
list of captured files.

BRIEF EXPLANATION:

- **Tasks 8.8, 8.9, 8.10 are documentation-only in this group.** All the underlying code, tests, and behaviour were delivered in Groups 1–4. Group 5 records the final evidence, the regression matrix, the layout review checklist, the known limitations, and the manual screenshot sequence.
- **Task 8.8 regression evidence** shows: baseline 252 → final 375, zero source changes, zero pre-existing tests modified, calculation bodies of the three render functions untouched across the diff, and the mode-safety invariant test passing.
- **Task 8.9** honestly separates *automated* (AppTest — functional behaviour) from *manual* (browser layout — cannot be automated) verification. The capture checklist is in a new file `docs/screenshots/README.md` because I cannot take browser screenshots myself. The acceptance criterion "screenshots document the reviewed states" is marked ⏳ pending until you run the checklist.
- **Task 8.10** is the completion summary. It states every deliverable, the final test totals, the files added/modified, the known limitations (including the read-only target-reflection timing limitation carried from Task 8.6), and the safeguards honoured.
- **`docs/release_notes.md`** gets a "Phase 8 — complete" entry above the preserved "Phase 8 — started" entry, so history is visible.
- **`README.md`** gets a short Phase 8 additions section that points to the full document.
- **`docs/dashboard_specification.md`** gets a cross-reference so the spec remains navigable after Phase 8.
- **No source, no tests, no `src/` change in this group.** `git diff --stat -- src/` must remain empty.