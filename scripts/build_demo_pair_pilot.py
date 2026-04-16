"""Build a tiny demo-only pair pilot from reviewed MIMIC/eICU shortlist rows."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from mimic_eicu_pipeline import (
    OUTPUT_DIR,
    PILOT_MAPPING_REVIEW_APPROVED_PATH,
    PILOT_MAPPING_REVIEW_FINAL_PATH,
    PILOT_MAPPING_REVIEW_MAYBE_PATH,
    PILOT_MAPPING_REVIEW_NEXT_STEP_PATH,
    PILOT_SHORTLIST_PATH,
    ambiguity_tokens,
    bool_from_text,
    load_manifest,
    read_csv,
    run_mode_label,
    write_csv,
)


DEMO_PAIR_DIR = OUTPUT_DIR / "demo_pair_pilot"
DEMO_PAIR_JSONL_PATH = DEMO_PAIR_DIR / "demo_pair_candidates.jsonl"
DEMO_PAIR_CSV_PATH = DEMO_PAIR_DIR / "demo_pair_candidates.csv"
DEMO_PAIR_SUMMARY_PATH = DEMO_PAIR_DIR / "demo_pair_generation_summary.md"
DEMO_PAIR_FLAGS_PATH = DEMO_PAIR_DIR / "demo_pair_review_flags.csv"
DEMO_PAIR_NEXT_STEP_PATH = DEMO_PAIR_DIR / "demo_pair_next_step.md"

ALLOWED_INPUT_STYLES = ["concise_clinical", "semi_structured"]
MAX_SOURCE_ITEMS = 10
MAX_OBSERVATION_ITEMS = 8
MAX_PATIENT_ITEMS = 1
MAX_CONDITION_ITEMS = 1

PAIR_FIELDNAMES = [
    "pair_id",
    "candidate_id",
    "source_dataset",
    "source_table",
    "resource_type",
    "input_style",
    "input_text",
    "target_fhir_json",
    "demo_only",
    "source_status",
    "review_status",
    "notes",
]

FLAG_FIELDNAMES = [
    "pair_id",
    "candidate_id",
    "resource_type",
    "flag_type",
    "flag_reason",
]


def parse_next_step_outcome(path: Path) -> str:
    """Read the prior next-step recommendation outcome if it exists."""

    if not path.exists():
        return "unknown"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("outcome:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def normalize_space(text: str) -> str:
    """Collapse repeated whitespace for stable short inputs."""

    return " ".join(str(text).strip().split())


def parse_structured_numeric(value: str) -> int | float:
    """Parse a numeric structured value while preserving integers when possible."""

    stripped = str(value).strip()
    if re.fullmatch(r"-?\d+", stripped):
        return int(stripped)
    return float(stripped)


def shortlist_index(shortlist_rows: list[dict]) -> dict[str, dict]:
    """Index shortlist rows by candidate id."""

    return {row["candidate_id"]: row for row in shortlist_rows}


def row_rank(row: dict) -> int:
    """Return a deterministic numeric rank for a reviewed row."""

    try:
        return int(row.get("shortlist_rank", "999"))
    except ValueError:
        return 999


def observation_fallback_eligibility(row: dict, shortlist_row: dict | None) -> tuple[bool, str]:
    """Apply a strict fallback filter for maybe_later Observation rows."""

    if row.get("likely_fhir_resource") != "Observation":
        resource = row.get("likely_fhir_resource", "")
        if resource == "Patient":
            return False, "Patient fragment remains too sparse for a demo-only pair pilot."
        if resource == "Condition":
            return False, "Condition coding remains too uncertain for a demo-only pair pilot."
        return False, "Only Observation fallback rows are allowed in this demo-only pair stage."
    if row.get("final_status") != "maybe_later":
        return False, "Only maybe_later rows are eligible for conservative fallback."
    if bool_from_text(row.get("needs_linked_context", "false")):
        return False, "Hidden linked context is still required."
    if row.get("proposed_fhir_path") not in {"Observation.valueQuantity", "Observation.valueString"}:
        return False, "FHIR path is not conservative enough for the demo-only pilot."
    if shortlist_row is None:
        return False, "Backing shortlist row is missing."
    if shortlist_row.get("complexity_guess", "").strip().lower() not in {"", "low"}:
        return False, "Candidate complexity is above the demo-only threshold."
    if not bool_from_text(shortlist_row.get("good_for_pairing", "false")):
        return False, "Candidate was not marked as good_for_pairing."
    ambiguity = ambiguity_tokens(row.get("ambiguity_flag", ""))
    if "unit_review" in ambiguity:
        return False, "Unit handling still needs expert confirmation."
    if row.get("proposed_fhir_path") == "Observation.valueQuantity":
        if not row.get("proposed_unit", "").strip():
            return False, "Unit-sensitive quantity is missing a trustworthy unit."
        if not shortlist_row.get("structured_value", "").strip():
            return False, "Structured numeric value is missing."
    return True, ""


def minimal_code_block(row: dict) -> dict:
    """Build the most conservative supported Observation or Condition code block."""

    display = normalize_space(row.get("proposed_display") or row.get("raw_measure_name"))
    code_system = row.get("proposed_code_system", "").strip()
    code = row.get("proposed_code", "").strip()
    code_block: dict[str, object] = {}
    if code_system and code:
        coding = {"system": code_system, "code": code}
        if display:
            coding["display"] = display
        code_block["coding"] = [coding]
    if display:
        code_block["text"] = display
    return code_block


def build_target_fhir_json(row: dict, shortlist_row: dict) -> dict:
    """Construct a minimal FHIR resource using only supported reviewed fields."""

    resource = row["likely_fhir_resource"]
    if resource == "Observation":
        target: dict[str, object] = {"resourceType": "Observation"}
        code_block = minimal_code_block(row)
        if code_block:
            target["code"] = code_block
        path = row.get("proposed_fhir_path", "")
        if path == "Observation.valueQuantity":
            value_quantity: dict[str, object] = {
                "value": parse_structured_numeric(shortlist_row["structured_value"]),
            }
            if row.get("proposed_unit", "").strip():
                value_quantity["unit"] = row["proposed_unit"].strip()
            if row.get("ucum_unit", "").strip():
                value_quantity["system"] = "http://unitsofmeasure.org"
                value_quantity["code"] = row["ucum_unit"].strip()
            target["valueQuantity"] = value_quantity
        elif path == "Observation.valueString":
            target["valueString"] = normalize_space(
                shortlist_row.get("structured_value") or row.get("candidate_text_snippet", "")
            )
        return target

    if resource == "Patient":
        target = {"resourceType": "Patient"}
        path = row.get("proposed_fhir_path", "")
        display = normalize_space(row.get("proposed_display") or shortlist_row.get("structured_value", ""))
        if path == "Patient.gender" and display:
            target["gender"] = display.lower()
        elif path == "Patient.birthDate" and shortlist_row.get("structured_value", "").strip():
            target["birthDate"] = shortlist_row["structured_value"].strip()
        return target

    if resource == "Condition":
        target = {"resourceType": "Condition"}
        code_block = minimal_code_block(row)
        if code_block:
            target["code"] = code_block
        return target

    return {"resourceType": resource}


def build_input_text(row: dict, shortlist_row: dict, input_style: str) -> str:
    """Render the allowed terse input variants for the demo-only pilot."""

    if input_style == "concise_clinical":
        return normalize_space(row.get("candidate_text_snippet", ""))

    display = normalize_space(row.get("proposed_display") or row.get("raw_measure_name", ""))
    value = normalize_space(shortlist_row.get("structured_value", ""))
    unit = normalize_space(row.get("proposed_unit", "") or shortlist_row.get("unit_if_available", ""))
    if unit:
        return f"{display}: {value} {unit}".strip()
    return f"{display}: {value}".strip()


def selection_note(selection_mode: str) -> str:
    """Explain why a row is being used for pair generation."""

    if selection_mode == "approved_only":
        return "demo-only approved shortlist row; target JSON kept minimal and no hidden context was added."
    return (
        "demo-only fallback from maybe_later Observation row; code kept text-only or minimal and "
        "subject/encounter references were omitted because the snippet does not resolve them."
    )


def build_review_flags(pair_row: dict, review_row: dict) -> list[dict]:
    """Attach explicit review-risk flags to each generated pair."""

    flags = []
    resource_type = pair_row["resource_type"]
    pair_id = pair_row["pair_id"]
    candidate_id = pair_row["candidate_id"]
    ambiguity = ambiguity_tokens(review_row.get("ambiguity_flag", ""))

    if "code_review" in ambiguity:
        flags.append(
            {
                "pair_id": pair_id,
                "candidate_id": candidate_id,
                "resource_type": resource_type,
                "flag_type": "coding_uncertainty",
                "flag_reason": "Reviewed row still lacks confirmed source coding, so the JSON keeps code text minimal.",
            }
        )
    if resource_type == "Observation" and review_row.get("proposed_fhir_path") == "Observation.valueQuantity":
        flags.append(
            {
                "pair_id": pair_id,
                "candidate_id": candidate_id,
                "resource_type": resource_type,
                "flag_type": "unit_sensitivity",
                "flag_reason": "Quantity meaning depends on preserving the exact numeric value and unit.",
            }
        )
    if review_row.get("subject_required") == "yes" or review_row.get("encounter_required") == "yes":
        flags.append(
            {
                "pair_id": pair_id,
                "candidate_id": candidate_id,
                "resource_type": resource_type,
                "flag_type": "possible_omission",
                "flag_reason": "Subject or encounter linkage was reviewed as relevant, but resolvable references were omitted in demo mode.",
            }
        )
    if pair_row["input_style"] == "semi_structured":
        flags.append(
            {
                "pair_id": pair_id,
                "candidate_id": candidate_id,
                "resource_type": resource_type,
                "flag_type": "near_duplicate_variant",
                "flag_reason": "Semi-structured variant stays intentionally close to the concise clinical phrasing.",
            }
        )
    return flags


def choose_source_rows(
    approved_rows: list[dict],
    maybe_rows: list[dict],
    shortlist_rows: list[dict],
) -> tuple[str, list[dict], list[dict]]:
    """Select a tiny conservative source set and log excluded reviewed rows."""

    shortlist_by_id = shortlist_index(shortlist_rows)
    excluded_rows: list[dict] = []

    if approved_rows:
        approved_sorted = sorted(approved_rows, key=row_rank)
        observations = [row for row in approved_sorted if row["likely_fhir_resource"] == "Observation"][:MAX_OBSERVATION_ITEMS]
        patients = [row for row in approved_sorted if row["likely_fhir_resource"] == "Patient"][:MAX_PATIENT_ITEMS]
        conditions = [row for row in approved_sorted if row["likely_fhir_resource"] == "Condition"][:MAX_CONDITION_ITEMS]
        selected = (observations + patients + conditions)[:MAX_SOURCE_ITEMS]
        selected_ids = {row["candidate_id"] for row in selected}
        for row in sorted(approved_rows + maybe_rows, key=row_rank):
            if row["candidate_id"] not in selected_ids:
                excluded_rows.append(
                    {
                        "candidate_id": row["candidate_id"],
                        "reason": "Not selected because the demo-only pilot uses approved rows first and stays tiny.",
                    }
                )
        return "approved_only", selected, excluded_rows

    selected = []
    for row in sorted(maybe_rows, key=row_rank):
        shortlist_row = shortlist_by_id.get(row["candidate_id"])
        eligible, reason = observation_fallback_eligibility(row, shortlist_row)
        if not eligible:
            excluded_rows.append({"candidate_id": row["candidate_id"], "reason": reason})
            continue
        if len(selected) >= MAX_OBSERVATION_ITEMS:
            excluded_rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "reason": "Observation cap reached for the tiny demo-only pilot.",
                }
            )
            continue
        selected.append(row)

    return "fallback_to_maybe", selected[:MAX_SOURCE_ITEMS], excluded_rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    """Write JSONL rows with deterministic key order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")


