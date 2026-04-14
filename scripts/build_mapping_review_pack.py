"""Build the mapping review CSV and reviewer batch prompt."""

from mimic_eicu_pipeline import (
    PILOT_MAPPING_REVIEW_PATH,
    PILOT_SHORTLIST_PATH,
    REVIEWER_BATCH_PROMPT_PATH,
    build_mapping_review_rows,
    build_shortlist_artifacts,
    load_manifest,
    load_or_build_candidate_catalog,
    read_csv,
    run_mode_label,
    write_csv,
    write_reviewer_batch_prompt,
)


def main() -> None:
    """Create the mapping review pack from the current shortlist."""

    manifest_rows = load_manifest()
    shortlist_rows = read_csv(PILOT_SHORTLIST_PATH)
    if not shortlist_rows:
        candidate_rows = load_or_build_candidate_catalog()
        shortlist_rows, _ = build_shortlist_artifacts(candidate_rows)
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
    mapping_rows = build_mapping_review_rows(shortlist_rows)
    write_csv(PILOT_MAPPING_REVIEW_PATH, mapping_rows, [
        "shortlist_rank",
        "candidate_id",
        "source_dataset",
        "source_table",
        "raw_measure_name",
        "candidate_text_snippet",
        "likely_fhir_resource",
        "proposed_fhir_path",
        "proposed_value_type",
        "proposed_code_system",
        "proposed_code",
        "proposed_display",
        "proposed_unit",
        "ucum_unit",
        "subject_required",
        "encounter_required",
        "needs_linked_context",
        "ambiguity_flag",
        "reviewer_decision",
        "reviewer_comments",
    ])
    write_reviewer_batch_prompt()
    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Read shortlist from {PILOT_SHORTLIST_PATH}")
    print(f"Wrote mapping review table to {PILOT_MAPPING_REVIEW_PATH}")
    print(f"Wrote reviewer prompt to {REVIEWER_BATCH_PROMPT_PATH}")


if __name__ == "__main__":
    main()
