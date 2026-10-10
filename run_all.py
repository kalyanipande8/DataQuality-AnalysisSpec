"""End-to-end: simulate data, run the 45-rule specification-driven QC
engine, and build TLF specifications/mock-up displays of the results."""
import json
import os

from src.simulate_data import simulate
from src.qc_spec import QC_SPECIFICATIONS
from src.qc_engine import run_qc_specifications, overall_accuracy
from src.tlf_spec_mockup import build_qc_summary_table, build_qc_failure_listing, TLF_SPECS

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating clinical analysis dataset ===")
df = simulate()
df.to_csv("data/analysis_data.csv", index=False)
print(f"{len(df)} subjects")

print(f"\n=== Running {len(QC_SPECIFICATIONS)}-rule specification-driven QC engine ===")
results = run_qc_specifications(df)
accuracy = overall_accuracy(results)
print(accuracy)

print("\n=== TLF specifications for QC results ===")
for spec in TLF_SPECS:
    print(spec)

print("\n=== QC summary table (by rule type) ===")
summary_table = build_qc_summary_table(results)
print(summary_table)
summary_table.to_csv("results/qc_summary_table.csv", index=False)

print("\n=== QC failure listing ===")
failure_listing = build_qc_failure_listing(results)
print(failure_listing)
failure_listing.to_csv("results/qc_failure_listing.csv", index=False)

summary = {
    "n_subjects": len(df),
    "n_qc_rules": len(QC_SPECIFICATIONS),
    **accuracy,
    "n_rules_with_failures": len(failure_listing),
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
