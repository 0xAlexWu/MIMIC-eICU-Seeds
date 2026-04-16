"""Package demo-only MIMIC/eICU pair candidates into external reviewer batches."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from mimic_eicu_pipeline import OUTPUT_DIR, REPO_ROOT, load_manifest, read_csv, run_mode_label, write_csv


BATCH_SIZE = 10
DEMO_PAIR_DIR = OUTPUT_DIR / "demo_pair_pilot"
PAIR_JSONL_PATH = DEMO_PAIR_DIR / "demo_pair_candidates.jsonl"
PAIR_CSV_PATH = DEMO_PAIR_DIR / "demo_pair_candidates.csv"
PAIR_SUMMARY_PATH = DEMO_PAIR_DIR / "demo_pair_generation_summary.md"
PAIR_NEXT_STEP_PATH = DEMO_PAIR_DIR / "demo_pair_next_step.md"
PROMPT_DIR = DEMO_PAIR_DIR / "reviewer_batch_prompts"
ROOT_PROMPT_DIR = REPO_ROOT / "outputs" / "reviewer_batch_prompts"
INDEX_PATH = DEMO_PAIR_DIR / "reviewer_batch_index.csv"
MANIFEST_PATH = DEMO_PAIR_DIR / "reviewer_batch_manifest.jsonl"
SUMMARY_PATH = DEMO_PAIR_DIR / "reviewer_batching_summary.md"

PROMPT_HEADER = """You are acting as an external reviewer in a clinical-data-to-FHIR pairing evaluation workflow.

These items come from a demo-only MIMIC/eICU workflow-validation pilot.
They are intended only to test the pairing and review workflow.
They are not part of the formal real-data paired mother pool.

You will review multiple candidate paired samples.
Apply the same scoring rubric independently to each item.
Do not compare items with each other.
Judge each pair only on its own merits.

For each item, return:
- pair_id
- faithfulness
- unsupported_fact
- omission
- naturalness
- context_leakage
- short_rationale
- flag_type

Scoring rubric:
- faithfulness: 1 = faithful, 0 = not faithful
- unsupported_fact: 1 = yes, 0 = no
- omission: 1 = yes, 0 = no
- naturalness: 1 to 5
- context_leakage: 1 = yes, 0 = no

Allowed flag_type values:
- none
- possible_hallucination
- possible_omission
- awkward_input
- context_leakage
- style_uncertainty
- other

Review principles:
1. Only judge alignment between the shown input text and the shown target FHIR JSON.
2. Do not assume facts from linked resources unless explicitly present in the shown target JSON.
3. Do not reward unsupported extra detail.
4. Be conservative about unsupported facts.
5. Be conservative about omission of core information.
6. If the target is sparse, do not punish the input for not containing unavailable details.

