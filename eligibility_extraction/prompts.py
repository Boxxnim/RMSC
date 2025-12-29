"""
Prompt templates for systematic review data extraction
"""

SYSTEM_PROMPT = """You are a systematic review data extraction specialist for transplantation medicine.

Your task is to extract structured data from research papers for a systematic review and network meta-analysis on ex vivo machine perfusion in extended criteria donor (ECD) liver transplantation.

## PICO Criteria

**Population**: Adult liver transplant recipients receiving grafts from:
- Extended criteria donors (ECD)
- Donation after circulatory death (DCD) donors
- High donor risk index (DRI) grafts

**Intervention**: 
- Hypothermic oxygenated perfusion (HOPE) - single or dual cannulation
- Normothermic machine perfusion (NMP)

**Comparator**: Static cold storage (SCS)

**Outcomes** (primary):
- Early allograft dysfunction (EAD) - Olthoff criteria
- Non-anastomotic biliary stricture (NAS)
- Total biliary complications (TBC)
- Acute cellular rejection (ACR)
- Primary non-function (PNF)
- Graft survival
- Patient survival

## Eligibility Criteria

**Include**:
- RCTs and matched non-randomized studies
- Comparing HOPE or NMP with SCS
- Adult liver transplantation
- ECD or DCD donor population (or subgroup data available)

**Exclude**:
- Studies with additional co-interventions that alter the intervention (e.g., tPA during perfusion)
- Viability-guided selection that changes graft pool (e.g., FMN-based discard criteria)
- Combined/sequential perfusion techniques (e.g., HOPE followed by NMP)
- Multi-organ transplants
- Pediatric recipients
- Non-comparative studies
- Studies where ECD/DCD outcomes cannot be extracted separately

## Key Flags to Watch For

1. **Co-interventions**: Any therapeutic agents added during perfusion (tPA, defatting cocktails, stem cells)
2. **Selection changes**: Viability criteria that lead to different utilization rates between groups
3. **Technique variations**: Deviations from standard HOPE or NMP protocols
4. **Overlapping cohorts**: Same institution + overlapping time periods = potential duplicate patients

Always be conservative - when in doubt, flag for manual review rather than making assumptions."""


EXTRACTION_PROMPT_TEMPLATE = """## Task
Extract structured data from the following study for systematic review inclusion.

## Study Information
{paper_content}

## Instructions
1. Extract all relevant fields according to the schema
2. Assess eligibility based on PICO criteria
3. Flag any concerns about co-interventions, selection bias, or overlapping cohorts
4. If information is not explicitly stated, use "Not specified" rather than inferring

## Important Definitions

**ECD (Extended Criteria Donor)**: Donors with factors associated with increased graft failure risk:
- Age ≥60, or age ≥50 with ≥2 of: CVA as cause of death, hypertension, creatinine >1.5
- DCD donors are generally considered ECD

**EAD (Early Allograft Dysfunction)**: Olthoff criteria - any of:
- Bilirubin ≥10 mg/dL on POD7
- INR ≥1.6 on POD7  
- ALT or AST >2000 IU/L within first 7 days

**NAS (Non-anastomotic Biliary Stricture)**: Biliary strictures not at surgical anastomosis site, typically >1cm from anastomosis

## Output Format
Respond with valid JSON matching this structure:

```json
{{
  "registry_data": {{
    "study_id": "string - format: INTERVENTION_CENTER_YEAR",
    "first_author": "string",
    "year": integer,
    "title": "string",
    "journal": "string",
    "doi": "string",
    "study_design": "RCT|Prospective Cohort|Retrospective Cohort|Matched Cohort|Registry Study",
    "centers": ["list of center codes"],
    "countries": ["ISO country codes"],
    "enrollment_period": "YYYY-MM/YYYY-MM",
    "registry_id": "NCT number if available",
    "sample_size": {{
      "total": integer,
      "intervention": integer,
      "control": integer
    }},
    "intervention_type": "HOPE|D-HOPE|NMP|etc",
    "comparator_type": "SCS|etc",
    "donor_type": ["DCD", "DBD", "ECD"],
    "co_interventions": ["list any additional interventions"],
    "viability_criteria": "description of viability assessment",
    "perfusion_timing": "End-ischemic|Continuous|Back-to-base|In-transit",
    "outcomes_reported": ["EAD", "NAS", etc],
    "ecd_definition": "how ECD was defined",
    "notes": "any additional relevant information"
  }},
  "eligibility": {{
    "decision": "Include|Exclude|Pending|Sensitivity only",
    "exclusion_category": "category if excluded",
    "rationale": "detailed explanation",
    "pico_violation": "Population|Intervention|Comparator|Outcome|Multiple|None",
    "precedent": "reference to guideline or similar decision",
    "concerns": [
      {{
        "concern_type": "type of concern",
        "detail": "specific detail",
        "severity": "Minor|Moderate|Major"
      }}
    ],
    "confidence": "High|Medium|Low"
  }},
  "potential_overlaps": [
    {{
      "related_study": "study ID or author/year",
      "relationship_type": "same cohort|same center|post-hoc analysis|etc",
      "evidence": "why you suspect overlap"
    }}
  ]
}}
```

Extract the data now:"""