def build_summary_markdown(
    manifest_rows: list[dict],
    selection_mode: str,
    reviewed_final_rows: list[dict],
    selected_rows: list[dict],
    excluded_rows: list[dict],
    pair_rows: list[dict],
    prior_next_step_outcome: str,
) -> str:
    """Render the generation summary for the tiny demo-only pilot."""

    resource_counts = Counter(row["resource_type"] for row in pair_rows)
    style_counts = Counter(row["input_style"] for row in pair_rows)
    source_resource_counts = Counter(row["likely_fhir_resource"] for row in selected_rows)
    approved_exists = any(row["final_status"] == "approved" for row in reviewed_final_rows)

    excluded_lines = ["- none"] if not excluded_rows else [
        f"- `{row['candidate_id']}`: {row['reason']}" for row in excluded_rows
    ]
    source_mix = (
        f"{source_resource_counts.get('Observation', 0)} Observation, "
        f"{source_resource_counts.get('Patient', 0)} Patient, "
        f"{source_resource_counts.get('Condition', 0)} Condition"
    )
    pair_mix = (
        f"{resource_counts.get('Observation', 0)} Observation, "
        f"{resource_counts.get('Patient', 0)} Patient, "
        f"{resource_counts.get('Condition', 0)} Condition"
    )
    style_mix = ", ".join(
        f"{style}: {style_counts.get(style, 0)}" for style in ALLOWED_INPUT_STYLES
    ) or "none"
    fallback_line = "yes" if selection_mode == "fallback_to_maybe" else "no"
    external_review_ready = (
        len(selected_rows) >= 6
        and source_resource_counts.get("Observation", 0) >= 6
        and source_resource_counts.get("Observation", 0) > (
            source_resource_counts.get("Patient", 0) + source_resource_counts.get("Condition", 0)
        )
    )

    return "\n".join(
        [
            "# Demo Pair Generation Summary",
            "",
            f"- run_mode: `{run_mode_label(manifest_rows)}`",
            f"- approved_rows_existed: `{'yes' if approved_exists else 'no'}`",
            f"- fallback_to_maybe_used: `{fallback_line}`",
            f"- prior_formal_next_step: `{prior_next_step_outcome}`",
            f"- final_source_items_retained: `{len(selected_rows)}`",
            f"- final_pair_count: `{len(pair_rows)}`",
            f"- source_item_composition: `{source_mix}`",
            f"- pair_composition_by_resource: `{pair_mix}`",
            f"- pair_composition_by_input_style: `{style_mix}`",
            "",
            "## Excluded At Pair Stage",
            *excluded_lines,
            "",
            "## Why This Is Demo-Only",
            "- every retained row comes from demo-equivalent MIMIC-IV or eICU-backed workflow outputs",
            "- no approved reviewed rows existed, so this pilot relies on conservative Observation-only fallback from `maybe_later`",
            "- coding remains intentionally minimal or text-only where the reviewed mapping never confirmed a source code",
            "- subject and encounter references were not fabricated from terse snippets",
            "- this tiny set is for workflow validation only and is not suitable for mother-pool inclusion",
            "",
            "## External AI Review Readiness",
            (
                "- good enough for a small external AI review focused on workflow validation only"
                if external_review_ready
                else "- still too thin for external AI review without additional clarification"
            ),
        ]
    ) + "\n"


