# FHIR-mimic-eicu-seeds

Independent MIMIC-IV / eICU-CRD curation workflow for rough, observation-heavy FHIR seed candidates.

This repository is intentionally separate from any Synthea-derived, Official-derived, or NHANES-derived pipeline. The current scope stays conservative and covers:

- source profiling
- candidate extraction
- mapping preparation
- pilot-seed shortlist recommendation
- human-reviewable pilot shortlist preparation
- mapping review pack generation

It does not yet generate paired input variants, final paired samples, or dataset splits.

## Modeling stance

- Treat MIMIC-IV / eICU-CRD as realism sources, not backbone sources.
- Favor terse and semi-structured clinical measurement text.
- Prioritize Observation-like candidates first.
- Use Patient-like candidates sparingly.
- Use Condition-like candidates only when explicit and low-ambiguity.
- Avoid complex longitudinal composition in the first pass.

## Repository layout

```text
/
├── README.md
├── scripts/
│   ├── fetch_or_prepare_sources.py
│   ├── profile_mimic_eicu_tables.py
│   ├── build_candidate_catalog.py
│   ├── recommend_pilot.py
│   ├── build_shortlist.py
│   ├── build_mapping_review_pack.py
│   ├── consolidate_mapping_review.py
│   └── mimic_eicu_pipeline.py
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
    └── mimic_eicu/
        ├── source_counts_summary.csv
        ├── observation_profile_summary.csv
        ├── candidate_seed_catalog.csv
        ├── mimic_eicu_source_summary.md
        ├── pilot_shortlist.csv
        ├── exclusion_log.csv
        ├── pilot_shortlist_summary.md
        ├── pilot_mapping_review.csv
        ├── pilot_mapping_review_final.csv
        ├── pilot_mapping_review_approved.csv
        ├── pilot_mapping_review_maybe.csv
        ├── pilot_mapping_review_rejected.csv
        ├── pilot_mapping_review_decision_summary.md
        ├── pilot_mapping_review_next_step.md
        ├── reviewer_batch_prompt.md
        └── pilot_readiness_summary.md
```

## Data access modes

The workflow supports two source modes:

1. Credentialed extracts placed under:
   - `data/raw/mimic_iv/`
   - `data/raw/eicu_crd/`
2. Demo-equivalent schema-shaped tables written automatically under:
   - `data/raw/demo/mimic_iv/`
   - `data/raw/demo/eicu_crd/`

If credentialed access is not available yet, the demo-equivalent tables let you stand up profiling, candidate extraction, and pilot recommendation logic without mixing in non-MIMIC/eICU source families.

## Expected credentialed extract filenames

- `data/raw/mimic_iv/labevents.csv`
- `data/raw/mimic_iv/chartevents.csv`
- `data/raw/mimic_iv/patients.csv`
- `data/raw/mimic_iv/diagnoses_icd.csv`
- `data/raw/eicu_crd/lab.csv`
- `data/raw/eicu_crd/vitalperiodic.csv`
- `data/raw/eicu_crd/patient.csv`
- `data/raw/eicu_crd/diagnosis.csv`

The scripts automatically prefer those files when they exist. Otherwise they fall back to the demo-equivalent tables, record the exact selected file path in `data/processed/source_manifest.csv`, and emit clear warnings about missing credentialed inputs.

## Candidate catalog fields

Each candidate row records:

- `candidate_id`
- `source_dataset`
- `source_table`
- `source_column_or_measure`
- `patient_or_stay_id_if_available`
- `likely_fhir_resource`
- `candidate_text_snippet`
- `structured_value`
- `unit_if_available`
- `likely_numeric`
- `needs_linked_context`
- `complexity_guess`
- `good_for_pairing`
- `mapping_notes`
- `review_notes`

Each row is a candidate fragment, not a full patient case.

## Run the first pass

```bash
python3 scripts/fetch_or_prepare_sources.py
python3 scripts/profile_mimic_eicu_tables.py
python3 scripts/build_candidate_catalog.py
python3 scripts/recommend_pilot.py
python3 scripts/build_shortlist.py
python3 scripts/build_mapping_review_pack.py
python3 scripts/consolidate_mapping_review.py
```

All scripts use only the Python standard library.

## Output intent

- `source_counts_summary.csv`: table-level counts and rough candidate yield
- `candidate_seed_catalog.csv`: first-pass candidate pool
- `observation_profile_summary.csv`: observation-heavy profiling summary
- `mimic_eicu_source_summary.md`: conservative pilot recommendation and source interpretation
- `pilot_shortlist.csv`: manual-review shortlist with keep/maybe/drop status
- `exclusion_log.csv`: explicit reasons for rows that did not make the shortlist
- `pilot_shortlist_summary.md`: reviewer-facing shortlist overview
- `pilot_mapping_review.csv`: conservative FHIR mapping review table
- `pilot_mapping_review_final.csv`: finalized mapping decisions with approved/maybe_later/rejected status
- `pilot_mapping_review_approved.csv`: rows safe enough for a later tiny pilot discussion
- `pilot_mapping_review_maybe.csv`: rows held back for later clarification
- `pilot_mapping_review_rejected.csv`: rows rejected for the current tiny pilot decision
- `pilot_mapping_review_decision_summary.md`: go/no-go summary for the reviewed mapping table
- `pilot_mapping_review_next_step.md`: single explicit next-step outcome
- `reviewer_batch_prompt.md`: reviewer instructions and output schema
- `pilot_readiness_summary.md`: readiness call and next step after review

## Not in scope yet

- paired input variant generation
- final paired sample construction
- train/validation/test assignment
- full MIMIC/eICU quota targeting
