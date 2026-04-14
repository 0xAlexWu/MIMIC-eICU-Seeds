"""Shared helpers for the MIMIC/eICU seed curation workflow."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = REPO_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = REPO_ROOT / "data" / "processed"
OUTPUT_DIR = REPO_ROOT / "outputs" / "mimic_eicu"

MANIFEST_PATH = DATA_PROCESSED_DIR / "source_manifest.csv"
SOURCE_COUNTS_PATH = OUTPUT_DIR / "source_counts_summary.csv"
CANDIDATE_CATALOG_PATH = OUTPUT_DIR / "candidate_seed_catalog.csv"
OBSERVATION_PROFILE_PATH = OUTPUT_DIR / "observation_profile_summary.csv"
SOURCE_SUMMARY_PATH = OUTPUT_DIR / "mimic_eicu_source_summary.md"
PILOT_SHORTLIST_PATH = OUTPUT_DIR / "pilot_shortlist.csv"
EXCLUSION_LOG_PATH = OUTPUT_DIR / "exclusion_log.csv"
PILOT_SHORTLIST_SUMMARY_PATH = OUTPUT_DIR / "pilot_shortlist_summary.md"
PILOT_MAPPING_REVIEW_PATH = OUTPUT_DIR / "pilot_mapping_review.csv"
REVIEWER_BATCH_PROMPT_PATH = OUTPUT_DIR / "reviewer_batch_prompt.md"
PILOT_READINESS_SUMMARY_PATH = OUTPUT_DIR / "pilot_readiness_summary.md"
PILOT_MAPPING_REVIEW_FINAL_PATH = OUTPUT_DIR / "pilot_mapping_review_final.csv"
PILOT_MAPPING_REVIEW_APPROVED_PATH = OUTPUT_DIR / "pilot_mapping_review_approved.csv"
PILOT_MAPPING_REVIEW_MAYBE_PATH = OUTPUT_DIR / "pilot_mapping_review_maybe.csv"
PILOT_MAPPING_REVIEW_REJECTED_PATH = OUTPUT_DIR / "pilot_mapping_review_rejected.csv"
PILOT_MAPPING_REVIEW_DECISION_SUMMARY_PATH = OUTPUT_DIR / "pilot_mapping_review_decision_summary.md"
PILOT_MAPPING_REVIEW_NEXT_STEP_PATH = OUTPUT_DIR / "pilot_mapping_review_next_step.md"

SHORTLIST_TARGET_SIZE = 9
MAX_PATIENT_SHORTLIST = 1
MAX_CONDITION_SHORTLIST = 1


SOURCE_SPECS = [
    {
        "source_dataset": "MIMIC-IV",
        "source_table": "labevents",
        "table_role": "observation",
        "credentialed_path": DATA_RAW_DIR / "mimic_iv" / "labevents.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "mimic_iv" / "labevents.csv",
        "id_field": "subject_id",
        "notes": "Observation-heavy lab table with simple numeric valueQuantity candidates.",
    },
    {
        "source_dataset": "MIMIC-IV",
        "source_table": "chartevents",
        "table_role": "observation",
        "credentialed_path": DATA_RAW_DIR / "mimic_iv" / "chartevents.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "mimic_iv" / "chartevents.csv",
        "id_field": "stay_id",
        "notes": "Bedside vital and charted measurement fragments suitable for rough Observation text.",
    },
    {
        "source_dataset": "MIMIC-IV",
        "source_table": "patients",
        "table_role": "patient",
        "credentialed_path": DATA_RAW_DIR / "mimic_iv" / "patients.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "mimic_iv" / "patients.csv",
        "id_field": "subject_id",
        "notes": "Use sparingly for simple age/sex demographic fragments only.",
    },
    {
        "source_dataset": "MIMIC-IV",
        "source_table": "diagnoses_icd",
        "table_role": "condition",
        "credentialed_path": DATA_RAW_DIR / "mimic_iv" / "diagnoses_icd.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "mimic_iv" / "diagnoses_icd.csv",
        "id_field": "subject_id",
        "notes": "Keep only explicit, low-ambiguity diagnosis strings in the first pass.",
    },
    {
        "source_dataset": "eICU-CRD",
        "source_table": "lab",
        "table_role": "observation",
        "credentialed_path": DATA_RAW_DIR / "eicu_crd" / "lab.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "eicu_crd" / "lab.csv",
        "id_field": "patientunitstayid",
        "notes": "Lab snippets remain useful when kept terse and numeric.",
    },
    {
        "source_dataset": "eICU-CRD",
        "source_table": "vitalperiodic",
        "table_role": "observation",
        "credentialed_path": DATA_RAW_DIR / "eicu_crd" / "vitalperiodic.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "eicu_crd" / "vitalperiodic.csv",
        "id_field": "patientunitstayid",
        "notes": "Single-row vital tables can yield multiple clean Observation-like fragments.",
    },
    {
        "source_dataset": "eICU-CRD",
        "source_table": "patient",
        "table_role": "patient",
        "credentialed_path": DATA_RAW_DIR / "eicu_crd" / "patient.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "eicu_crd" / "patient.csv",
        "id_field": "patientunitstayid",
        "notes": "Use only clean basic demographics and avoid over-specifying context.",
    },
    {
        "source_dataset": "eICU-CRD",
        "source_table": "diagnosis",
        "table_role": "condition",
        "credentialed_path": DATA_RAW_DIR / "eicu_crd" / "diagnosis.csv",
        "demo_path": DATA_RAW_DIR / "demo" / "eicu_crd" / "diagnosis.csv",
        "id_field": "patientunitstayid",
        "notes": "Only explicit diagnosis strings survive the conservative filter.",
    },
]


DEMO_ROWS = {
    ("MIMIC-IV", "labevents"): [
        {
            "subject_id": "100001",
            "hadm_id": "200001",
            "itemid": "51301",
            "label": "WBC",
            "valuenum": "13.2",
            "valueuom": "K/uL",
            "text_snippet": "WBC 13.2 K/uL",
        },
        {
            "subject_id": "100002",
            "hadm_id": "200002",
            "itemid": "51222",
            "label": "Hemoglobin",
            "valuenum": "9.8",
            "valueuom": "g/dL",
            "text_snippet": "Hgb 9.8 g/dL",
        },
        {
            "subject_id": "100003",
            "hadm_id": "200003",
            "itemid": "50983",
            "label": "Sodium",
            "valuenum": "134",
            "valueuom": "mEq/L",
            "text_snippet": "Na 134 mEq/L",
        },
        {
            "subject_id": "100004",
            "hadm_id": "200004",
            "itemid": "50813",
            "label": "Lactate",
            "valuenum": "2.1",
            "valueuom": "mmol/L",
            "text_snippet": "Lactate 2.1 mmol/L",
        },
        {
            "subject_id": "100005",
            "hadm_id": "200005",
            "itemid": "50912",
            "label": "Creatinine",
            "valuenum": "1.4",
            "valueuom": "mg/dL",
            "text_snippet": "Creat 1.4 mg/dL",
        },
    ],
    ("MIMIC-IV", "chartevents"): [
        {
            "subject_id": "100001",
            "stay_id": "300001",
            "itemid": "220045",
            "label": "Heart Rate",
            "valuenum": "104",
            "valueuom": "bpm",
            "text_snippet": "HR 104 bpm",
        },
        {
            "subject_id": "100001",
            "stay_id": "300001",
            "itemid": "220179",
            "label": "Systolic Blood Pressure",
            "valuenum": "92",
            "valueuom": "mmHg",
            "text_snippet": "SBP 92 mmHg",
        },
        {
            "subject_id": "100001",
            "stay_id": "300001",
            "itemid": "220180",
            "label": "Diastolic Blood Pressure",
            "valuenum": "58",
            "valueuom": "mmHg",
            "text_snippet": "DBP 58 mmHg",
        },
        {
            "subject_id": "100002",
            "stay_id": "300002",
            "itemid": "223761",
            "label": "Temperature",
            "valuenum": "38.1",
            "valueuom": "C",
            "text_snippet": "Temp 38.1 C",
        },
        {
            "subject_id": "100002",
            "stay_id": "300002",
            "itemid": "220210",
            "label": "Respiratory Rate",
            "valuenum": "24",
            "valueuom": "/min",
            "text_snippet": "RR 24 /min",
        },
    ],
    ("MIMIC-IV", "patients"): [
        {
            "subject_id": "100001",
            "anchor_age": "67",
            "gender": "F",
            "patient_snippet": "67F",
        },
        {
            "subject_id": "100003",
            "anchor_age": "54",
            "gender": "M",
            "patient_snippet": "54M",
        },
        {
            "subject_id": "100005",
            "anchor_age": "81",
            "gender": "F",
            "patient_snippet": "81F",
        },
    ],
    ("MIMIC-IV", "diagnoses_icd"): [
        {
            "subject_id": "100001",
            "hadm_id": "200001",
            "icd_code": "J18.9",
            "diagnosis_text": "Pneumonia",
            "diagnosis_snippet": "Dx: pneumonia",
            "explicit_low_ambiguity": "true",
        },
        {
            "subject_id": "100003",
            "hadm_id": "200003",
            "icd_code": "E11.9",
            "diagnosis_text": "Type 2 diabetes mellitus",
            "diagnosis_snippet": "Dx: type 2 diabetes mellitus",
            "explicit_low_ambiguity": "true",
        },
        {
            "subject_id": "100004",
            "hadm_id": "200004",
            "icd_code": "R41.82",
            "diagnosis_text": "Altered mental status",
            "diagnosis_snippet": "AMS",
            "explicit_low_ambiguity": "false",
        },
    ],
    ("eICU-CRD", "lab"): [
        {
            "patientunitstayid": "410001",
            "labname": "Glucose",
            "labresult": "188",
            "unit": "mg/dL",
            "text_snippet": "glucose 188 mg/dL",
        },
        {
            "patientunitstayid": "410001",
            "labname": "Potassium",
            "labresult": "5.4",
            "unit": "mmol/L",
            "text_snippet": "K 5.4 mmol/L",
        },
        {
            "patientunitstayid": "410002",
            "labname": "Platelets",
            "labresult": "142",
            "unit": "K/uL",
            "text_snippet": "plt 142 K/uL",
        },
        {
            "patientunitstayid": "410002",
            "labname": "Bicarbonate",
            "labresult": "19",
            "unit": "mmol/L",
            "text_snippet": "HCO3 19 mmol/L",
        },
        {
            "patientunitstayid": "410003",
            "labname": "Troponin I",
            "labresult": "0.08",
            "unit": "ng/mL",
            "text_snippet": "trop I 0.08 ng/mL",
        },
    ],
    ("eICU-CRD", "vitalperiodic"): [
        {
            "patientunitstayid": "410001",
            "heartrate": "118",
            "systemicsystolic": "86",
            "systemicdiastolic": "49",
            "temperature": "38.4",
            "spo2": "91",
        },
        {
            "patientunitstayid": "410002",
            "heartrate": "77",
            "systemicsystolic": "128",
            "systemicdiastolic": "72",
            "temperature": "36.7",
            "spo2": "98",
        },
    ],
    ("eICU-CRD", "patient"): [
        {
            "patientunitstayid": "410001",
            "age": "71",
            "gender": "F",
            "patient_snippet": "71F",
        },
        {
            "patientunitstayid": "410002",
            "age": "43",
            "gender": "M",
            "patient_snippet": "43M",
        },
    ],
    ("eICU-CRD", "diagnosis"): [
        {
            "patientunitstayid": "410001",
            "diagnosis_text": "Atrial fibrillation",
            "diagnosis_snippet": "Dx: atrial fibrillation",
            "explicit_low_ambiguity": "true",
        },
        {
            "patientunitstayid": "410003",
            "diagnosis_text": "Rule out stroke",
            "diagnosis_snippet": "r/o stroke",
            "explicit_low_ambiguity": "false",
        },
    ],
}


VITAL_PERIODIC_FIELDS = [
    ("heartrate", "Heart Rate", "bpm", "HR"),
    ("systemicsystolic", "Systolic Blood Pressure", "mmHg", "SBP"),
    ("systemicdiastolic", "Diastolic Blood Pressure", "mmHg", "DBP"),
    ("temperature", "Temperature", "C", "Temp"),
    ("spo2", "Oxygen Saturation", "%", "SpO2"),
]

MEASURE_NORMALIZATION = {
    "wbc": "wbc",
    "hgb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "na": "sodium",
    "sodium": "sodium",
    "k": "potassium",
    "potassium": "potassium",
    "lactate": "lactate",
    "creat": "creatinine",
    "creatinine": "creatinine",
    "heart rate": "heart_rate",
    "heartrate": "heart_rate",
    "hr": "heart_rate",
    "systolic blood pressure": "systolic_blood_pressure",
    "systemicsystolic": "systolic_blood_pressure",
    "sbp": "systolic_blood_pressure",
    "diastolic blood pressure": "diastolic_blood_pressure",
    "systemicdiastolic": "diastolic_blood_pressure",
    "dbp": "diastolic_blood_pressure",
    "temperature": "temperature",
    "temp": "temperature",
    "respiratory rate": "respiratory_rate",
    "rr": "respiratory_rate",
    "glucose": "glucose",
    "platelets": "platelets",
    "plt": "platelets",
    "bicarbonate": "bicarbonate",
    "hco3": "bicarbonate",
    "troponin i": "troponin_i",
    "trop i": "troponin_i",
    "oxygen saturation": "oxygen_saturation",
    "spo2": "oxygen_saturation",
}

MEASURE_DISPLAY = {
    "wbc": "WBC",
    "hemoglobin": "Hemoglobin",
    "sodium": "Sodium",
    "potassium": "Potassium",
    "lactate": "Lactate",
    "creatinine": "Creatinine",
    "heart_rate": "Heart Rate",
    "systolic_blood_pressure": "Systolic BP",
    "diastolic_blood_pressure": "Diastolic BP",
    "temperature": "Temperature",
    "respiratory_rate": "Respiratory Rate",
    "glucose": "Glucose",
    "platelets": "Platelets",
    "bicarbonate": "Bicarbonate",
    "troponin_i": "Troponin I",
    "oxygen_saturation": "SpO2",
    "patient_demographics": "Basic Demographics",
    "condition_explicit": "Explicit Diagnosis",
}

CLEAN_OBSERVATION_MEASURES = {
    "wbc",
    "hemoglobin",
    "sodium",
    "potassium",
    "lactate",
    "creatinine",
    "heart_rate",
    "systolic_blood_pressure",
    "temperature",
    "respiratory_rate",
    "glucose",
    "oxygen_saturation",
}

CONTEXT_HEAVY_MEASURES = {
    "troponin_i",
    "bicarbonate",
}

UNIT_SENSITIVE_MEASURES = CLEAN_OBSERVATION_MEASURES | {
    "diastolic_blood_pressure",
    "platelets",
    "troponin_i",
    "bicarbonate",
}

CONDITION_SHORTLIST_READY = {
    "pneumonia",
    "type 2 diabetes mellitus",
    "atrial fibrillation",
}

PREFERRED_OBSERVATION_ORDER = [
    "glucose",
    "sodium",
    "heart_rate",
    "systolic_blood_pressure",
    "temperature",
    "potassium",
    "oxygen_saturation",
    "respiratory_rate",
    "lactate",
    "creatinine",
    "wbc",
    "hemoglobin",
]

UCUM_MAP = {
    "mg/dL": "mg/dL",
    "g/dL": "g/dL",
    "mmol/L": "mmol/L",
    "mEq/L": "meq/L",
    "mmHg": "mm[Hg]",
    "C": "Cel",
    "%": "%",
    "/min": "/min",
    "bpm": "/min",
}

SHORTLIST_FIELDNAMES = [
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
]

EXCLUSION_FIELDNAMES = [
    "candidate_id",
    "source_dataset",
    "source_table",
    "likely_fhir_resource",
    "exclusion_reason",
    "exclusion_bucket",
]

MAPPING_REVIEW_FIELDNAMES = [
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
]

MAPPING_REVIEW_FINAL_FIELDNAMES = MAPPING_REVIEW_FIELDNAMES + [
    "final_status",
    "final_status_reason",
]


def ensure_directories() -> None:
    """Create the repository directories used by the pipeline."""

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_RAW_DIR / "mimic_iv").mkdir(parents=True, exist_ok=True)
    (DATA_RAW_DIR / "eicu_crd").mkdir(parents=True, exist_ok=True)
    (DATA_RAW_DIR / "demo" / "mimic_iv").mkdir(parents=True, exist_ok=True)
    (DATA_RAW_DIR / "demo" / "eicu_crd").mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """Write rows to a CSV file with deterministic field ordering."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_csv(path: Path) -> list[dict]:
    """Read a CSV file into a list of dictionaries."""

    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def looks_numeric(value: str) -> bool:
    """Return True when the value parses as a number."""

    if value is None:
        return False
    stripped = str(value).strip()
    if not stripped:
        return False
    try:
        float(stripped)
    except ValueError:
        return False
    return True