def build_next_step_markdown(selected_rows: list[dict]) -> str:
    """Choose the conservative next step for the demo-only pair pilot."""

    resource_counts = Counter(row["likely_fhir_resource"] for row in selected_rows)
    observation_count = resource_counts.get("Observation", 0)
    patient_count = resource_counts.get("Patient", 0)
    condition_count = resource_counts.get("Condition", 0)
    pair_count = len(selected_rows) * len(ALLOWED_INPUT_STYLES)
    if len(selected_rows) >= 6 and observation_count >= 6:
        return "\n".join(
            [
                "outcome: ready_for_demo_review",
                "recommended_next_step: package these demo pairs for external AI review",
                "scope_note: workflow validation only; do not treat these pairs as part of the formal MIMIC/eICU mother pool",
                f"maximum_recommended_pilot_size: {pair_count} pairs from {len(selected_rows)} source items",
                (
                    "recommended_resource_mix: "
                    f"Observation {observation_count}, Patient {patient_count}, Condition {condition_count}"
                ),
                "strict_constraints:",
                "- keep the branch demo-only",
                "- do not add paraphrased or stylized variants",
                "- do not promote text-only coding into confident coded mappings",
                "- do not infer subject, encounter, time, or diagnosis context that the shortlist does not explicitly support",
            ]
        ) + "\n"
    return "\n".join(
        [
            "outcome: demo_pairs_too_ambiguous",
            "reason: even the conservative fallback pool did not yield enough low-ambiguity Observation rows for a trustworthy demo pilot.",
        ]
    ) + "\n"


