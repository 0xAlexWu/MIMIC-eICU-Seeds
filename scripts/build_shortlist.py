"""Build the conservative manual-review shortlist and exclusion log."""

from mimic_eicu_pipeline import (
    CANDIDATE_CATALOG_PATH,
    EXCLUSION_LOG_PATH,
    PILOT_READINESS_SUMMARY_PATH,
    PILOT_SHORTLIST_PATH,
    PILOT_SHORTLIST_SUMMARY_PATH,
    build_shortlist_artifacts,
    load_manifest,
    load_or_build_candidate_catalog,
    run_mode_label,
    write_csv,
    write_pilot_readiness_summary,
    write_pilot_shortlist_summary,
    write_summary_markdown,
)


def main() -> None:
    """Create the manual-review shortlist from the exported candidate catalog."""

    manifest_rows = load_manifest()
    candidate_rows = load_or_build_candidate_catalog()
    shortlist_rows, exclusion_rows = build_shortlist_artifacts(candidate_rows)
    write_csv(PILOT_SHORTLIST_PATH, shortlist_rows, [
        "shortlist_rank",
        "candidate_id",
        "source_dataset",
        "source_table",
        "source_column_or_measure",
        "patient_or_stay_id_if_available",
        "likely_fhir_resource",
        "candidate_text_snippet",
        "structured_value",
        "unit_if_available",
        "likely_numeric",
        "needs_linked_context",
        "complexity_guess",
        "good_for_pairing",
        "mapping_notes",
        "review_notes",
        "shortlist_reason",
        "reviewer_priority",
        "provisional_status",
    ])
    write_csv(EXCLUSION_LOG_PATH, exclusion_rows, [
        "candidate_id",
        "source_dataset",
        "source_table",
        "likely_fhir_resource",
        "exclusion_reason",
        "exclusion_bucket",
    ])
    write_pilot_shortlist_summary(manifest_rows, shortlist_rows, exclusion_rows)
    write_pilot_readiness_summary(manifest_rows, shortlist_rows, exclusion_rows)
    write_summary_markdown(manifest_rows, candidate_rows, shortlist_rows, exclusion_rows)
    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Read candidate catalog from {CANDIDATE_CATALOG_PATH}")
    print(f"Wrote shortlist to {PILOT_SHORTLIST_PATH}")
    print(f"Wrote exclusion log to {EXCLUSION_LOG_PATH}")
    print(f"Wrote shortlist summary to {PILOT_SHORTLIST_SUMMARY_PATH}")
    print(f"Wrote readiness summary to {PILOT_READINESS_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
