"""Consolidate reviewed mapping decisions into approved, maybe, and rejected outputs."""

from mimic_eicu_pipeline import (
    MAPPING_REVIEW_FINAL_FIELDNAMES,
    PILOT_MAPPING_REVIEW_APPROVED_PATH,
    PILOT_MAPPING_REVIEW_DECISION_SUMMARY_PATH,
    PILOT_MAPPING_REVIEW_FINAL_PATH,
    PILOT_MAPPING_REVIEW_MAYBE_PATH,
    PILOT_MAPPING_REVIEW_NEXT_STEP_PATH,
    PILOT_MAPPING_REVIEW_PATH,
    PILOT_MAPPING_REVIEW_REJECTED_PATH,
    build_mapping_review_decision_artifacts,
    load_manifest,
    read_csv,
    run_mode_label,
    write_csv,
    write_mapping_review_decision_summary,
    write_mapping_review_next_step,
)


def main() -> None:
    """Finalize the mapping review table into decision-specific artifacts."""

    manifest_rows = load_manifest()
    mapping_rows = read_csv(PILOT_MAPPING_REVIEW_PATH)
    if not mapping_rows:
        raise SystemExit(f"No mapping review rows found at {PILOT_MAPPING_REVIEW_PATH}")

    decision_rows = build_mapping_review_decision_artifacts(mapping_rows)
    write_csv(PILOT_MAPPING_REVIEW_FINAL_PATH, decision_rows["finalized"], MAPPING_REVIEW_FINAL_FIELDNAMES)
    write_csv(PILOT_MAPPING_REVIEW_APPROVED_PATH, decision_rows["approved"], MAPPING_REVIEW_FINAL_FIELDNAMES)
    write_csv(PILOT_MAPPING_REVIEW_MAYBE_PATH, decision_rows["maybe"], MAPPING_REVIEW_FINAL_FIELDNAMES)
    write_csv(PILOT_MAPPING_REVIEW_REJECTED_PATH, decision_rows["rejected"], MAPPING_REVIEW_FINAL_FIELDNAMES)
    write_mapping_review_decision_summary(manifest_rows, decision_rows)
    write_mapping_review_next_step(manifest_rows, decision_rows)

    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Read reviewed mapping table from {PILOT_MAPPING_REVIEW_PATH}")
    print(f"Wrote final decision table to {PILOT_MAPPING_REVIEW_FINAL_PATH}")
    print(f"Wrote approved rows to {PILOT_MAPPING_REVIEW_APPROVED_PATH}")
    print(f"Wrote maybe rows to {PILOT_MAPPING_REVIEW_MAYBE_PATH}")
    print(f"Wrote rejected rows to {PILOT_MAPPING_REVIEW_REJECTED_PATH}")
    print(f"Wrote decision summary to {PILOT_MAPPING_REVIEW_DECISION_SUMMARY_PATH}")
    print(f"Wrote next-step recommendation to {PILOT_MAPPING_REVIEW_NEXT_STEP_PATH}")


if __name__ == "__main__":
    main()