def main() -> None:
    """Create a tiny demo-only pair pilot from the reviewed mapping outputs."""

    manifest_rows = load_manifest()
    reviewed_final_rows = read_csv(PILOT_MAPPING_REVIEW_FINAL_PATH)
    approved_rows = read_csv(PILOT_MAPPING_REVIEW_APPROVED_PATH)
    maybe_rows = read_csv(PILOT_MAPPING_REVIEW_MAYBE_PATH)
    shortlist_rows = read_csv(PILOT_SHORTLIST_PATH)
    if not reviewed_final_rows:
        raise SystemExit(f"No finalized mapping review rows found at {PILOT_MAPPING_REVIEW_FINAL_PATH}")
    if not shortlist_rows:
        raise SystemExit(f"No shortlist rows found at {PILOT_SHORTLIST_PATH}")

    selection_mode, selected_rows, excluded_rows = choose_source_rows(approved_rows, maybe_rows, shortlist_rows)
    if not selected_rows:
        DEMO_PAIR_DIR.mkdir(parents=True, exist_ok=True)
        DEMO_PAIR_SUMMARY_PATH.write_text(
            "# Demo Pair Generation Summary\n\n- no rows were conservative enough for demo-only pair generation\n",
            encoding="utf-8",
        )
        DEMO_PAIR_NEXT_STEP_PATH.write_text(
            "outcome: demo_pairs_too_ambiguous\nreason: no reviewed rows met the demo-only fallback criteria.\n",
            encoding="utf-8",
        )
        write_csv(DEMO_PAIR_CSV_PATH, [], PAIR_FIELDNAMES)
        write_jsonl(DEMO_PAIR_JSONL_PATH, [])
        write_csv(DEMO_PAIR_FLAGS_PATH, [], FLAG_FIELDNAMES)
        print("No rows met the conservative demo-only pair criteria.")
        return

    shortlist_by_id = shortlist_index(shortlist_rows)
    pair_jsonl_rows = []
    pair_csv_rows = []
    flag_rows = []

    for pair_number, review_row in enumerate(selected_rows, start=1):
        shortlist_row = shortlist_by_id[review_row["candidate_id"]]
        target_fhir_json = build_target_fhir_json(review_row, shortlist_row)
        for style_offset, input_style in enumerate(ALLOWED_INPUT_STYLES):
            pair_id = f"demo-mimic-eicu-pair-{((pair_number - 1) * len(ALLOWED_INPUT_STYLES)) + style_offset + 1:04d}"
            input_text = build_input_text(review_row, shortlist_row, input_style)
            notes = selection_note(selection_mode)
            pair_json_row = {
                "pair_id": pair_id,
                "candidate_id": review_row["candidate_id"],
                "source_dataset": review_row["source_dataset"],
                "source_table": review_row["source_table"],
                "resource_type": review_row["likely_fhir_resource"],
                "input_style": input_style,
                "input_text": input_text,
                "target_fhir_json": target_fhir_json,
                "demo_only": True,
                "source_status": "demo_equivalent",
                "review_status": review_row["final_status"],
                "notes": notes,
            }
            pair_jsonl_rows.append(pair_json_row)
            pair_csv_rows.append(
                {
                    **pair_json_row,
                    "target_fhir_json": json.dumps(target_fhir_json, ensure_ascii=False, sort_keys=True),
                    "demo_only": "true",
                }
            )
            flag_rows.extend(build_review_flags(pair_json_row, review_row))

    prior_next_step_outcome = parse_next_step_outcome(PILOT_MAPPING_REVIEW_NEXT_STEP_PATH)
    write_jsonl(DEMO_PAIR_JSONL_PATH, pair_jsonl_rows)
    write_csv(DEMO_PAIR_CSV_PATH, pair_csv_rows, PAIR_FIELDNAMES)
    write_csv(DEMO_PAIR_FLAGS_PATH, flag_rows, FLAG_FIELDNAMES)
    DEMO_PAIR_SUMMARY_PATH.write_text(
        build_summary_markdown(
            manifest_rows,
            selection_mode,
            reviewed_final_rows,
            selected_rows,
            excluded_rows,
            pair_jsonl_rows,
            prior_next_step_outcome,
        ),
        encoding="utf-8",
    )
    DEMO_PAIR_NEXT_STEP_PATH.write_text(build_next_step_markdown(selected_rows), encoding="utf-8")

    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Read finalized mapping review from {PILOT_MAPPING_REVIEW_FINAL_PATH}")
    print(f"Selection mode: {selection_mode}")
    print(f"Retained source items: {len(selected_rows)}")
    print(f"Wrote JSONL pairs to {DEMO_PAIR_JSONL_PATH}")
    print(f"Wrote CSV pairs to {DEMO_PAIR_CSV_PATH}")
    print(f"Wrote review flags to {DEMO_PAIR_FLAGS_PATH}")
    print(f"Wrote summary to {DEMO_PAIR_SUMMARY_PATH}")
    print(f"Wrote next-step note to {DEMO_PAIR_NEXT_STEP_PATH}")


if __name__ == "__main__":
    main()
