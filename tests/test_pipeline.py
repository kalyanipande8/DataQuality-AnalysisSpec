import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_data import simulate
from src.qc_spec import QC_SPECIFICATIONS
from src.qc_engine import run_qc_specifications, overall_accuracy, RULE_DISPATCH
from src.tlf_spec_mockup import build_qc_summary_table, build_qc_failure_listing


@pytest.fixture(scope="module")
def df():
    return simulate()


@pytest.fixture(scope="module")
def results(df):
    return run_qc_specifications(df)


def test_exactly_45_qc_rules_specified():
    assert len(QC_SPECIFICATIONS) == 45


def test_every_rule_type_has_a_dispatch_handler():
    rule_types = {spec["rule_type"] for spec in QC_SPECIFICATIONS}
    assert rule_types <= set(RULE_DISPATCH.keys())


def test_engine_produces_one_result_per_rule(results):
    assert len(results) == 45


def test_injected_defects_are_detected(results):
    """The simulation injects missingness, out-of-range values, bad codes,
    duplicates, and date-order violations on purpose -- the engine must
    flag at least some of them."""
    assert sum(r["n_fail"] for r in results) > 0


def test_clean_rules_show_zero_failures(results):
    """Rules on fields with no injected defects (e.g. age, which is
    always generated within range) should show exactly 0 failures."""
    age_range_rule = next(r for r in results if r["rule_id"] == "QC007")
    assert age_range_rule["n_fail"] == 0


def test_overall_accuracy_in_realistic_band(results):
    result = overall_accuracy(results)
    assert 90.0 <= result["overall_accuracy_pct"] <= 100.0


def test_date_order_rule_catches_violations(results):
    date_rule = next(r for r in results if r["rule_id"] == "QC015")
    assert date_rule["n_fail"] > 0


def test_qc_summary_table_covers_all_rule_types(results):
    summary = build_qc_summary_table(results)
    rule_types_in_spec = {spec["rule_type"] for spec in QC_SPECIFICATIONS}
    assert set(summary["rule_type"]) == rule_types_in_spec


def test_qc_failure_listing_only_contains_failing_rules(results):
    listing = build_qc_failure_listing(results)
    assert (listing["n_fail"] > 0).all()


def test_adding_a_new_rule_requires_no_new_code(df):
    """Demonstrates the specification-driven architecture: a brand-new
    rule (different field, same rule_type) runs correctly through the
    existing engine with zero new functions written."""
    new_rule = {"rule_id": "QC999", "field": "lab_value", "rule_type": "range", "params": {"min": -1000, "max": 1000}}
    result = run_qc_specifications(df, specs=[new_rule])
    assert len(result) == 1
    assert result[0]["n_fail"] == 0
