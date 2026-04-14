"""Prepare source selection metadata and demo fallbacks when needed."""

from mimic_eicu_pipeline import MANIFEST_PATH, prepare_sources, run_mode_label, source_warning_messages


def main() -> None:
    """Build the current source manifest and print the run mode."""

    manifest_rows = prepare_sources()
    print(f"Prepared {len(manifest_rows)} source table(s).")
    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Manifest ready at {MANIFEST_PATH}")
    warnings = source_warning_messages(manifest_rows)
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
