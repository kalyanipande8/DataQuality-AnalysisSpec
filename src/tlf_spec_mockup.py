"""TLF specification and mock-up display for the QC results themselves --
a QC summary table (by rule type) and a QC failure listing, both specified
and then genuinely populated from the real QC engine output, enabling
clinical analysis and regulatory submission review of data quality."""
from __future__ import annotations

import pandas as pd

TLF_SPECS = [
    {"output_id": "QC-SUM-01", "title": "QC Rule Pass Rate Summary by Rule Type", "type": "Table",
     "method": "Mean pass rate, grouped by rule_type"},
    {"output_id": "QC-LIST-01", "title": "QC Rules with Failures Detected", "type": "Listing",
     "method": "Filtered listing, rules where n_fail > 0"},
]


def build_qc_summary_table(qc_results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(qc_results)
    return (
        df.groupby("rule_type")
        .agg(n_rules=("rule_id", "count"), total_checked=("n_checked", "sum"),
             total_fail=("n_fail", "sum"), mean_pass_rate_pct=("pass_rate_pct", "mean"))
        .round(2).reset_index()
    )


def build_qc_failure_listing(qc_results: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(qc_results)
    return df[df["n_fail"] > 0].sort_values("n_fail", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    from .simulate_data import simulate
    from .qc_engine import run_qc_specifications

    df = simulate()
    results = run_qc_specifications(df)
    print(build_qc_summary_table(results))
    print(build_qc_failure_listing(results))