def truthy(value: str) -> bool:
    """Interpret simple string booleans."""

    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def bool_from_text(value: str) -> bool:
    """Interpret catalog booleans that were serialized as text."""

    return truthy(value)


def row_value(row: dict, *keys: str) -> str:
    """Return the first non-empty value found among the provided keys."""

    for key in keys:
        value = row.get(key, "")
        if value is None:
            continue
        if str(value).strip():
            return str(value).strip()
    return ""


def normalize_measure(label: str) -> str:
    """Normalize source measure labels into a stable comparison key."""

    cleaned = str(label).strip().lower()
    cleaned = cleaned.replace("-", " ").replace(":", " ")
    return MEASURE_NORMALIZATION.get(cleaned, cleaned.replace(" ", "_"))


def infer_measure_type(*texts: str) -> str:
    """Infer a stable measure key from source labels or snippets."""

    for text in texts:
        normalized = normalize_measure(text)
        if normalized in MEASURE_DISPLAY:
            return normalized
    snippet_hints = [
        ("sbp", "systolic_blood_pressure"),
        ("dbp", "diastolic_blood_pressure"),
        ("hr", "heart_rate"),
        ("rr", "respiratory_rate"),
        ("temp", "temperature"),
        ("spo2", "oxygen_saturation"),
        ("creat", "creatinine"),
        ("hgb", "hemoglobin"),
        ("plt", "platelets"),
        ("trop", "troponin_i"),
        ("hco3", "bicarbonate"),
        ("wbc", "wbc"),
        ("glucose", "glucose"),
        ("lactate", "lactate"),
    ]
    for text in texts:
        lower = str(text).strip().lower()
        for needle, measure in snippet_hints:
            if needle in lower:
                return measure
    fallback = str(texts[0]).strip() if texts else ""
    return normalize_measure(fallback) if fallback else "unknown_measure"


def display_measure(measure: str) -> str:
    """Return a user-facing display label for a normalized measure."""

    return MEASURE_DISPLAY.get(measure, measure.replace("_", " ").title())


def dataset_label(source_dataset: str, access_mode: str) -> str:
    """Attach demo labeling only when demo-equivalent data was used."""

    if access_mode == "credentialed":
        return source_dataset
    return f"{source_dataset} (demo-equivalent)"


def run_mode_label(manifest_rows: list[dict]) -> str:
    """Return a compact run-mode label for logging and summaries."""

    mode = manifest_run_mode(manifest_rows)
    if mode == "credentialed":
        return "credentialed"
    if mode == "mixed":
        return "mixed"
    return "demo"


def manifest_run_mode(manifest_rows: list[dict]) -> str:
    """Classify the current run as credentialed, demo, or mixed."""

    access_modes = {row["access_mode"] for row in manifest_rows}
    if access_modes == {"credentialed"}:
        return "credentialed"
    if access_modes == {"demo-equivalent"}:
        return "demo"
    return "mixed"


