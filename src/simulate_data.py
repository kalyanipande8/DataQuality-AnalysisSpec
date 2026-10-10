"""Simulate a clinical analysis dataset (SDTM/ADaM-style) with realistic
injected data-quality defects, for the declarative QC specification engine
to validate."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_SUBJECTS = 450
SEED = 71


def simulate(n: int = N_SUBJECTS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    df = pd.DataFrame({
        "usubjid": [f"SUBJ-{i:04d}" for i in range(n)],
        "age": rng.integers(18, 90, n),
        "sex": rng.choice(["M", "F"], n),
        "arm": rng.choice(["Arm A", "Arm B", "Placebo"], n),
        "baseline_score": rng.normal(5, 2, n).round(2),
        "visit_1_date_offset": rng.integers(0, 30, n),
        "visit_2_date_offset": rng.integers(30, 90, n),
        "lab_value": rng.normal(25, 8, n).round(1),
    })

    # inject defects:
    missing_idx = rng.choice(n, size=int(n * 0.02), replace=False)
    df.loc[missing_idx, "sex"] = None

    bad_arm_idx = rng.choice(n, size=int(n * 0.01), replace=False)
    df.loc[bad_arm_idx, "arm"] = "Unknown Arm"

    oor_idx = rng.choice(n, size=int(n * 0.015), replace=False)
    df.loc[oor_idx, "lab_value"] = -999.0

    dup_idx = rng.choice(n, size=int(n * 0.008), replace=False)
    df.loc[dup_idx, "usubjid"] = df.loc[dup_idx[0], "usubjid"] if len(dup_idx) else None

    # inject date-order violations (visit 1 should always precede visit 2)
    date_violation_idx = rng.choice(n, size=int(n * 0.012), replace=False)
    df.loc[date_violation_idx, "visit_2_date_offset"] = df.loc[date_violation_idx, "visit_1_date_offset"] - 5

    return df


if __name__ == "__main__":
    df = simulate()
    print(df.shape)
    print(df.isna().sum())
