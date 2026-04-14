"""Build the exported candidate catalog from the active source selection."""

from mimic_eicu_pipeline import build_candidate_catalog, load_manifest, run_mode_label, write_candidate_catalog


def main() -> None:
    """Write the candidate catalog for the current run mode."""

    manifest_rows = load_manifest()
    candidates = build_candidate_catalog(manifest_rows)
    write_candidate_catalog(candidates)
    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Wrote {len(candidates)} candidate row(s).")


if __name__ == "__main__":
    main()