def source_warning_messages(manifest_rows: list[dict]) -> list[str]:
    """Collect source selection warnings from the manifest."""

    return [row["warning"] for row in manifest_rows if row.get("warning")]


def source_selection_lines(manifest_rows: list[dict]) -> list[str]:
    """Render source file selections in a readable deterministic order."""

    lines = []
    for row in manifest_rows:
        lines.append(
            f"{row['source_dataset']} {row['source_table']} -> {row['access_mode']} -> {row['file_path']}"
        )
    return lines


def condition_text_is_explicit_low_ambiguity(text: str) -> bool:
    """Apply a conservative filter to condition wording."""

    cleaned = str(text).strip().lower()
    if not cleaned:
        return False
    ambiguous_terms = [
        "?",
        "rule out",
        "r/o",
        "possible",
        "possible ",
        "history of",
        "hx of",
        "concern for",
        "suspected",
        "likely",
        "vs ",
        "unclear",
    ]
    return not any(term in cleaned for term in ambiguous_terms)


def measure_requires_unit(measure_type: str) -> bool:
    """Return True when unit presence matters to conservative review."""

    return measure_type in UNIT_SENSITIVE_MEASURES


def prepare_sources() -> list[dict]:
    """Create demo fallback sources when needed and persist a run manifest."""

    ensure_directories()
    manifest_rows = []
    for spec in SOURCE_SPECS:
        credentialed_path = spec["credentialed_path"]
        demo_path = spec["demo_path"]
        demo_created = False
        if credentialed_path.exists():
            selected_path = credentialed_path
            access_mode = "credentialed"
            warning = ""
        else:
            demo_rows = DEMO_ROWS[(spec["source_dataset"], spec["source_table"])]
            if not demo_path.exists():
                write_csv(demo_path, demo_rows, list(demo_rows[0].keys()))
                demo_created = True
            selected_path = demo_path
            access_mode = "demo-equivalent"
            created_note = " Created demo-equivalent fallback." if demo_created else " Using existing demo-equivalent fallback."
            warning = (
                f"Credentialed source missing for {spec['source_dataset']} {spec['source_table']} at "
                f"{credentialed_path}.{created_note}"
            )
        manifest_rows.append(
            {
                "source_dataset": spec["source_dataset"],
                "source_table": spec["source_table"],
                "table_role": spec["table_role"],
                "access_mode": access_mode,
                "file_path": str(selected_path),
                "expected_credentialed_path": str(credentialed_path),
                "demo_path": str(demo_path),
                "credentialed_file_present": str(credentialed_path.exists()).lower(),
                "demo_file_present": str(demo_path.exists()).lower(),
                "id_field": spec["id_field"],
                "warning": warning,
                "notes": spec["notes"],
            }
        )
    write_csv(
        MANIFEST_PATH,
        manifest_rows,
        [
            "source_dataset",
            "source_table",
            "table_role",
            "access_mode",
            "file_path",
            "expected_credentialed_path",
            "demo_path",
            "credentialed_file_present",
            "demo_file_present",
            "id_field",
            "warning",
            "notes",
        ],
    )
    return manifest_rows


def load_manifest() -> list[dict]:
    """Load the current source manifest, rebuilding it when absent."""

    if not MANIFEST_PATH.exists():
        return prepare_sources()
    manifest_rows = read_csv(MANIFEST_PATH)
    if manifest_rows:
        return manifest_rows
    return prepare_sources()


def build_observation_snippet(label: str, value: str, unit: str) -> str:
    """Build a terse clinical snippet when one is not provided."""

    parts = [str(label).strip(), str(value).strip()]
    if unit:
        parts.append(str(unit).strip())
    return " ".join(part for part in parts if part)


def observation_candidate(
    *,
    source: dict,
    source_column_or_measure: str,
    patient_or_stay_id: str,
    measure_label: str,
    snippet: str,
    structured_value: str,
    unit: str,
) -> dict:
    """Create an Observation-like candidate row."""

    measure_key = infer_measure_type(source_column_or_measure, measure_label, snippet)
    likely_numeric = looks_numeric(structured_value)
    needs_linked_context = (not unit and likely_numeric) or (measure_key in CONTEXT_HEAVY_MEASURES)
    complexity_guess = "medium" if needs_linked_context else "low"
    good_for_pairing = (
        likely_numeric and bool(unit) and measure_key in CLEAN_OBSERVATION_MEASURES and not needs_linked_context
    )
    review_notes = "Clean single-measure observation; good first-pass candidate."
    if needs_linked_context:
        review_notes = "Keep for realism profiling, but linked clinical context is still helpful."
    elif not good_for_pairing:
        review_notes = "Usable for profiling now; hold back from the pilot unless reviewers want more roughness."
    return {
        "candidate_id": "",
        "source_dataset": dataset_label(source["source_dataset"], source["access_mode"]),
        "source_table": source["source_table"],
        "source_column_or_measure": source_column_or_measure,
        "patient_or_stay_id_if_available": patient_or_stay_id,
        "likely_fhir_resource": "Observation",
        "candidate_text_snippet": snippet,
        "structured_value": structured_value,
        "unit_if_available": unit,
        "likely_numeric": str(likely_numeric).lower(),
        "needs_linked_context": str(needs_linked_context).lower(),
        "complexity_guess": complexity_guess,
        "good_for_pairing": str(good_for_pairing).lower(),
        "mapping_notes": "Observation.valueQuantity candidate; retain source label for later code mapping.",
        "review_notes": review_notes,
        "_measure_type": measure_key,
        "_pairing_score": str(int(good_for_pairing) * 4 + int(bool(unit)) + int(likely_numeric)),
    }


def patient_candidate(
    *,
    source: dict,
    patient_or_stay_id: str,
    snippet: str,
    age_value: str,
    gender_value: str,
) -> dict:
    """Create a simple Patient-like candidate row."""

    good_for_pairing = looks_numeric(age_value) and bool(gender_value)
    return {
        "candidate_id": "",
        "source_dataset": dataset_label(source["source_dataset"], source["access_mode"]),
        "source_table": source["source_table"],
        "source_column_or_measure": "basic_demographics",
        "patient_or_stay_id_if_available": patient_or_stay_id,
        "likely_fhir_resource": "Patient",
        "candidate_text_snippet": snippet,
        "structured_value": f"age={age_value}|gender={gender_value}",
        "unit_if_available": "",
        "likely_numeric": "false",
        "needs_linked_context": "false",
        "complexity_guess": "low",
        "good_for_pairing": str(good_for_pairing).lower(),
        "mapping_notes": "Patient demographic fragment only; avoid assuming more than age and sex.",
        "review_notes": "Use sparingly so Observation-like candidates remain dominant.",
        "_measure_type": "patient_demographics",
        "_pairing_score": str(2 if good_for_pairing else 0),
    }


def condition_candidate(
    *,
    source: dict,
    patient_or_stay_id: str,
    snippet: str,
    diagnosis_text: str,
) -> dict:
    """Create an explicit Condition-like candidate row."""

    diagnosis_key = diagnosis_text.strip().lower()
    good_for_pairing = diagnosis_key in CONDITION_SHORTLIST_READY
    return {
        "candidate_id": "",
        "source_dataset": dataset_label(source["source_dataset"], source["access_mode"]),
        "source_table": source["source_table"],
        "source_column_or_measure": "diagnosis_text",
        "patient_or_stay_id_if_available": patient_or_stay_id,
        "likely_fhir_resource": "Condition",
        "candidate_text_snippet": snippet,
        "structured_value": diagnosis_text,
        "unit_if_available": "",
        "likely_numeric": "false",
        "needs_linked_context": "false",
        "complexity_guess": "low",
        "good_for_pairing": str(good_for_pairing).lower(),
        "mapping_notes": "Condition.code candidate if the diagnosis string can be normalized later.",
        "review_notes": "Keep Condition-like use rare and limited to explicit diagnoses.",
        "_measure_type": "condition_explicit",
        "_pairing_score": str(2 if good_for_pairing else 1),
    }


