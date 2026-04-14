# Pilot Shortlist Summary

## Run mode
- Overall run mode: demo
- MIMIC-IV labevents -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/labevents.csv
- MIMIC-IV chartevents -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/chartevents.csv
- MIMIC-IV patients -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/patients.csv
- MIMIC-IV diagnoses_icd -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/mimic_iv/diagnoses_icd.csv
- eICU-CRD lab -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/lab.csv
- eICU-CRD vitalperiodic -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/vitalperiodic.csv
- eICU-CRD patient -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/patient.csv
- eICU-CRD diagnosis -> demo-equivalent -> /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/demo/eicu_crd/diagnosis.csv

## Source warnings
- Credentialed source missing for MIMIC-IV labevents at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/labevents.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for MIMIC-IV chartevents at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/chartevents.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for MIMIC-IV patients at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/patients.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for MIMIC-IV diagnoses_icd at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/mimic_iv/diagnoses_icd.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD lab at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/lab.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD vitalperiodic at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/vitalperiodic.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD patient at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/patient.csv. Using existing demo-equivalent fallback.
- Credentialed source missing for eICU-CRD diagnosis at /Users/dongfang/Desktop/MIMIC:eICU /FHIR-mimic-eicu-seeds/data/raw/eicu_crd/diagnosis.csv. Using existing demo-equivalent fallback.

## Shortlist size and mix
- Shortlist size: 9
- Resource mix: 7 Observation, 1 Patient, 1 Condition
- Mix justification: Observation dominates because standalone numeric measurements remain the safest path for early human review; Patient and Condition stay deliberately sparse.

## Shortlist entries
- 1. `eicu-obs-0001` | Observation | glucose 188 mg/dL | keep | high
- 2. `mimic-obs-0003` | Observation | Na 134 mEq/L | keep | high
- 3. `eicu-obs-0006` | Observation | HR 118 bpm | keep | high
- 4. `eicu-obs-0007` | Observation | SBP 86 mmHg | keep | high
- 5. `eicu-obs-0009` | Observation | Temp 38.4 C | keep | high
- 6. `eicu-obs-0002` | Observation | K 5.4 mmol/L | keep | high
- 7. `eicu-obs-0010` | Observation | SpO2 91 % | keep | high
- 8. `eicu-pat-0001` | Patient | 71F | maybe | low
- 9. `eicu-cond-0001` | Condition | Dx: atrial fibrillation | maybe | medium

## Main exclusion buckets
- duplicate_or_redundant: 13
- weak_pairing_value: 9
- needs_too_much_context: 2

## Manual review stance
- Good enough for the first manual review round: yes
- Recommended next action after review: freeze a keep-only subset, confirm conservative FHIR paths and units, and only then design later-stage pair templates outside this step.
