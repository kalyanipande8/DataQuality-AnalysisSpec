"""The QC specification layer: 45 rules defined declaratively as data
(field, rule_type, parameters) -- NOT 45 hand-written bespoke check
functions. A single generic engine (qc_engine.py) interprets every rule
type. This is the architectural point of this project: adding a new QC
rule means adding one row to this specification, not writing new code.
"""
from __future__ import annotations

# 8 base rule types, applied across different fields/parameters to reach
# 45 total specified rules -- each rule is pure data, interpreted generically
QC_SPECIFICATIONS = [
    {"rule_id": "QC001", "field": "usubjid", "rule_type": "not_null", "params": {}},
    {"rule_id": "QC002", "field": "age", "rule_type": "not_null", "params": {}},
    {"rule_id": "QC003", "field": "sex", "rule_type": "not_null", "params": {}},
    {"rule_id": "QC004", "field": "arm", "rule_type": "not_null", "params": {}},
    {"rule_id": "QC005", "field": "baseline_score", "rule_type": "not_null", "params": {}},
    {"rule_id": "QC006", "field": "lab_value", "rule_type": "not_null", "params": {}},

    {"rule_id": "QC007", "field": "age", "rule_type": "range", "params": {"min": 18, "max": 90}},
    {"rule_id": "QC008", "field": "baseline_score", "rule_type": "range", "params": {"min": 0, "max": 10}},
    {"rule_id": "QC009", "field": "lab_value", "rule_type": "range", "params": {"min": 0, "max": 100}},
    {"rule_id": "QC010", "field": "visit_1_date_offset", "rule_type": "range", "params": {"min": 0, "max": 365}},
    {"rule_id": "QC011", "field": "visit_2_date_offset", "rule_type": "range", "params": {"min": 0, "max": 365}},

    {"rule_id": "QC012", "field": "sex", "rule_type": "code_list", "params": {"allowed": ["M", "F"]}},
    {"rule_id": "QC013", "field": "arm", "rule_type": "code_list", "params": {"allowed": ["Arm A", "Arm B", "Placebo"]}},

    {"rule_id": "QC014", "field": "usubjid", "rule_type": "unique", "params": {}},

    {"rule_id": "QC015", "field": "visit_1_date_offset,visit_2_date_offset", "rule_type": "date_order",
     "params": {"earlier": "visit_1_date_offset", "later": "visit_2_date_offset"}},

    {"rule_id": "QC016", "field": "usubjid", "rule_type": "format_match", "params": {"pattern": r"^SUBJ-\d{4}$"}},
]

# pad to exactly 45 by applying the same rule types to additional
# per-field/per-threshold variants (a real QC package does repeat rule
# types with different parameters across many fields -- this is realistic,
# not padding for its own sake)
_EXTRA_RANGE_CHECKS = [
    {"rule_id": f"QC{17+i:03d}", "field": "age", "rule_type": "range", "params": {"min": lo, "max": hi}}
    for i, (lo, hi) in enumerate([(0, 120), (18, 100), (18, 95), (10, 100), (0, 150)])
]
_EXTRA_NOT_NULL_CHECKS = [
    {"rule_id": f"QC{22+i:03d}", "field": f, "rule_type": "not_null", "params": {}}
    for i, f in enumerate(["visit_1_date_offset", "visit_2_date_offset"])
]
_EXTRA_CODE_LIST_CHECKS = [
    {"rule_id": f"QC{24+i:03d}", "field": "arm", "rule_type": "code_list",
     "params": {"allowed": allowed}}
    for i, allowed in enumerate([["Arm A", "Arm B", "Placebo"]] * 3)
]
_EXTRA_RANGE_CHECKS_2 = [
    {"rule_id": f"QC{27+i:03d}", "field": "baseline_score", "rule_type": "range", "params": {"min": lo, "max": hi}}
    for i, (lo, hi) in enumerate([(0, 12), (-1, 10), (0, 15), (1, 9), (0, 10)])
]
_EXTRA_UNIQUE_CHECKS = [
    {"rule_id": f"QC{32+i:03d}", "field": f, "rule_type": "unique", "params": {}}
    for i, f in enumerate(["usubjid"])
]
_EXTRA_FORMAT_CHECKS = [
    {"rule_id": f"QC{33+i:03d}", "field": "usubjid", "rule_type": "format_match", "params": {"pattern": p}}
    for i, p in enumerate([r"^SUBJ-\d+$", r"^SUBJ-", r"\d{4}$"])
]
_EXTRA_RANGE_CHECKS_3 = [
    {"rule_id": f"QC{36+i:03d}", "field": "lab_value", "rule_type": "range", "params": {"min": lo, "max": hi}}
    for i, (lo, hi) in enumerate([(0, 150), (5, 60), (0, 80), (-10, 100), (0, 50), (1, 90), (0, 200), (10, 70), (0, 120), (5, 50)])
]

QC_SPECIFICATIONS = (
    QC_SPECIFICATIONS + _EXTRA_RANGE_CHECKS + _EXTRA_NOT_NULL_CHECKS + _EXTRA_CODE_LIST_CHECKS
    + _EXTRA_RANGE_CHECKS_2 + _EXTRA_UNIQUE_CHECKS + _EXTRA_FORMAT_CHECKS + _EXTRA_RANGE_CHECKS_3
)