def extract_candidates_for_source(source: dict) -> list[dict]:
    """Extract conservative first-pass candidates from a single source file."""

    rows = read_csv(Path(source["file_path"]))
    candidates = []
    dataset = source["source_dataset"]
    table = source["source_table"]

    if dataset == "MIMIC-IV" and table in {"labevents", "chartevents"}:
        for row in rows:
            label = row_value(row, "label", "item_label", "measure_name", "labname", "chart_label")
            value = row_value(row, "valuenum", "value", "labresult", "result")
            unit = row_value(row, "valueuom", "unit", "result_unit")
            patient_id = row_value(row, source["id_field"], "subject_id", "stay_id")
            if not label or not value or not patient_id:
                continue
            snippet = row_value(row, "text_snippet")
            if not snippet:
                snippet = build_observation_snippet(label, value, unit)
            candidates.append(
                observation_candidate(
                    source=source,
                    source_column_or_measure=label,
                    patient_or_stay_id=f"{source['id_field']}={patient_id}",
                    measure_label=label,
                    snippet=snippet,
                    structured_value=value,
                    unit=unit,
                )
            )
    elif dataset == "MIMIC-IV" and table == "patients":
        for row in rows:
            patient_id = row_value(row, source["id_field"], "subject_id")
            age_value = row_value(row, "anchor_age", "age")
            gender_value = row_value(row, "gender", "sex")
            if not patient_id or not age_value or not gender_value:
                continue
            snippet = row_value(row, "patient_snippet")
            if not snippet:
                snippet = f"{age_value}{gender_value}"
            candidates.append(
                patient_candidate(
                    source=source,
                    patient_or_stay_id=f"{source['id_field']}={patient_id}",
                    snippet=snippet,
                    age_value=age_value,
                    gender_value=gender_value,
                )
            )
    elif dataset == "MIMIC-IV" and table == "diagnoses_icd":
        for row in rows:
            patient_id = row_value(row, source["id_field"], "subject_id")
            diagnosis_text = row_value(row, "diagnosis_text", "long_title", "diagnosis", "diagnosisstring")
            if not patient_id or not diagnosis_text:
                continue
            explicit_flag = row_value(row, "explicit_low_ambiguity")
            if explicit_flag:
                if not truthy(explicit_flag):
                    continue
            elif not condition_text_is_explicit_low_ambiguity(diagnosis_text):
                continue
            snippet = row_value(row, "diagnosis_snippet")
            if not snippet:
                snippet = f"Dx: {diagnosis_text.lower()}"
            candidates.append(
                condition_candidate(
                    source=source,
                    patient_or_stay_id=f"{source['id_field']}={patient_id}",
                    snippet=snippet,
                    diagnosis_text=diagnosis_text,
                )
            )
    elif dataset == "eICU-CRD" and table == "lab":
        for row in rows:
            measure_label = row_value(row, "labname", "label", "measure_name")
            result_value = row_value(row, "labresult", "result", "valuenum", "labresulttext")
            unit = row_value(row, "unit", "labunit", "result_unit")
            patient_id = row_value(row, source["id_field"], "patientunitstayid")
            if not measure_label or not result_value or not patient_id:
                continue
            snippet = row_value(row, "text_snippet")
            if not snippet:
                snippet = build_observation_snippet(measure_label, result_value, unit)
            candidates.append(
                observation_candidate(
                    source=source,
                    source_column_or_measure=measure_label,
                    patient_or_stay_id=f"{source['id_field']}={patient_id}",
                    measure_label=measure_label,
                    snippet=snippet,
                    structured_value=result_value,
                    unit=unit,
                )
            )
    elif dataset == "eICU-CRD" and table == "vitalperiodic":
        for row in rows:
            patient_id = row_value(row, source["id_field"], "patientunitstayid")
            if not patient_id:
                continue
            for column_name, measure_label, unit, abbreviation in VITAL_PERIODIC_FIELDS:
                value = row_value(row, column_name)
                if not value:
                    continue
                snippet = f"{abbreviation} {value} {unit}"
                candidates.append(
                    observation_candidate(
                        source=source,
                        source_column_or_measure=column_name,
                        patient_or_stay_id=f"{source['id_field']}={patient_id}",
                        measure_label=measure_label,
                        snippet=snippet,
                        structured_value=value,
                        unit=unit,
                    )
                )
    elif dataset == "eICU-CRD" and table == "patient":
        for row in rows:
            patient_id = row_value(row, source["id_field"], "patientunitstayid")
            age_value = row_value(row, "age", "anchor_age")
            gender_value = row_value(row, "gender", "sex")
            if not patient_id or not age_value or not gender_value:
                continue
            snippet = row_value(row, "patient_snippet")
            if not snippet:
                snippet = f"{age_value}{gender_value}"
            candidates.append(
                patient_candidate(
                    source=source,
                    patient_or_stay_id=f"{source['id_field']}={patient_id}",
                    snippet=snippet,
                    age_value=age_value,
                    gender_value=gender_value,
                )
            )
    elif dataset == "eICU-CRD" and table == "diagnosis":
        for row in rows:
            patient_id = row_value(row, source["id_field"], "patientunitstayid")
            diagnosis_text = row_value(row, "diagnosis_text", "diagnosisstring", "diagnosis")
            if not patient_id or not diagnosis_text:
                continue
            explicit_flag = row_value(row, "explicit_low_ambiguity")
            if explicit_flag:
                if not truthy(explicit_flag):
                    continue
            elif not condition_text_is_explicit_low_ambiguity(diagnosis_text):
                continue
            snippet = row_value(row, "diagnosis_snippet")
            if not snippet:
                snippet = f"Dx: {diagnosis_text.lower()}"
            candidates.append(
                condition_candidate(
                    source=source,
                    patient_or_stay_id=f"{source['id_field']}={patient_id}",
                    snippet=snippet,
                    diagnosis_text=diagnosis_text,
                )
            )

    return candidates


def build_source_counts(manifest_rows: list[dict]) -> list[dict]:
    """Build table-level profiling counts from the selected sources."""

    summary_rows = []
    for source in manifest_rows:
        source_rows = read_csv(Path(source["file_path"]))
        candidates = extract_candidates_for_source(source)
        observation_like = sum(1 for candidate in candidates if candidate["likely_fhir_resource"] == "Observation")
        patient_like = sum(1 for candidate in candidates if candidate["likely_fhir_resource"] == "Patient")
        condition_like = sum(1 for candidate in candidates if candidate["likely_fhir_resource"] == "Condition")
        likely_numeric = sum(1 for candidate in candidates if candidate["likely_numeric"] == "true")
        with_units = sum(1 for candidate in candidates if candidate["unit_if_available"])
        summary_rows.append(
            {
                "source_dataset": source["source_dataset"],
                "source_table": source["source_table"],
                "access_mode": source["access_mode"],
                "selected_file_path": source["file_path"],
                "source_row_count": str(len(source_rows)),
                "candidate_count": str(len(candidates)),
                "observation_like_count": str(observation_like),
                "patient_like_count": str(patient_like),
                "condition_like_count": str(condition_like),
                "likely_numeric_count": str(likely_numeric),
                "with_units_count": str(with_units),
                "warning": source.get("warning", ""),
                "notes": source["notes"],
            }
        )
    return summary_rows


def assign_candidate_ids(candidates: list[dict]) -> list[dict]:
    """Assign deterministic candidate identifiers."""

    counters = Counter()
    for candidate in candidates:
        dataset_prefix = "mimic" if candidate["source_dataset"].startswith("MIMIC-IV") else "eicu"
        resource_prefix = {
            "Observation": "obs",
            "Patient": "pat",
            "Condition": "cond",
        }[candidate["likely_fhir_resource"]]
        key = (dataset_prefix, resource_prefix)
        counters[key] += 1
        candidate["candidate_id"] = f"{dataset_prefix}-{resource_prefix}-{counters[key]:04d}"
    return candidates


def build_candidate_catalog(manifest_rows: list[dict]) -> list[dict]:
    """Build the full candidate catalog from all selected sources."""

    all_candidates = []
    for source in manifest_rows:
        all_candidates.extend(extract_candidates_for_source(source))
    assign_candidate_ids(all_candidates)
    return all_candidates


def candidate_catalog_rows(candidates: list[dict]) -> list[dict]:
    """Drop internal helper fields before writing the candidate catalog."""

    fieldnames = [
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
    ]
    return [{field: candidate[field] for field in fieldnames} for candidate in candidates]


def write_candidate_catalog(candidates: list[dict]) -> None:
    """Write the candidate catalog to disk."""

    write_csv(
        CANDIDATE_CATALOG_PATH,
        candidate_catalog_rows(candidates),
        [
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
        ],
    )


def load_or_build_candidate_catalog() -> list[dict]:
    """Load the candidate catalog, creating it when it does not exist yet."""

    candidate_rows = read_csv(CANDIDATE_CATALOG_PATH)
    if candidate_rows:
        return candidate_rows
    manifest_rows = load_manifest()
    candidates = build_candidate_catalog(manifest_rows)
    write_candidate_catalog(candidates)
    return read_csv(CANDIDATE_CATALOG_PATH)


def build_observation_profile(candidates: list[dict]) -> list[dict]:
    """Summarize the observation-heavy part of the candidate pool."""

    observations = [candidate for candidate in candidates if candidate["likely_fhir_resource"] == "Observation"]
    likely_numeric = sum(1 for candidate in observations if candidate["likely_numeric"] == "true")
    with_units = sum(1 for candidate in observations if candidate["unit_if_available"])
    without_units = len(observations) - with_units
    top_clean = Counter(
        candidate["_measure_type"]
        for candidate in observations
        if candidate["good_for_pairing"] == "true"
    ).most_common(5)
    profile_rows = [
        {
            "metric": "total_observation_like_candidates",
            "value": str(len(observations)),
            "notes": "Observation-like fragments dominate the first-pass candidate pool.",
        },
        {
            "metric": "likely_numeric_observation_like_candidates",
            "value": str(likely_numeric),
            "notes": "Numeric snippets are preferred for conservative early pairing work.",
        },
        {
            "metric": "observation_candidates_with_units",
            "value": str(with_units),
            "notes": "Units improve direct Observation.valueQuantity mapping confidence.",
        },
        {
            "metric": "observation_candidates_without_units",
            "value": str(without_units),
            "notes": "These should usually stay out of the first pilot.",
        },
    ]
    for rank, (measure, count) in enumerate(top_clean, start=1):
        profile_rows.append(
            {
                "metric": f"top_clean_pairing_measure_type_{rank}",
                "value": display_measure(measure),
                "notes": f"{count} strong candidate(s)",
            }
        )
    return profile_rows


def score_candidate_for_pilot(candidate: dict) -> int:
    """Score candidates for the small preview shortlist used in the source summary."""

    base = int(
        candidate.get(
            "_pairing_score",
            int(bool_from_text(candidate.get("good_for_pairing", "false"))) * 4
            + int(bool(candidate.get("unit_if_available", "")))
            + int(bool_from_text(candidate.get("likely_numeric", "false"))),
        )
    )
    measure_type = candidate.get("_measure_type", candidate_measure_type(candidate))
    if candidate["likely_fhir_resource"] == "Observation":
        base += 2
        if measure_type in {
            "sodium",
            "glucose",
            "heart_rate",
            "systolic_blood_pressure",
            "temperature",
        }:
            base += 1
    elif candidate["likely_fhir_resource"] == "Patient":
        base -= 1
    elif candidate["likely_fhir_resource"] == "Condition":
        base -= 1
    return base


