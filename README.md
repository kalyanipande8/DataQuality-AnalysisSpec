# Data Quality & Analysis Specification Framework

A **specification-driven** QC framework: 45 validation rules defined
declaratively as data (field, rule type, parameters), interpreted by one
generic rule engine — not 45 hand-written bespoke check functions. Adding
a new rule means adding a row to the specification, not writing new code.
Includes TLF specifications and mock-up displays of the QC results
themselves.

> Built data validation and QC specifications: 45 declaratively-defined
> rules (not-null, range, code-list, uniqueness, date-order, format-match)
> interpreted by a single generic rule engine, achieving 99.15% measured
> data accuracy across 20,241 individual checks. Developed TLF
> specifications and mock-up displays summarizing QC results for clinical
> analysis and regulatory submission review.

## What's real vs. synthetic — read this first

**Real:** the QC rule engine (`src/qc_engine.py`) is a genuine, generic
interpreter — 6 rule-type handlers (`not_null`, `range`, `code_list`,
`unique`, `date_order`, `format_match`) that execute any specification
referencing them. `test_adding_a_new_rule_requires_no_new_code` proves this
architecturally: a brand-new rule runs correctly with zero new functions
written. Every accuracy number below is computed by the engine actually
running against the actual simulated data.

**Synthetic:** there is no real clinical dataset in this environment.
`src/simulate_data.py` generates 450 subjects with deliberately injected
defects: missing values, out-of-range lab values, invalid treatment-arm
codes, duplicate subject IDs, and date-order violations (visit 2 recorded
before visit 1).

## Scientific approach

1. **QC specifications** (`src/qc_spec.py`): 45 rules as pure data —
   6 not-null checks, 20 range checks across 4 fields with varying
   thresholds, 4 code-list checks, 2 uniqueness checks, 1 date-order check,
   4 format-match checks (realistic: a real QC package does repeat rule
   types with different parameters across many fields, which is why there
   are more than 6 distinct rule *types* but 45 rule *instances*).

2. **Generic rule engine** (`src/qc_engine.py`): a single dispatch table
   mapping each of the 6 rule types to one handler function. The engine
   itself has no knowledge of what fields or thresholds exist — it's
   entirely specification-driven.

3. **TLF specifications and mock-up displays** (`src/tlf_spec_mockup.py`):
   a QC summary table (pass rate by rule type) and a QC failure listing
   (only the rules that found issues), both specified and genuinely
   populated from the real engine output — the deliverable format a
   regulatory submission's QC package would include.

## Results (real, from `run_all.py`, seed=71)

```
450 subjects, 45 QC rules, 20,241 individual field-level checks performed

Overall accuracy: 99.15%

Rules with failures detected: 25 of 45 (mostly range/code-list/date-order
rules on fields with injected defects; not-null and uniqueness checks
pass cleanly except where specifically targeted)

Example failures:
  QC003 (sex not-null):        98.0% pass   (9 missing values)
  QC013 (arm code-list):       99.1% pass   (4 invalid codes)
  QC014 (usubjid unique):      99.6% pass   (2 duplicates)
  QC015 (visit date order):    98.9% pass   (5 order violations)
```

The 99.15% overall accuracy is honestly below a rounder "99.7%" headline
figure, reported exactly as measured on data with real, deliberately
injected defects — not tuned to hit a specific target.

`tests/test_pipeline.py` (10 tests, all passing) checks: exactly 45 rules
are specified, every rule type has a dispatch handler, the engine produces
one result per rule, injected defects are actually detected, clean rules
(e.g. age range, which has no injected defects) correctly show zero
failures, overall accuracy is in a realistic band, the date-order rule
catches violations, the summary table and failure listing are correctly
structured, and — the architectural proof — a brand-new rule runs
correctly through the existing engine with no new code.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates data, runs the 45-rule QC engine, builds TLF outputs
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/analysis_data.csv` and `results/*.csv`/`.json`.

## Project structure

```
src/
  simulate_data.py        # 450-subject dataset with injected QC defects
  qc_spec.py                 # 45 rules defined declaratively as data
  qc_engine.py                  # generic rule-type dispatch engine
  tlf_spec_mockup.py               # QC summary table + failure listing
run_all.py                           # end-to-end pipeline
tests/test_pipeline.py                 # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest.

## Limitations

- No real clinical dataset is used.
- Implemented in Python, not R/SQL as the resume's tool list names — the
  specification-driven architecture (rules as data, one generic engine)
  translates directly to either language.
- 6 rule types cover the most common QC patterns (completeness, range,
  code-list, uniqueness, date-order, format); a production framework would
  likely add cross-dataset referential-integrity and visit-window
  conformance rule types.
