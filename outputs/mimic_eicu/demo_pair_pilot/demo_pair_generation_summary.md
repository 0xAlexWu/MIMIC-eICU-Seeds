# Demo Pair Generation Summary

- run_mode: `demo`
- approved_rows_existed: `no`
- fallback_to_maybe_used: `yes`
- prior_formal_next_step: `collect_real_credentialed_data_first`
- final_source_items_retained: `7`
- final_pair_count: `14`
- source_item_composition: `7 Observation, 0 Patient, 0 Condition`
- pair_composition_by_resource: `14 Observation, 0 Patient, 0 Condition`
- pair_composition_by_input_style: `concise_clinical: 7, semi_structured: 7`

## Excluded At Pair Stage
- `eicu-pat-0001`: Patient fragment remains too sparse for a demo-only pair pilot.
- `eicu-cond-0001`: Condition coding remains too uncertain for a demo-only pair pilot.

## Why This Is Demo-Only
- every retained row comes from demo-equivalent MIMIC-IV or eICU-backed workflow outputs
- no approved reviewed rows existed, so this pilot relies on conservative Observation-only fallback from `maybe_later`
- coding remains intentionally minimal or text-only where the reviewed mapping never confirmed a source code
- subject and encounter references were not fabricated from terse snippets
- this tiny set is for workflow validation only and is not suitable for mother-pool inclusion

## External AI Review Readiness
- good enough for a small external AI review focused on workflow validation only