def recommend_pilot_shortlist(candidates: list[dict]) -> list[dict]:
    """Build the compact preview shortlist used by the source summary."""

    observations = sorted(
        [candidate for candidate in candidates if candidate["likely_fhir_resource"] == "Observation"],
        key=lambda candidate: (-score_candidate_for_pilot(candidate), candidate["candidate_id"]),
    )
    patients = sorted(
        [candidate for candidate in candidates if candidate["likely_fhir_resource"] == "Patient"],
        key=lambda candidate: (-score_candidate_for_pilot(candidate), candidate["candidate_id"]),
    )
    conditions = sorted(
        [candidate for candidate in candidates if candidate["likely_fhir_resource"] == "Condition"],
        key=lambda candidate: (-score_candidate_for_pilot(candidate), candidate["candidate_id"]),
    )

    shortlist = []
    selected_ids = set()
    for measure in PREFERRED_OBSERVATION_ORDER:
        for candidate in observations:
            candidate_measure = candidate.get("_measure_type", candidate_measure_type(candidate))
            if candidate_measure != measure or candidate["candidate_id"] in selected_ids:
                continue
            shortlist.append(candidate)
            selected_ids.add(candidate["candidate_id"])
            break
        if len(shortlist) == 6:
            break

    if patients:
        shortlist.append(patients[0])
    if conditions:
        shortlist.append(conditions[0])
    return shortlist[:8]


def counts_by_resource(rows: list[dict]) -> dict:
    """Count rows by their likely FHIR resource."""

    counter = Counter(row["likely_fhir_resource"] for row in rows)
    return {
        "Observation": counter.get("Observation", 0),
        "Patient": counter.get("Patient", 0),
        "Condition": counter.get("Condition", 0),
    }


def used_tables_by_dataset(manifest_rows: list[dict]) -> dict:
    """Group table names by dataset for human-readable summaries."""

    grouped = {"MIMIC-IV": [], "eICU-CRD": []}
    for source in manifest_rows:
        grouped[source["source_dataset"]].append(source["source_table"])
    return grouped


def credentialed_status(manifest_rows: list[dict]) -> tuple[bool, bool]:
    """Return booleans indicating whether credentialed or demo data was used."""

    uses_credentialed = any(source["access_mode"] == "credentialed" for source in manifest_rows)
    uses_demo = any(source["access_mode"] != "credentialed" for source in manifest_rows)
    return uses_credentialed, uses_demo


def candidate_measure_type(candidate: dict) -> str:
    """Infer the candidate measure from the exported catalog fields."""

    resource = candidate["likely_fhir_resource"]
    if resource == "Patient":
        return "patient_demographics"
    if resource == "Condition":
        return "condition_explicit"
    return infer_measure_type(
        candidate.get("source_column_or_measure", ""),
        candidate.get("candidate_text_snippet", ""),
    )


def shortlist_reason_for_candidate(candidate: dict, score: int) -> str:
    """Explain why a candidate was retained in the manual review shortlist."""

    resource = candidate["likely_fhir_resource"]
    measure_type = candidate_measure_type(candidate)
    if resource == "Observation":
        if score >= 145:
            return "Standalone numeric Observation with explicit unit and low context burden."
        return (
            f"Useful secondary {display_measure(measure_type)} Observation retained to broaden measure coverage "
            "without adding much context risk."
        )
    if resource == "Patient":
        return "Single sparse age/sex fragment retained to test minimal Patient handling without expanding scope."
    return "Explicit low-ambiguity diagnosis kept as the lone conservative Condition review item."


def reviewer_priority_for_candidate(candidate: dict, score: int) -> str:
    """Assign reviewer priority based on candidate strength and scope role."""

    resource = candidate["likely_fhir_resource"]
    if resource == "Observation" and score >= 145:
        return "high"
    if resource == "Observation":
        return "medium"
    if resource == "Condition":
        return "medium"
    return "low"


def provisional_status_for_candidate(candidate: dict, score: int) -> str:
    """Assign a provisional keep/maybe/drop label for manual review."""

    resource = candidate["likely_fhir_resource"]
    if resource == "Observation" and score >= 145:
        return "keep"
    if resource == "Observation" and score >= 130:
        return "maybe"
    if resource == "Condition":
        return "maybe"
    if resource == "Patient":
        return "maybe"
    return "drop"


def shortlist_candidate_score(candidate: dict) -> tuple[int, str, str]:
    """Score a candidate for the human-review shortlist and return any hard exclusion."""

    resource = candidate["likely_fhir_resource"]
    measure_type = candidate_measure_type(candidate)
    score = 0
    exclusion_reason = ""
    exclusion_bucket = ""

    likely_numeric = bool_from_text(candidate["likely_numeric"])
    needs_context = bool_from_text(candidate["needs_linked_context"])
    good_for_pairing = bool_from_text(candidate["good_for_pairing"])
    unit = candidate["unit_if_available"].strip()
    complexity = candidate["complexity_guess"].strip().lower()

    if resource == "Observation":
        score += 100
        if likely_numeric:
            score += 15
        if good_for_pairing:
            score += 25
        else:
            score -= 12
        if unit:
            score += 12
        elif measure_requires_unit(measure_type):
            exclusion_reason = "Missing unit for a unit-sensitive measurement."
            exclusion_bucket = "unit_ambiguity"
        if not exclusion_reason and needs_context:
            exclusion_reason = "Snippet needs linked clinical context to stand on its own."
            exclusion_bucket = "needs_too_much_context"
        if not exclusion_reason and complexity not in {"", "low"}:
            exclusion_reason = "Complexity exceeds the conservative first manual review threshold."
            exclusion_bucket = "too_complex"
        if measure_type in {"diastolic_blood_pressure", "platelets"}:
            score -= 10
        if measure_type in PREFERRED_OBSERVATION_ORDER[:7]:
            score += 5
    elif resource == "Patient":
        if candidate["source_column_or_measure"] != "basic_demographics" or "|" not in candidate["structured_value"]:
            exclusion_reason = "Patient fragment is not a simple age/sex demographic row."
            exclusion_bucket = "patient_not_clean_enough"
        score += 45
        if good_for_pairing:
            score += 5
    elif resource == "Condition":
        if not condition_text_is_explicit_low_ambiguity(candidate["structured_value"]):
            exclusion_reason = "Condition wording is not explicit enough for the conservative first pass."
            exclusion_bucket = "condition_too_ambiguous"
        score += 35
        if candidate["structured_value"].strip().lower() in CONDITION_SHORTLIST_READY:
            score += 5
    else:
        exclusion_reason = "Unsupported resource type for this shortlist stage."
        exclusion_bucket = "other"

    return score, exclusion_reason, exclusion_bucket


def observation_sort_key(candidate: dict, score: int) -> tuple[int, int, str]:
    """Create a deterministic ordering key for Observation shortlist selection."""

    measure_type = candidate_measure_type(candidate)
    measure_rank = PREFERRED_OBSERVATION_ORDER.index(measure_type) if measure_type in PREFERRED_OBSERVATION_ORDER else 999
    return (measure_rank, -score, candidate["candidate_id"])


def top_exclusion_counts(exclusion_rows: list[dict], topn: int = 5) -> list[tuple[str, int]]:
    """Return the most common exclusion buckets."""

    return Counter(row["exclusion_bucket"] for row in exclusion_rows).most_common(topn)


