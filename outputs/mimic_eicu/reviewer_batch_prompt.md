# Reviewer Batch Prompt

## Reviewer role
- Review each shortlisted MIMIC-IV / eICU-like candidate as a conservative clinical-data curator focused on early FHIR seed feasibility.

## Scope reminder
- This is NOT final pair generation.
- This is only shortlist + mapping review.
- Do not rewrite snippets into polished prose and do not infer hidden context that is not in the row.

## Review dimensions
- standalone usability
- FHIR mapping clarity
- unit clarity
- context sufficiency
- realism value
- pairing suitability

## Keep / Maybe / Drop framework
- `keep`: standalone, low-ambiguity, realistic, and conservatively mappable without hidden inference.
- `maybe`: promising but needs light expert judgment on mapping, unit handling, or residual context dependence.
- `drop`: too context-dependent, too ambiguous, or too weak to justify the first manual review pack.

## Specific cautions
- Context dependency: do not rescue rows that need linked encounter or trend context to make sense.
- Unit ambiguity: if the measurement meaning changes materially without unit confirmation, flag it.
- Condition ambiguity: only explicit diagnosis/problem wording should survive.
- Over-polishing risk: preserve terse chart-like character rather than rewriting it into synthetic prose.
- Hidden inference: if the mapping depends on guessed code systems, guessed chronology, or guessed patient state, mark it down.

## Reviewer JSON output schema
```json
{
  "candidate_id": "string",
  "decision": "keep | maybe | drop",
  "likely_fhir_resource": "Observation | Patient | Condition",
  "mapping_confidence": "high | medium | low",
  "main_issue": "string",
  "short_rationale": "string"
}
```
