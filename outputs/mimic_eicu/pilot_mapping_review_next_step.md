outcome: collect_real_credentialed_data_first
reason: demo-mode evidence is not sufficient for a trustworthy MIMIC/eICU pair pilot, especially when reviewer approvals are absent or unresolved.
required_before_any_pair_generation:
- load credentialed MIMIC-IV / eICU extracts into data/raw/mimic_iv/ and data/raw/eicu_crd/
- enter explicit reviewer keep/maybe/drop decisions in pilot_mapping_review.csv
- confirm unit and coding clarity on the strongest Observation rows
