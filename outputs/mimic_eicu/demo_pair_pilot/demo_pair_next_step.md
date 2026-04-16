outcome: ready_for_demo_review
recommended_next_step: package these demo pairs for external AI review
scope_note: workflow validation only; do not treat these pairs as part of the formal MIMIC/eICU mother pool
maximum_recommended_pilot_size: 14 pairs from 7 source items
recommended_resource_mix: Observation 7, Patient 0, Condition 0
strict_constraints:
- keep the branch demo-only
- do not add paraphrased or stylized variants
- do not promote text-only coding into confident coded mappings
- do not infer subject, encounter, time, or diagnosis context that the shortlist does not explicitly support