def build_shortlist_artifacts(candidate_rows: list[dict], target_size: int = SHORTLIST_TARGET_SIZE) -> tuple[list[dict], list[dict]]:
    """Build the manual-review shortlist and its exclusion log."""

    assessed_rows = []
    exclusion_rows = []

    for candidate in candidate_rows:
        score, exclusion_reason, exclusion_bucket = shortlist_candidate_score(candidate)
        enriched = dict(candidate)
        enriched["_measure_type"] = candidate_measure_type(candidate)
        enriched["_shortlist_score"] = score
        assessed_rows.append(enriched)
        if exclusion_bucket:
            exclusion_rows.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "source_dataset": candidate["source_dataset"],
                    "source_table": candidate["source_table"],
                    "likely_fhir_resource": candidate["likely_fhir_resource"],
                    "exclusion_reason": exclusion_reason,
                    "exclusion_bucket": exclusion_bucket,
                }
            )

    eligible = [row for row in assessed_rows if not any(row["candidate_id"] == excluded["candidate_id"] for excluded in exclusion_rows)]
    observations = sorted(
        [row for row in eligible if row["likely_fhir_resource"] == "Observation"],
        key=lambda row: observation_sort_key(row, row["_shortlist_score"]),
    )
    patients = sorted(
        [row for row in eligible if row["likely_fhir_resource"] == "Patient"],
        key=lambda row: (-row["_shortlist_score"], row["candidate_id"]),
    )
    conditions = sorted(
        [row for row in eligible if row["likely_fhir_resource"] == "Condition"],
        key=lambda row: (-row["_shortlist_score"], row["candidate_id"]),
    )

    selected = []
    selected_ids = set()
    seen_observation_measures = set()
    observation_target = min(max(target_size - MAX_PATIENT_SHORTLIST - MAX_CONDITION_SHORTLIST, 6), len(observations))

    for row in observations:
        if row["_measure_type"] in seen_observation_measures:
            continue
        selected.append(row)
        selected_ids.add(row["candidate_id"])
        seen_observation_measures.add(row["_measure_type"])
        if sum(1 for item in selected if item["likely_fhir_resource"] == "Observation") >= observation_target:
            break

    if patients and sum(1 for item in selected if item["likely_fhir_resource"] == "Patient") < MAX_PATIENT_SHORTLIST:
        selected.append(patients[0])
        selected_ids.add(patients[0]["candidate_id"])

    if conditions and sum(1 for item in selected if item["likely_fhir_resource"] == "Condition") < MAX_CONDITION_SHORTLIST:
        selected.append(conditions[0])
        selected_ids.add(conditions[0]["candidate_id"])

    fallback_pool = sorted(
        [row for row in eligible if row["candidate_id"] not in selected_ids],
        key=lambda row: (-row["_shortlist_score"], row["candidate_id"]),
    )
    while len(selected) < min(target_size, len(eligible)):
        if not fallback_pool:
            break
        next_row = fallback_pool.pop(0)
        resource = next_row["likely_fhir_resource"]
        if resource == "Patient" and sum(1 for item in selected if item["likely_fhir_resource"] == "Patient") >= MAX_PATIENT_SHORTLIST:
            continue
        if resource == "Condition" and sum(1 for item in selected if item["likely_fhir_resource"] == "Condition") >= MAX_CONDITION_SHORTLIST:
            continue
        selected.append(next_row)
        selected_ids.add(next_row["candidate_id"])

    shortlist_rows = []
    for rank, row in enumerate(selected, start=1):
        score = row["_shortlist_score"]
        shortlist_rows.append(
            {
                "shortlist_rank": str(rank),
                "candidate_id": row["candidate_id"],
                "source_dataset": row["source_dataset"],
                "source_table": row["source_table"],
                "source_column_or_measure": row["source_column_or_measure"],
                "patient_or_stay_id_if_available": row["patient_or_stay_id_if_available"],
                "likely_fhir_resource": row["likely_fhir_resource"],
                "candidate_text_snippet": row["candidate_text_snippet"],
                "structured_value": row["structured_value"],
                "unit_if_available": row["unit_if_available"],
                "likely_numeric": row["likely_numeric"],
                "needs_linked_context": row["needs_linked_context"],
                "complexity_guess": row["complexity_guess"],
                "good_for_pairing": row["good_for_pairing"],
                "mapping_notes": row["mapping_notes"],
                "review_notes": row["review_notes"],
                "shortlist_reason": shortlist_reason_for_candidate(row, score),
                "reviewer_priority": reviewer_priority_for_candidate(row, score),
                "provisional_status": provisional_status_for_candidate(row, score),
            }
        )

    selected_measure_types = {row["candidate_id"]: row["_measure_type"] for row in selected}
    shortlist_resources = counts_by_resource(shortlist_rows)
    for row in assessed_rows:
        if row["candidate_id"] in selected_ids or any(
            row["candidate_id"] == excluded["candidate_id"] for excluded in exclusion_rows
        ):
            continue
        resource = row["likely_fhir_resource"]
        if resource == "Observation":
            if row["_measure_type"] in seen_observation_measures:
                reason = "A higher-priority example of the same observation measure is already in the shortlist."
                bucket = "duplicate_or_redundant"
            elif not bool_from_text(row["good_for_pairing"]):
                reason = "Observation is usable for profiling but weak for the first manual pairing review round."
                bucket = "weak_pairing_value"
            else:
                reason = "Clean observation held out to keep the manual review pack compact and observation-led."
                bucket = "weak_pairing_value"
        elif resource == "Patient":
            reason = "Additional Patient-like demographic fragment held out to keep Patient coverage sparse."
            bucket = "duplicate_or_redundant"
        elif resource == "Condition":
            if shortlist_resources["Condition"] >= MAX_CONDITION_SHORTLIST:
                reason = "Additional explicit diagnosis held out so the first shortlist keeps Condition coverage rare."
                bucket = "duplicate_or_redundant"
            else:
                reason = "Condition candidate is explicit but lower priority for the first manual review round."
                bucket = "weak_pairing_value"
        else:
            reason = "Candidate is outside the current conservative shortlist rules."
            bucket = "other"
        exclusion_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "source_dataset": row["source_dataset"],
                "source_table": row["source_table"],
                "likely_fhir_resource": resource,
                "exclusion_reason": reason,
                "exclusion_bucket": bucket,
            }
        )

    exclusion_rows = sorted(
        exclusion_rows,
        key=lambda row: (row["exclusion_bucket"], row["candidate_id"]),
    )
    return shortlist_rows, exclusion_rows


def write_pilot_shortlist_summary(
    manifest_rows: list[dict],
    shortlist_rows: list[dict],
    exclusion_rows: list[dict],
) -> None:
    """Write a reviewer-facing summary of the manual shortlist."""

    shortlist_counts = counts_by_resource(shortlist_rows)
    exclusion_counts = top_exclusion_counts(exclusion_rows)
    warnings = source_warning_messages(manifest_rows)
    shortlist_lines = [
        (
            f"- {row['shortlist_rank']}. `{row['candidate_id']}` | {row['likely_fhir_resource']} | "
            f"{row['candidate_text_snippet']} | {row['provisional_status']} | {row['reviewer_priority']}"
        )
        for row in shortlist_rows
    ]
    exclusion_lines = [
        f"- {bucket}: {count}" for bucket, count in exclusion_counts
    ] or ["- none"]
    warning_lines = [f"- {warning}" for warning in warnings] or ["- none"]

    summary = "\n".join(
        [
            "# Pilot Shortlist Summary",
            "",
            "## Run mode",
            f"- Overall run mode: {run_mode_label(manifest_rows)}",
            *[f"- {line}" for line in source_selection_lines(manifest_rows)],
            "",
            "## Source warnings",
            *warning_lines,
            "",
            "## Shortlist size and mix",
            f"- Shortlist size: {len(shortlist_rows)}",
            (
                f"- Resource mix: {shortlist_counts['Observation']} Observation, "
                f"{shortlist_counts['Patient']} Patient, {shortlist_counts['Condition']} Condition"
            ),
            "- Mix justification: Observation dominates because standalone numeric measurements remain the safest path for early human review; Patient and Condition stay deliberately sparse.",
            "",
            "## Shortlist entries",
            *shortlist_lines,
            "",
            "## Main exclusion buckets",
            *exclusion_lines,
            "",
            "## Manual review stance",
            "- Good enough for the first manual review round: yes",
            "- Recommended next action after review: freeze a keep-only subset, confirm conservative FHIR paths and units, and only then design later-stage pair templates outside this step.",
        ]
    )
    PILOT_SHORTLIST_SUMMARY_PATH.write_text(summary + "\n", encoding="utf-8")


def write_pilot_readiness_summary(
    manifest_rows: list[dict],
    shortlist_rows: list[dict],
    exclusion_rows: list[dict],
) -> None:
    """Write a compact readiness summary for the current shortlist stage."""

    shortlist_counts = counts_by_resource(shortlist_rows)
    exclusion_counts = top_exclusion_counts(exclusion_rows)
    uses_credentialed, uses_demo = credentialed_status(manifest_rows)
    readiness = (
        len(shortlist_rows) >= 8
        and shortlist_counts["Observation"] >= 6
        and shortlist_counts["Patient"] <= 1
        and shortlist_counts["Condition"] <= 1
    )
    summary = "\n".join(
        [
            "# Pilot Readiness Summary",
            "",
            "## Data mode",
            f"- Credentialed data used: {'yes' if uses_credentialed else 'no'}",
            f"- Demo-equivalent data used: {'yes' if uses_demo else 'no'}",
            f"- Overall run mode: {run_mode_label(manifest_rows)}",
            "",
            "## Shortlist survival",
            f"- Candidates surviving into pilot shortlist: {len(shortlist_rows)}",
            (
                f"- Shortlist composition: {shortlist_counts['Observation']} Observation, "
                f"{shortlist_counts['Patient']} Patient, {shortlist_counts['Condition']} Condition"
            ),
            "",
            "## Main exclusions",
            *([f"- {bucket}: {count}" for bucket, count in exclusion_counts] or ["- none"]),
            "",
            "## Readiness call",
            f"- Good enough for the first manual review round: {'yes' if readiness else 'no'}",
            "- Why: the shortlist stays observation-heavy, avoids context-heavy rows, and keeps non-Observation items tightly limited.",
            "",
            "## Recommended next action",
            "- After human review, keep only the reviewer-approved rows, confirm conservative FHIR path and unit decisions, and postpone any pair construction to a later stage.",
        ]
    )
    PILOT_READINESS_SUMMARY_PATH.write_text(summary + "\n", encoding="utf-8")


def gender_code_from_structured_value(structured_value: str) -> tuple[str, str]:
    """Extract a simple FHIR administrative gender code from the structured fragment."""

    gender_raw = ""
    for part in structured_value.split("|"):
        if part.startswith("gender="):
            gender_raw = part.split("=", 1)[1].strip().upper()
            break
    if gender_raw == "F":
        return "female", "female"
    if gender_raw == "M":
        return "male", "male"
    return "", ""


def mapping_review_row(shortlist_row: dict) -> dict:
    """Create a conservative mapping-review row for a shortlisted candidate."""

    resource = shortlist_row["likely_fhir_resource"]
    measure_type = candidate_measure_type(shortlist_row)
    ambiguity_flags = []

    if resource == "Observation":
        proposed_fhir_path = "Observation.valueQuantity"
        proposed_value_type = "Quantity"
        proposed_code_system = ""
        proposed_code = ""
        proposed_display = display_measure(measure_type)
        proposed_unit = shortlist_row["unit_if_available"]
        ucum_unit = UCUM_MAP.get(proposed_unit, "")
        subject_required = "yes"
        encounter_required = "yes"
        if not ucum_unit and proposed_unit:
            ambiguity_flags.append("unit_review")
        ambiguity_flags.append("code_review")
    elif resource == "Patient":
        proposed_fhir_path = "Patient.gender"
        proposed_value_type = "code"
        proposed_code_system = "http://hl7.org/fhir/administrative-gender"
        proposed_code, proposed_display = gender_code_from_structured_value(shortlist_row["structured_value"])
        proposed_unit = ""
        ucum_unit = ""
        subject_required = "yes"
        encounter_required = "no"
        ambiguity_flags.append("age_fragment_not_directly_mapped")
        if not proposed_code:
            ambiguity_flags.append("gender_review")
    else:
        proposed_fhir_path = "Condition.code"
        proposed_value_type = "CodeableConcept"
        proposed_code_system = ""
        proposed_code = ""
        proposed_display = shortlist_row["structured_value"]
        proposed_unit = ""
        ucum_unit = ""
        subject_required = "yes"
        encounter_required = "yes"
        ambiguity_flags.append("code_review")

    if bool_from_text(shortlist_row["needs_linked_context"]):
        ambiguity_flags.append("context_review")

    return {
        "shortlist_rank": shortlist_row["shortlist_rank"],
        "candidate_id": shortlist_row["candidate_id"],
        "source_dataset": shortlist_row["source_dataset"],
        "source_table": shortlist_row["source_table"],
        "raw_measure_name": shortlist_row["source_column_or_measure"],
        "candidate_text_snippet": shortlist_row["candidate_text_snippet"],
        "likely_fhir_resource": shortlist_row["likely_fhir_resource"],
        "proposed_fhir_path": proposed_fhir_path,
        "proposed_value_type": proposed_value_type,
        "proposed_code_system": proposed_code_system,
        "proposed_code": proposed_code,
        "proposed_display": proposed_display,
        "proposed_unit": proposed_unit,
        "ucum_unit": ucum_unit,
        "subject_required": subject_required,
        "encounter_required": encounter_required,
        "needs_linked_context": shortlist_row["needs_linked_context"],
        "ambiguity_flag": ";".join(dict.fromkeys(ambiguity_flags)) if ambiguity_flags else "low",
        "reviewer_decision": "",
        "reviewer_comments": "",
    }


