"""
JIT Skill Definitions for Data Extraction
These are injected at runtime when the model calls get_rob_skill()
"""

# =============================================================================
# RoB 2 Skill (for RCTs)
# =============================================================================

ROB2_SKILL = """
## Risk of Bias 2 (RoB 2) Assessment Instructions

You are now assessing Risk of Bias for a **Randomized Controlled Trial** using the Cochrane RoB 2 tool.

### Assessment Domains

**Domain 1: Randomization Process**
Assess whether the allocation sequence was random and concealed.
- Signaling questions:
  1. Was the allocation sequence random? (Look for: computer-generated, random number table)
  2. Was the allocation sequence concealed? (Look for: sealed opaque envelopes, central allocation, pharmacy-controlled)
  3. Were there baseline differences that suggest a problem with randomization?
- Judgment: Low risk / Some concerns / High risk

**Domain 2: Deviations from Intended Interventions**
Assess whether there were deviations from intended interventions due to the trial context.
- Signaling questions:
  1. Were participants aware of their assigned intervention?
  2. Were carers/personnel aware of the assigned intervention?
  3. Were there deviations from intended interventions that arose because of the trial context?
  4. Were these deviations likely to have affected the outcome?
  5. Was an appropriate analysis used to estimate the effect of assignment?
- Judgment: Low risk / Some concerns / High risk

**Domain 3: Missing Outcome Data**
Assess whether outcome data were available for all or nearly all participants randomized.
- Signaling questions:
  1. Were data available for all or nearly all participants randomized?
  2. Is there evidence that the result was not biased by missing outcome data?
  3. Could missingness depend on the true value of the outcome?
- Judgment: Low risk / Some concerns / High risk

**Domain 4: Measurement of the Outcome**
Assess whether the method of outcome measurement was inappropriate or differed between groups.
- Signaling questions:
  1. Was the method of measuring the outcome inappropriate?
  2. Could measurement or ascertainment differ between intervention groups?
  3. Were outcome assessors aware of intervention received?
  4. Could assessment of the outcome have been influenced by knowledge of intervention?
- Judgment: Low risk / Some concerns / High risk

**Domain 5: Selection of the Reported Result**
Assess whether multiple outcome measurements, analyses, or time points could lead to selective reporting.
- Signaling questions:
  1. Were the data that produced this result analyzed in accordance with a pre-specified analysis plan?
  2. Is the numerical result being assessed likely to have been selected from multiple outcome measurements?
  3. Is the numerical result being assessed likely to have been selected from multiple analyses?
- Judgment: Low risk / Some concerns / High risk

### Overall Judgment Algorithm
- **Low risk**: Low risk in ALL domains
- **Some concerns**: Some concerns in at least one domain, but no high risk
- **High risk**: High risk in at least one domain, OR some concerns in multiple domains that substantially lower confidence

### Instructions
1. For each domain, provide:
   - judgment: Your risk level assessment
   - rationale: Detailed explanation with page/table references
   - support_quotes: Direct quotes from the paper

2. Consider the specific outcome being assessed (primary: NAS/EAD)

3. When finished, call submit_extraction() with complete data including rob_rct field.
"""


# =============================================================================
# ROBINS-I Skill (for NRS)
# =============================================================================

ROBINS_I_SKILL = """
## ROBINS-I Assessment Instructions

You are now assessing Risk of Bias for a **Non-Randomized Study** using the ROBINS-I tool.

### Assessment Domains

**Domain 1: Bias due to Confounding**
- Key confounders in liver transplant MP studies: donor age, DRI, MELD, CIT
- Look for: propensity score matching, multivariable regression, IPTW
- Judgment: Low / Moderate / Serious / Critical / No information

**Domain 2: Bias in Selection of Participants**
- Was selection into the study related to intervention AND outcome?
- Look for: exclusion of participants after intervention started
- Judgment: Low / Moderate / Serious / Critical / No information

**Domain 3: Bias in Classification of Interventions**
- Was intervention status well-defined and determined prospectively?
- Could classification of intervention status be affected by knowledge of the outcome?
- Judgment: Low / Moderate / Serious / Critical / No information

**Domain 4: Bias due to Deviations from Intended Interventions**
- Were there co-interventions that differed between groups?
- Did switches between groups occur?
- Judgment: Low / Moderate / Serious / Critical / No information

**Domain 5: Bias due to Missing Data**
- Were outcome data available for all or nearly all participants?
- Was there differential loss to follow-up?
- Judgment: Low / Moderate / Serious / Critical / No information

**Domain 6: Bias in Measurement of Outcomes**
- Could outcome measurement have differed between groups?
- Were outcome assessors aware of intervention status?
- Judgment: Low / Moderate / Serious / Critical / No information

**Domain 7: Bias in Selection of the Reported Result**
- Is there evidence of selective outcome reporting?
- Were multiple analyses performed?
- Judgment: Low / Moderate / Serious / Critical / No information

### Overall Judgment Algorithm
- **Low risk**: Comparable to a well-performed RCT for this domain
- **Moderate risk**: Sound for an observational study but not RCT
- **Serious risk**: Some important problems
- **Critical risk**: Too problematic to provide useful evidence
- Use the HIGHEST risk across all domains for overall judgment

### Instructions
1. For each domain, provide:
   - judgment: Your risk level assessment
   - rationale: Detailed explanation with references
   - support_quotes: Direct quotes from the paper

2. Pay particular attention to:
   - Matching method and variables used
   - Residual confounding potential
   - Center effects in single-center studies

3. When finished, call submit_extraction() with complete data including rob_nrs field.
"""


# =============================================================================
# Skill Registry
# =============================================================================

SKILL_REGISTRY = {
    "RCT": ROB2_SKILL,
    "NRS": ROBINS_I_SKILL,
}


def get_skill(study_type: str) -> str:
    """Get the appropriate skill based on study type."""
    return SKILL_REGISTRY.get(study_type, ROBINS_I_SKILL)