VALIDATION_PROMPT_TEMPLATE = """## Task
Validate the following data extraction for accuracy and completeness.

## Original Study Summary
{paper_summary}

## Extracted Data
{extracted_json}

## Validation Checklist

1. **Factual Accuracy**: Do extracted values match the source?
2. **Completeness**: Are all available fields populated?
3. **Eligibility Decision**: Is the decision justified by the rationale?
4. **PICO Alignment**: Does the study actually match our criteria?
5. **Red Flags**: Were all co-interventions and selection issues identified?

## Known Problematic Patterns to Check

- tPA, alteplase, or thrombolytic therapy during perfusion → Exclude (Co-intervention)
- FMN-guided, viability-based discard decisions → Exclude (Viability-guided selection)
- Different utilization rates between groups suggesting selection → Flag for review
- Same institution appearing in multiple studies → Check for overlap

## Output Format

```json
{{
  "validation_status": "Confirmed|Needs revision|Major concerns",
  "accuracy_issues": [
    {{
      "field": "field name",
      "extracted_value": "what was extracted",
      "correct_value": "what it should be",
      "source": "where in paper this is found"
    }}
  ],
  "missing_information": ["list of fields that could be filled but weren't"],
  "eligibility_agreement": true|false,
  "eligibility_concerns": "explanation if disagreement",
  "additional_red_flags": ["any concerns the first extraction missed"],
  "final_recommendation": "Accept extraction|Revise extraction|Manual review required",
  "confidence": "High|Medium|Low"
}}
```

Validate now:"""


OVERLAP_CHECK_PROMPT_TEMPLATE = """## Task
Assess potential patient overlap between studies for meta-analysis.

## Study A
{study_a_summary}

## Study B  
{study_b_summary}

## Overlap Assessment Criteria

**High probability of overlap** if:
- Same institution(s)
- Overlapping enrollment periods
- Similar sample sizes with same intervention
- Same registry/trial ID
- Shared authorship + same center

**Check for**:
- Post-hoc analyses of RCTs
- Extended follow-up publications
- Subgroup publications from larger cohorts
- Registry studies that may include patients from single-center studies

## Output Format

```json
{{
  "study_id_a": "string",
  "study_id_b": "string", 
  "overlap_type": "Confirmed Duplicate|Likely Overlap|Subset|No Overlap|Unknown",
  "overlap_evidence": "detailed explanation",
  "shared_elements": {{
    "centers": ["overlapping centers"],
    "enrollment_overlap": "description of time overlap",
    "registry_id": "shared registry if any",
    "author_overlap": ["shared authors"]
  }},
  "estimated_overlap_percent": integer (0-100),
  "resolution_recommendation": "Use A only|Use B only|Outcome-specific|Pending author contact",
  "resolution_rationale": "why this resolution",
  "confidence": "High|Medium|Low"
}}
```

Assess overlap now:"""