Return only a JSON array.
Do not include markdown.
Do not include any text before or after the JSON array.
"""

INDEX_FIELDNAMES = [
    "batch_id",
    "file_name",
    "start_pair_id",
    "end_pair_id",
    "item_count",
]


def load_pairs_jsonl(path: Path) -> list[dict]:
    """Load pair candidates from JSONL and sort deterministically by pair id."""

    if not path.exists():
        raise SystemExit(f"Missing demo pair JSONL input: {path}")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return sorted(rows, key=lambda row: row["pair_id"])


def validate_pair_csv(path: Path, jsonl_rows: list[dict]) -> None:
    """Confirm the CSV export matches the JSONL export at the pair-id level."""

    csv_rows = read_csv(path)
    if len(csv_rows) != len(jsonl_rows):
        raise SystemExit(
            f"Pair count mismatch between JSONL ({len(jsonl_rows)}) and CSV ({len(csv_rows)})"
        )
    jsonl_ids = [row["pair_id"] for row in jsonl_rows]
    csv_ids = [row["pair_id"] for row in csv_rows]
    if csv_ids != jsonl_ids:
        raise SystemExit("Pair ordering mismatch between JSONL and CSV inputs.")


def read_outcome(path: Path) -> str:
    """Read a simple outcome field from the existing markdown note."""

    if not path.exists():
        return "unknown"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("outcome:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def chunked(items: list[dict], batch_size: int) -> list[list[dict]]:
    """Split items into fixed-size batches."""

    return [items[index : index + batch_size] for index in range(0, len(items), batch_size)]


def render_target_json(target_fhir_json: object) -> str:
    """Render target JSON without changing its content."""

    return json.dumps(target_fhir_json, ensure_ascii=False, indent=2)


def render_item(item_number: int, pair: dict) -> tuple[str, dict]:
    """Render one reviewer item block and record its approximate size."""

    rendered = (
        f"ITEM {item_number}\n"
        f"pair_id: {pair['pair_id']}\n"
        f"resource_type: {pair['resource_type']}\n"
        f"input_style: {pair['input_style']}\n"
        "input_text:\n"
        f"{pair['input_text']}\n"
        "target_fhir_json:\n"
        f"{render_target_json(pair['target_fhir_json']).rstrip()}\n"
    )
    return rendered, {
        "pair_id": pair["pair_id"],
        "resource_type": pair["resource_type"],
        "length_chars": len(rendered),
    }


def build_prompt(batch_pairs: list[dict]) -> tuple[str, list[dict]]:
    """Build one self-contained reviewer prompt file."""

    rendered_items = []
    item_stats = []
    for item_number, pair in enumerate(batch_pairs, start=1):
        rendered, stats = render_item(item_number, pair)
        rendered_items.append(rendered)
        item_stats.append(stats)
    prompt_text = PROMPT_HEADER.rstrip() + "\n\n" + "\n\n".join(rendered_items) + "\n"
    return prompt_text, item_stats


def unusual_long_items(item_stats: list[dict]) -> list[dict]:
    """Flag unusually long rendered review items for manual attention."""

    lengths = [item["length_chars"] for item in item_stats]
    if not lengths:
        return []
    if len(lengths) < 4:
        return sorted(item_stats, key=lambda row: row["length_chars"], reverse=True)[:1]
    sorted_lengths = sorted(lengths)
    midpoint = len(sorted_lengths) // 2
    lower_half = sorted_lengths[:midpoint]
    upper_half = sorted_lengths[-midpoint:]
    q1 = statistics.median(lower_half)
    q3 = statistics.median(upper_half)
    iqr = q3 - q1
    threshold = q3 + (1.5 * iqr)
    return sorted(
        [item for item in item_stats if item["length_chars"] > threshold],
        key=lambda row: row["length_chars"],
        reverse=True,
    )


def write_jsonl(path: Path, rows: list[dict]) -> None:
    """Write JSONL output with deterministic ordering."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def write_summary(
    path: Path,
    manifest_rows: list[dict],
    total_pairs: int,
    batches: list[list[dict]],
    long_items: list[dict],
    prior_outcome: str,
) -> None:
    """Write a markdown batching summary for the demo reviewer prompts."""

    full_batches = sum(len(batch) == BATCH_SIZE for batch in batches)
    partial_batch = any(len(batch) < BATCH_SIZE for batch in batches)
    lines = [
        "# Reviewer Batching Summary",
        "",
        f"- run_mode: `{run_mode_label(manifest_rows)}`",
        f"- prior_demo_pair_next_step: `{prior_outcome}`",
        f"- total number of demo pairs packaged: `{total_pairs}`",
        f"- total number of batches created: `{len(batches)}`",
        f"- full 10-item batches created: `{full_batches}`",
        f"- final partial batch present: `{'yes' if partial_batch else 'no'}`",
        "",
        "## Unusually Long Items",
    ]
    if long_items:
        for item in long_items:
            lines.append(
                f"- `{item['pair_id']}` (`{item['resource_type']}`) rendered item length: {item['length_chars']} characters"
            )
    else:
        lines.append("- None detected by the batching heuristic.")
    lines.extend(
        [
            "",
            "## Scope Reminder",
            "- these reviewer batches are for demo-only workflow validation",
            "- they are not formal real-data MIMIC/eICU pairs",
            "- they must not be treated as part of the formal mother pool",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Package the existing demo pair pilot into reviewer-ready batch files."""

    manifest_rows = load_manifest()
    pairs = load_pairs_jsonl(PAIR_JSONL_PATH)
    validate_pair_csv(PAIR_CSV_PATH, pairs)
    if not pairs:
        raise SystemExit(f"No demo pair candidates found at {PAIR_JSONL_PATH}")
    if not PAIR_SUMMARY_PATH.exists():
        raise SystemExit(f"Missing demo pair summary at {PAIR_SUMMARY_PATH}")

    prior_outcome = read_outcome(PAIR_NEXT_STEP_PATH)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    ROOT_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    for existing_prompt in PROMPT_DIR.glob("review_batch_*.txt"):
        existing_prompt.unlink()
    for existing_prompt in ROOT_PROMPT_DIR.glob("review_batch_*.txt"):
        existing_prompt.unlink()

    batches = chunked(pairs, BATCH_SIZE)
    batch_index_rows = []
    batch_manifest_rows = []
    all_item_stats = []
    seen_pair_ids = []

    for batch_number, batch_pairs in enumerate(batches, start=1):
        batch_id = f"review_batch_{batch_number:03d}"
        file_name = f"{batch_id}.txt"
        prompt_text, item_stats = build_prompt(batch_pairs)
        (PROMPT_DIR / file_name).write_text(prompt_text, encoding="utf-8")
        (ROOT_PROMPT_DIR / file_name).write_text(prompt_text, encoding="utf-8")
        batch_index_rows.append(
            {
                "batch_id": batch_id,
                "file_name": file_name,
                "start_pair_id": batch_pairs[0]["pair_id"],
                "end_pair_id": batch_pairs[-1]["pair_id"],
                "item_count": len(batch_pairs),
            }
        )
        batch_manifest_rows.append(
            {
                "batch_id": batch_id,
                "file_name": file_name,
                "item_count": len(batch_pairs),
                "pair_ids": [pair["pair_id"] for pair in batch_pairs],
            }
        )
        all_item_stats.extend(item_stats)
        seen_pair_ids.extend(pair["pair_id"] for pair in batch_pairs)

    if seen_pair_ids != [pair["pair_id"] for pair in pairs]:
        raise SystemExit("Pair batching mismatch: not all pairs were packaged exactly once.")

    write_csv(INDEX_PATH, batch_index_rows, INDEX_FIELDNAMES)
    write_jsonl(MANIFEST_PATH, batch_manifest_rows)
    write_summary(
        SUMMARY_PATH,
        manifest_rows,
        total_pairs=len(pairs),
        batches=batches,
        long_items=unusual_long_items(all_item_stats),
        prior_outcome=prior_outcome,
    )

    print(f"Run mode: {run_mode_label(manifest_rows)}")
    print(f"Read demo pairs from {PAIR_JSONL_PATH}")
    print(f"Packaged pairs: {len(pairs)}")
    print(f"Batches created: {len(batches)}")
    print(f"Wrote prompts to {PROMPT_DIR}")
    print(f"Mirrored prompts to {ROOT_PROMPT_DIR}")
    print(f"Wrote batch index to {INDEX_PATH}")
    print(f"Wrote batch manifest to {MANIFEST_PATH}")
    print(f"Wrote batching summary to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
