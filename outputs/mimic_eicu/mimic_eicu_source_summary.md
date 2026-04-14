# MIMIC/eICU Source Summary

## Datasets and tables used
- MIMIC-IV tables: labevents, chartevents, patients, diagnoses_icd
- eICU-CRD tables: lab, vitalperiodic, patient, diagnosis

## Source files used
- MIMIC-IV labevents -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/labevents.csv
- MIMIC-IV chartevents -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/chartevents.csv
- MIMIC-IV patients -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/patients.csv
- MIMIC-IV diagnoses_icd -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/diagnoses_icd.csv
- eICU-CRD lab -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/lab.csv
- eICU-CRD vitalperiodic -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/vitalperiodic.csv
- eICU-CRD patient -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/patient.csv
- eICU-CRD diagnosis -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/diagnosis.csv

## Access mode
- Credentialed data used: no
- Demo-equivalent data used: yes
- Overall run mode: demo
- Interpretation: the workflow stays runnable in demo mode but prefers credentialed extracts whenever they are present.

## Source warnings
- Credentialed source missing for MIMIC-IV labevents at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/labevents.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for MIMIC-IV chartevents at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/chartevents.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for MIMIC-IV patients at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/patients.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for MIMIC-IV diagnoses_icd at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/diagnoses_icd.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD lab at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/lab.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD vitalperiodic at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/vitalperiodic.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD patient at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/patient.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD diagnosis at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/diagnosis.csv. Using existing demo-equivalent fallback.

## Candidate counts
- Observation-like candidates: 25
- Patient-like candidates: 5
- Condition-like candidates: 3

## Pilot suitability
- Suitable for a small pilot: yes
- Why: Observation-like numeric snippets dominate, units are usually present, and the fragments preserve terse charting character without needing multi-event reconstruction.

## Source interpretation
- Best interpreted as a realism source rather than a backbone source: yes
- Why: these fragments contribute clinical roughness and realistic shorthand better than they provide broad, balanced backbone coverage.

## Compact preview shortlist
- Recommended preview size: 8 candidates
- Recommended preview mix: 6 Observation, 1 Patient, 1 Condition max
- `eicu-obs-0001` | Observation | glucose 188 mg/dL
- `mimic-obs-0003` | Observation | Na 134 mEq/L
- `eicu-obs-0006` | Observation | HR 118 bpm
- `eicu-obs-0007` | Observation | SBP 86 mmHg
- `eicu-obs-0009` | Observation | Temp 38.4 C
- `eicu-obs-0002` | Observation | K 5.4 mmol/L
- `eicu-pat-0001` | Patient | 71F
- `eicu-cond-0001` | Condition | Dx: atrial fibrillation

## Manual review shortlist stage
- Candidates surviving into the pilot shortlist: 9
- Shortlist composition: 7 Observation, 1 Patient, 1 Condition
- duplicate_or_redundant: 13
- weak_pairing_value: 9
- needs_too_much_context: 2
- Good enough for the first manual review round: yes
- Recommended next action after human review: freeze a keep-only subset and confirm conservative FHIR mapping choices before any later-stage pair drafting.
