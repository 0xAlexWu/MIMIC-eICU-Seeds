"""Profile currently selected MIMIC/eICU tables into a compact CSV summary."""

from mimic_eicu_pipeline import SOURCE_COUNTS_PATH, build_source_counts, load_manifest, run_mode_label, write_csv


def main() -> None:
    """Write the table-level profiling summary for the active source mode."""

    manifest_rows = load_manifest()
    summary_rows = build_source_counts(manifest_rows)
    write_csv(
        SOURCE_COUNTS_PATH,
        summary_rows,
        [
            "source_dataset",
            "source_table",
            "access_mode",
            "selected_file_path",
            "source_row_count",
            "candidate_count",
            "observation_like_count",
            "patient_like_count",
            "condition_like_count",
            "likely_numeric_count",
            "with_units_count",
            "warning",
            "notes",
        ],
    )
    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Wrote {len(summary_rows)} table profile row(s) to {SOURCE_COUNTS_PATH}")


if __name__ == "__main__":
    main()