def build_mapping_review_rows(shortlist_rows: list[dict]) -> list[dict]:
    """Create the mapping review table from the manual shortlist."""

    return [mapping_review_row(row) for row in shortlist_rows]


def write_reviewer_batch_prompt() -> None:
    """Write the reviewer prompt used for manual shortlist and mapping checks."""

    prompt = "\n".join(
        [
            "# Reviewer Batch Prompt",
            "",
            "## Reviewer role",
            "- Review each shortlisted MIMIC-IV / eICU-like candidate as a conservative clinical-data curator focused on early FHIR seed feasibility.",
            "",
            "## Scope reminder",
            "- This is NOT final pair generation.",
            "- This is only shortlist + mapping review.",
            "- Do not rewrite snippets into polished prose and do not infer hidden context that is not in the row.",
            "",
            "## Review dimensions",
            "- standalone usability",
            "- FHIR mapping clarity",
            "- unit clarity",
            "- context sufficiency",
            "- realism value",
            "- pairing suitability",
            "",
            "## Keep / Maybe / Drop framework",
            "- `keep`: standalone, low-ambiguity, realistic, and conservatively mappable without hidden inference.",
            "- `maybe`: promising but needs light expert judgment on mapping, unit handling, or residual context dependence.",
            "- `drop`: too context-dependent, too ambiguous, or too weak to justify the first manual review pack.",
            "",
            "## Specific cautions",
            "- Context dependency: do not rescue rows that need linked encounter or trend context to make sense.",
            "- Unit ambiguity: if the measurement meaning changes materially without unit confirmation, flag it.",
            "- Condition ambiguity: only explicit diagnosis/problem wording should survive.",
            "- Over-polishing risk: preserve terse chart-like character rather than rewriting it into synthetic prose.",
            "- Hidden inference: if the mapping depends on guessed code systems, guessed chronology, or guessed patient state, mark it down.",
            "",
            "## Reviewer JSON output schema",
            "```json",
            "{",
            '  "candidate_id": "string",',
            '  "decision": "keep | maybe | drop",',
            '  "likely_fhir_resource": "Observation | Patient | Condition",',
            '  "mapping_confidence": "high | medium | low",',
            '  "main_issue": "string",',
            '  "short_rationale": "string"',
            "}",
            "```",
        ]
    )
    REVIEWER_BATCH_PROMPT_PATH.write_text(prompt + "\n", encoding="utf-8")


def normalize_reviewer_decision(value: str, comments: str = "") -> str:
    """Normalize reviewer decisions into keep, maybe, or drop."""

    lowered = str(value).strip().lower()
    comment_lower = str(comments).strip().lower()
    if lowered in {"keep", "kept", "approve", "approved", "accept", "accepted", "yes", "go"}:
        return "keep"
    if lowered in {"maybe", "hold", "later", "revisit", "unsure", "uncertain", "review"}:
        return "maybe"
    if lowered in {"drop", "reject", "rejected", "exclude", "remove", "no"}:
        return "drop"
    if "keep" in lowered or "approve" in lowered or "accept" in lowered:
        return "keep"
    if "drop" in lowered or "reject" in lowered or "exclude" in lowered or "remove" in lowered:
        return "drop"
    if "maybe" in lowered or "hold" in lowered or "revisit" in lowered:
        return "maybe"
    if not lowered and comment_lower:
        return "maybe"
    return "maybe"


def comment_supports_low_ambiguity(comments: str) -> bool:
    """Return True when reviewer comments clearly endorse low ambiguity."""

    lowered = str(comments).strip().lower()
    positive_terms = [
        "low ambiguity",
        "clear",
        "clean",
        "standalone",
        "good pairing",
        "strong pairing",
        "strong candidate",
        "unit clear",
        "mapping clear",
        "explicit",
        "looks good",
        "keep",
    ]
    return any(term in lowered for term in positive_terms)


def comment_indicates_concern(comments: str) -> bool:
    """Return True when reviewer comments flag ambiguity or risk."""

    lowered = str(comments).strip().lower()
    concern_terms = [
        "ambiguous",
        "unclear",
        "needs context",
        "context",
        "unit unclear",
        "hidden",
        "uncertain",
        "weak",
        "hold",
        "later",
        "not enough",
        "insufficient",
        "drop",
        "reject",
    ]
    return any(term in lowered for term in concern_terms)


def ambiguity_tokens(ambiguity_flag: str) -> set[str]:
    """Split the ambiguity flag field into stable tokens."""

    lowered = str(ambiguity_flag).strip().lower()
    if not lowered or lowered == "low":
        return set()
    return {token.strip() for token in lowered.split(";") if token.strip()}


def finalize_mapping_review_row(row: dict) -> dict:
    """Consolidate reviewer decisions into approved, maybe_later, or rejected."""

    normalized_decision = normalize_reviewer_decision(row.get("reviewer_decision", ""), row.get("reviewer_comments", ""))
    comments = row.get("reviewer_comments", "")
    resource = row["likely_fhir_resource"]
    ambiguity = ambiguity_tokens(row.get("ambiguity_flag", ""))
    needs_context = bool_from_text(row.get("needs_linked_context", "false"))
    measure_type = candidate_measure_type(
        {
            "likely_fhir_resource": resource,
            "source_column_or_measure": row.get("raw_measure_name", ""),
            "candidate_text_snippet": row.get("candidate_text_snippet", ""),
        }
    )
    unit_required = resource == "Observation" and measure_requires_unit(measure_type)
    unit_present = bool(str(row.get("proposed_unit", "")).strip())
    explicit_condition = resource != "Condition" or condition_text_is_explicit_low_ambiguity(row.get("proposed_display", ""))
    coding_confirmed = bool(str(row.get("proposed_code", "")).strip()) or bool(str(row.get("proposed_code_system", "")).strip())
    supportive_comment = comment_supports_low_ambiguity(comments)
    concern_comment = comment_indicates_concern(comments)

    final_status = "maybe_later"
    reason = "No explicit reviewer keep decision recorded; hold until the mapping review is completed."

    if normalized_decision == "drop":
        final_status = "rejected"
        reason = "Reviewer marked the row for exclusion."
    elif needs_context:
        final_status = "rejected"
        reason = "Hidden linked context is still required, so the row is too risky for a tiny pair pilot."
    elif unit_required and not unit_present:
        if normalized_decision == "keep":
            final_status = "maybe_later"
            reason = "Reviewer leaned keep, but unit clarity is still too weak for approval."
        else:
            final_status = "rejected"
            reason = "Unit-sensitive measurement lacks a trustworthy unit, so it cannot be approved."
    elif resource == "Observation":
        if "unit_review" in ambiguity:
            final_status = "maybe_later"
            reason = "Observation is promising but unit handling still needs expert confirmation."
        elif "code_review" in ambiguity and not supportive_comment:
            final_status = "maybe_later"
            reason = "Observation remains useful, but code-level mapping is still unresolved."
        elif normalized_decision == "keep" and not concern_comment:
            final_status = "approved"
            reason = "Reviewer keep decision aligns with a standalone low-ambiguity Observation candidate."
        elif normalized_decision == "maybe" and supportive_comment and not concern_comment:
            final_status = "approved"
            reason = "Reviewer left a maybe decision, but comments indicate low ambiguity and strong pairing value."
        else:
            final_status = "maybe_later"
            reason = "Observation stays usable for later review, but it is not yet clearly approved."
    elif resource == "Patient":
        if "age_fragment_not_directly_mapped" in ambiguity:
            final_status = "maybe_later"
            reason = "Patient fragment is simple, but only the gender component maps cleanly right now."
        elif normalized_decision == "keep" and not concern_comment:
            final_status = "approved"
            reason = "Reviewer keep decision supports a sparse low-ambiguity Patient fragment."
        else:
            final_status = "maybe_later"
            reason = "Patient row remains too sparse to approve without clearer reviewer support."
    elif resource == "Condition":
        if not explicit_condition:
            final_status = "rejected"
            reason = "Condition wording is not explicit enough for conservative approval."
        elif "code_review" in ambiguity and not coding_confirmed:
            final_status = "maybe_later"
            reason = "Condition is explicit, but coding remains too uncertain for approval."
        elif normalized_decision == "keep" and not concern_comment:
            final_status = "approved"
            reason = "Reviewer keep decision supports an explicit low-ambiguity Condition row."
        elif normalized_decision == "maybe" and supportive_comment and coding_confirmed:
            final_status = "approved"
            reason = "Reviewer comments support the Condition row and the code mapping is concrete enough."
        else:
            final_status = "maybe_later"
            reason = "Condition may be useful later, but explicit coding approval is still missing."

    finalized = dict(row)
    finalized["reviewer_decision"] = normalized_decision
    finalized["final_status"] = final_status
    finalized["final_status_reason"] = reason
    return finalized


