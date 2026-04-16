# Clinical data to FHIR pairing evaluation
_Exported on 2026/4/16 at GMT+8 14:48:14 from Cursor (2.5.20)_

---

**User**

You are acting as an external reviewer in a clinical-data-to-FHIR pairing evaluation workflow.

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

ITEM 1
pair_id: demo-mimic-eicu-pair-0001
resource_type: Observation
input_style: concise_clinical
input_text:
glucose 188 mg/dL
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Glucose"
  },
  "valueQuantity": {
    "value": 188,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  }
}


ITEM 2
pair_id: demo-mimic-eicu-pair-0002
resource_type: Observation
input_style: semi_structured
input_text:
Glucose: 188 mg/dL
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Glucose"
  },
  "valueQuantity": {
    "value": 188,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  }
}


ITEM 3
pair_id: demo-mimic-eicu-pair-0003
resource_type: Observation
input_style: concise_clinical
input_text:
Na 134 mEq/L
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Sodium"
  },
  "valueQuantity": {
    "value": 134,
    "unit": "mEq/L",
    "system": "http://unitsofmeasure.org",
    "code": "meq/L"
  }
}


ITEM 4
pair_id: demo-mimic-eicu-pair-0004
resource_type: Observation
input_style: semi_structured
input_text:
Sodium: 134 mEq/L
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Sodium"
  },
  "valueQuantity": {
    "value": 134,
    "unit": "mEq/L",
    "system": "http://unitsofmeasure.org",
    "code": "meq/L"
  }
}


ITEM 5
pair_id: demo-mimic-eicu-pair-0005
resource_type: Observation
input_style: concise_clinical
input_text:
HR 118 bpm
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Heart Rate"
  },
  "valueQuantity": {
    "value": 118,
    "unit": "bpm",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  }
}


ITEM 6
pair_id: demo-mimic-eicu-pair-0006
resource_type: Observation
input_style: semi_structured
input_text:
Heart Rate: 118 bpm
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Heart Rate"
  },
  "valueQuantity": {
    "value": 118,
    "unit": "bpm",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  }
}


ITEM 7
pair_id: demo-mimic-eicu-pair-0007
resource_type: Observation
input_style: concise_clinical
input_text:
SBP 86 mmHg
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Systolic BP"
  },
  "valueQuantity": {
    "value": 86,
    "unit": "mmHg",
    "system": "http://unitsofmeasure.org",
    "code": "mm[Hg]"
  }
}


ITEM 8
pair_id: demo-mimic-eicu-pair-0008
resource_type: Observation
input_style: semi_structured
input_text:
Systolic BP: 86 mmHg
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Systolic BP"
  },
  "valueQuantity": {
    "value": 86,
    "unit": "mmHg",
    "system": "http://unitsofmeasure.org",
    "code": "mm[Hg]"
  }
}


ITEM 9
pair_id: demo-mimic-eicu-pair-0009
resource_type: Observation
input_style: concise_clinical
input_text:
Temp 38.4 C
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Temperature"
  },
  "valueQuantity": {
    "value": 38.4,
    "unit": "C",
    "system": "http://unitsofmeasure.org",
    "code": "Cel"
  }
}


ITEM 10
pair_id: demo-mimic-eicu-pair-0010
resource_type: Observation
input_style: semi_structured
input_text:
Temperature: 38.4 C
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Temperature"
  },
  "valueQuantity": {
    "value": 38.4,
    "unit": "C",
    "system": "http://unitsofmeasure.org",
    "code": "Cel"
  }
}



---

**Cursor**

[
  {
    "pair_id": "demo-mimic-eicu-pair-0001",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "Input shorthand accurately maps to Glucose value and unit in FHIR Observation",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0002",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Labeled semi-structured input perfectly aligns with FHIR Glucose Observation",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0003",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "Na abbreviation correctly expands to Sodium in target FHIR with matching value/unit",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0004",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Explicit Sodium label aligns fully with FHIR Observation details",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0005",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "Standard HR shorthand faithfully represented as Heart Rate in FHIR",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0006",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Clear Heart Rate label matches target FHIR structure and value",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0007",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "SBP clinical shorthand correctly maps to Systolic BP FHIR Observation",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0008",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Explicit Systolic BP input aligns precisely with target JSON",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0009",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "Temp abbreviation expands appropriately to Temperature FHIR resource",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0010",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Labeled Temperature input fully supported by target FHIR JSON",
    "flag_type": "none"
  }
]

---

**User**

You are acting as an external reviewer in a clinical-data-to-FHIR pairing evaluation workflow.

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

ITEM 1
pair_id: demo-mimic-eicu-pair-0011
resource_type: Observation
input_style: concise_clinical
input_text:
K 5.4 mmol/L
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Potassium"
  },
  "valueQuantity": {
    "value": 5.4,
    "unit": "mmol/L",
    "system": "http://unitsofmeasure.org",
    "code": "mmol/L"
  }
}


ITEM 2
pair_id: demo-mimic-eicu-pair-0012
resource_type: Observation
input_style: semi_structured
input_text:
Potassium: 5.4 mmol/L
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "Potassium"
  },
  "valueQuantity": {
    "value": 5.4,
    "unit": "mmol/L",
    "system": "http://unitsofmeasure.org",
    "code": "mmol/L"
  }
}


ITEM 3
pair_id: demo-mimic-eicu-pair-0013
resource_type: Observation
input_style: concise_clinical
input_text:
SpO2 91 %
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "SpO2"
  },
  "valueQuantity": {
    "value": 91,
    "unit": "%",
    "system": "http://unitsofmeasure.org",
    "code": "%"
  }
}


ITEM 4
pair_id: demo-mimic-eicu-pair-0014
resource_type: Observation
input_style: semi_structured
input_text:
SpO2: 91 %
target_fhir_json:
{
  "resourceType": "Observation",
  "code": {
    "text": "SpO2"
  },
  "valueQuantity": {
    "value": 91,
    "unit": "%",
    "system": "http://unitsofmeasure.org",
    "code": "%"
  }
}



---

**Cursor**

[
  {
    "pair_id": "demo-mimic-eicu-pair-0011",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "Standard K abbreviation accurately maps to Potassium value and unit in FHIR Observation",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0012",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Explicit Potassium label perfectly aligns with target FHIR Observation",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0013",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 4,
    "context_leakage": 0,
    "short_rationale": "Standard SpO2 clinical shorthand faithfully represented in target FHIR",
    "flag_type": "none"
  },
  {
    "pair_id": "demo-mimic-eicu-pair-0014",
    "faithfulness": 1,
    "unsupported_fact": 0,
    "omission": 0,
    "naturalness": 5,
    "context_leakage": 0,
    "short_rationale": "Explicit SpO2 label matches target FHIR structure, value and unit exactly",
    "flag_type": "none"
  }
]

