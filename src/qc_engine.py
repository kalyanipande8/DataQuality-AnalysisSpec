"""A generic QC rule engine: interprets every rule_type in qc_spec.py
against the actual dataframe. Adding a new check means adding a row to
QC_SPECIFICATIONS, not writing a new function -- this is the real,
demonstrated architectural benefit of a specification-driven QC framework
over hand-written per-check code.
"""
from __future__ import annotations

import re

import pandas as pd

from .qc_spec import QC_SPECIFICATIONS


def _run_not_null(df: pd.DataFrame, field: str, params: dict) -> tuple[int, int]:
    n_fail = int(df[field].isna().sum())
    return len(df), n_fail


def _run_range(df: pd.DataFrame, field: str, params: dict) -> tuple[int, int]:
    non_null = df[field].dropna()
    fail = ((non_null < params["min"]) | (non_null > params["max"])).sum()
    return len(non_null), int(fail)


def _run_code_list(df: pd.DataFrame, field: str, params: dict) -> tuple[int, int]:
    non_null = df[field].dropna()
    fail = (~non_null.isin(params["allowed"])).sum()
    return len(non_null), int(fail)


def _run_unique(df: pd.DataFrame, field: str, params: dict) -> tuple[int, int]:
    non_null = df[field].dropna()
    fail = int(non_null.duplicated().sum())
    return len(non_null), fail


def _run_date_order(df: pd.DataFrame, field: str, params: dict) -> tuple[int, int]:
    earlier, later = params["earlier"], params["later"]
    valid = df.dropna(subset=[earlier, later])
    fail = (valid[earlier] > valid[later]).sum()
    return len(valid), int(fail)


def _run_format_match(df: pd.DataFrame, field: str, params: dict) -> tuple[int, int]:
    non_null = df[field].dropna().astype(str)
    pattern = re.compile(params["pattern"])
    fail = (~non_null.apply(lambda v: bool(pattern.search(v)))).sum()
    return len(non_null), int(fail)


RULE_DISPATCH = {
    "not_null": _run_not_null,
    "range": _run_range,
    "code_list": _run_code_list,
    "unique": _run_unique,
    "date_order": _run_date_order,
    "format_match": _run_format_match,
}


def run_qc_specifications(df: pd.DataFrame, specs: list[dict] = QC_SPECIFICATIONS) -> list[dict]:
    results = []
    for spec in specs:
        handler = RULE_DISPATCH[spec["rule_type"]]
        n_checked, n_fail = handler(df, spec["field"], spec["params"])
        pass_rate = round(100 * (1 - n_fail / n_checked), 3) if n_checked else 100.0
        results.append({
            "rule_id": spec["rule_id"], "field": spec["field"], "rule_type": spec["rule_type"],
            "n_checked": n_checked, "n_fail": n_fail, "pass_rate_pct": pass_rate,
        })
    return results


def overall_accuracy(results: list[dict]) -> dict:
    total_checked = sum(r["n_checked"] for r in results)
    total_fail = sum(r["n_fail"] for r in results)
    return {
        "n_rules": len(results),
        "total_checks_performed": total_checked,
        "total_failures": total_fail,
        "overall_accuracy_pct": round(100 * (1 - total_fail / total_checked), 4),
    }


if __name__ == "__main__":
    from .simulate_data import simulate

    df = simulate()
    results = run_qc_specifications(df)
    for r in results:
        if r["n_fail"] > 0:
            print(r)
    print(overall_accuracy(results))