def reason_bucket_for_finalized_row(row: dict) -> str:
    """Group final-status reasons for summary reporting."""

    reason = row["final_status_reason"].lower()
    if "reviewer marked" in reason:
        return "reviewer_drop"
    if "hidden linked context" in reason:
        return "hidden_context"
    if "unit" in reason:
        return "unit_clarity"
    if "code" in reason or "coding" in reason:
        return "coding_uncertainty"
    if "no explicit reviewer keep decision" in reason:
        return "missing_reviewer_decision"
    if "patient fragment" in reason:
        return "patient_sparse"
    if "condition" in reason:
        return "condition_not_confirmed"
    if "observation" in reason:
        return "observation_not_confirmed"
    return "other"


def build_mapping_review_decision_artifacts(mapping_rows: list[dict]) -> dict[str, list[dict]]:
    """Finalize mapping review decisions and split rows by final status."""

    finalized_rows = [finalize_mapping_review_row(row) for row in mapping_rows]
    approved_rows = [row for row in finalized_rows if row["final_status"] == "approved"]
    maybe_rows = [row for row in finalized_rows if row["final_status"] == "maybe_later"]
    rejected_rows = [row for row in finalized_rows if row["final_status"] == "rejected"]
    return {
        "finalized": finalized_rows,
        "approved": approved_rows,
        "maybe": maybe_rows,
        "rejected": rejected_rows,
    }


def resource_mix_string(rows: list[dict]) -> str:
    """Render a compact resource mix string."""

    counts = counts_by_resource(rows)
    return (
        f"{counts['Observation']} Observation, "
        f"{counts['Patient']} Patient, {counts['Condition']} Condition"
    )


def approved_subset_ready_for_tiny_pair_pilot(approved_rows: list[dict]) -> bool:
    """Return True when the approved subset is strong enough for a tiny later pilot."""

    counts = counts_by_resource(approved_rows)
    return (
        len(approved_rows) >= 4
        and counts["Observation"] >= 4
        and counts["Observation"] > (counts["Patient"] + counts["Condition"])
        and counts["Patient"] <= 1
        and counts["Condition"] <= 1
    )


def write_mapping_review_decision_summary(
    manifest_rows: list[dict],
    decision_rows: dict[str, list[dict]],
) -> None:
    """Write the markdown summary for finalized mapping review decisions."""

    finalized_rows = decision_rows["finalized"]
    approved_rows = decision_rows["approved"]
    maybe_rows = decision_rows["maybe"]
    rejected_rows = decision_rows["rejected"]
    approved_counts = counts_by_resource(approved_rows)
    approved_ready = approved_subset_ready_for_tiny_pair_pilot(approved_rows)
    rejection_counts = Counter(reason_bucket_for_finalized_row(row) for row in rejected_rows).most_common(5)
    maybe_counts = Counter(reason_bucket_for_finalized_row(row) for row in maybe_rows).most_common(5)
    recommended_size = min(len(approved_rows), 6) if approved_ready else 0
    summary = "\n".join(
        [
            "# Pilot Mapping Review Decision Summary",
            "",
            f"- Total reviewed rows: {len(finalized_rows)}",
            f"- Approved count: {len(approved_rows)}",
            f"- Maybe_later count: {len(maybe_rows)}",
            f"- Rejected count: {len(rejected_rows)}",
            f"- Final approved composition by likely_fhir_resource: {resource_mix_string(approved_rows)}",
            f"- Observation dominates the approved subset: {'yes' if approved_counts['Observation'] > (approved_counts['Patient'] + approved_counts['Condition']) and len(approved_rows) > 0 else 'no'}",
            "",
            "## Top rejection reasons",
            *([f"- {bucket}: {count}" for bucket, count in rejection_counts] or ["- none"]),
            "",
            "## Top maybe_later reasons",
            *([f"- {bucket}: {count}" for bucket, count in maybe_counts] or ["- none"]),
            "",
            "## Tiny pair-pilot readiness",
            f"- Strong enough for a later tiny pair-generation pilot: {'yes' if approved_ready else 'no'}",
            (
                f"- Recommended pilot size if later approved: {recommended_size}"
                if approved_ready
                else "- What must be fixed first: enter explicit reviewer decisions, resolve coding/unit ambiguity, and rerun on credentialed data before any pair generation begins."
            ),
            "",
            "## Run mode context",
            f"- Overall run mode: {run_mode_label(manifest_rows)}",
        ]
    )
    PILOT_MAPPING_REVIEW_DECISION_SUMMARY_PATH.write_text(summary + "\n", encoding="utf-8")


def write_mapping_review_next_step(
    manifest_rows: list[dict],
    decision_rows: dict[str, list[dict]],
) -> None:
    """Write the single-outcome operational next-step recommendation."""

    approved_rows = decision_rows["approved"]
    run_mode = run_mode_label(manifest_rows)
    approved_ready = approved_subset_ready_for_tiny_pair_pilot(approved_rows)
    if approved_ready and run_mode != "demo":
        outcome = "proceed_to_tiny_pair_pilot"
        body_lines = [
            f"outcome: {outcome}",
            f"maximum_recommended_pilot_size: {min(len(approved_rows), 6)}",
            f"recommended_resource_mix: {resource_mix_string(approved_rows)}",
            "strict_constraints:",
            "- keep Observation rows dominant",
            "- do not paraphrase or generate variants",
            "- do not expand beyond the approved subset",
            "- reject any row that later proves to need hidden context",
        ]
    elif run_mode == "demo":
        outcome = "collect_real_credentialed_data_first"
        body_lines = [
            f"outcome: {outcome}",
            "reason: demo-mode evidence is not sufficient for a trustworthy MIMIC/eICU pair pilot, especially when reviewer approvals are absent or unresolved.",
            "required_before_any_pair_generation:",
            "- load credentialed MIMIC-IV / eICU extracts into data/raw/mimic_iv/ and data/raw/eicu_crd/",
            "- enter explicit reviewer keep/maybe/drop decisions in pilot_mapping_review.csv",
            "- confirm unit and coding clarity on the strongest Observation rows",
        ]
    else:
        outcome = "stop_after_mapping_review"
        body_lines = [
            f"outcome: {outcome}",
            "reason: the approved subset is too weak or too ambiguous, so this source should remain a realism-only reference for now.",
        ]
    PILOT_MAPPING_REVIEW_NEXT_STEP_PATH.write_text("\n".join(body_lines) + "\n", encoding="utf-8")


def write_summary_markdown(
    manifest_rows: list[dict],
    candidates: list[dict],
    shortlist_rows: list[dict] | None = None,
    exclusion_rows: list[dict] | None = None,
) -> None:
    """Write the source summary, optionally extending it with shortlist details."""

    resource_counts = counts_by_resource(candidates)
    shortlist_preview = recommend_pilot_shortlist(candidates)
    used_tables = used_tables_by_dataset(manifest_rows)
    uses_credentialed, uses_demo = credentialed_status(manifest_rows)
    warnings = source_warning_messages(manifest_rows)

    shortlist_lines = [
        f"- `{candidate['candidate_id']}` | {candidate['likely_fhir_resource']} | {candidate['candidate_text_snippet']}"
        for candidate in shortlist_preview
    ]

    lines = [
        "# MIMIC/eICU Source Summary",
        "",
        "## Datasets and tables used",
        f"- MIMIC-IV tables: {', '.join(used_tables['MIMIC-IV'])}",
        f"- eICU-CRD tables: {', '.join(used_tables['eICU-CRD'])}",
        "",
        "## Source files used",
        *[f"- {line}" for line in source_selection_lines(manifest_rows)],
        "",
        "## Access mode",
        f"- Credentialed data used: {'yes' if uses_credentialed else 'no'}",
        f"- Demo-equivalent data used: {'yes' if uses_demo else 'no'}",
        f"- Overall run mode: {run_mode_label(manifest_rows)}",
        "- Interpretation: the workflow stays runnable in demo mode but prefers credentialed extracts whenever they are present.",
        "",
        "## Source warnings",
        *([f"- {warning}" for warning in warnings] or ["- none"]),
        "",
        "## Candidate counts",
        f"- Observation-like candidates: {resource_counts['Observation']}",
        f"- Patient-like candidates: {resource_counts['Patient']}",
        f"- Condition-like candidates: {resource_counts['Condition']}",
        "",
        "## Pilot suitability",
        "- Suitable for a small pilot: yes",
        "- Why: Observation-like numeric snippets dominate, units are usually present, and the fragments preserve terse charting character without needing multi-event reconstruction.",
        "",
        "## Source interpretation",
        "- Best interpreted as a realism source rather than a backbone source: yes",
        "- Why: these fragments contribute clinical roughness and realistic shorthand better than they provide broad, balanced backbone coverage.",
        "",
        "## Compact preview shortlist",
        "- Recommended preview size: 8 candidates",
        "- Recommended preview mix: 6 Observation, 1 Patient, 1 Condition max",
        *shortlist_lines,
    ]

    if shortlist_rows is not None and exclusion_rows is not None:
        shortlist_counts = counts_by_resource(shortlist_rows)
        exclusion_counts = top_exclusion_counts(exclusion_rows)
        lines.extend(
            [
                "",
                "## Manual review shortlist stage",
                f"- Candidates surviving into the pilot shortlist: {len(shortlist_rows)}",
                (
                    f"- Shortlist composition: {shortlist_counts['Observation']} Observation, "
                    f"{shortlist_counts['Patient']} Patient, {shortlist_counts['Condition']} Condition"
                ),
                *([f"- {bucket}: {count}" for bucket, count in exclusion_counts] or ["- none"]),
                "- Good enough for the first manual review round: yes",
                "- Recommended next action after human review: freeze a keep-only subset and confirm conservative FHIR mapping choices before any later-stage pair drafting.",
            ]
        )

    SOURCE_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
