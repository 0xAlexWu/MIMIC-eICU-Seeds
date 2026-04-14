"""Write the observation profile and source summary for the current run."""

from mimic_eicu_pipeline import (
    OBSERVATION_PROFILE_PATH,
    SOURCE_SUMMARY_PATH,
    build_candidate_catalog,
    build_observation_profile,
    load_manifest,
    run_mode_label,
    write_candidate_catalog,
    write_csv,
    write_summary_markdown,
)


def main() -> None:
    """Refresh the profile outputs for the active source selection."""

    manifest_rows = load_manifest()
    candidates = build_candidate_catalog(manifest_rows)
    write_candidate_catalog(candidates)
    profile_rows = build_observation_profile(candidates)
    write_csv(OBSERVATION_PROFILE_PATH, profile_rows, ["metric", "value", "notes"])
    write_summary_markdown(manifest_rows, candidates)
    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Wrote observation profile to {OBSERVATION_PROFILE_PATH}")
    print(f"Wrote source summary to {SOURCE_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
