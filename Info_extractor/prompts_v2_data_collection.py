"""
Data Extraction Prompts for Machine Perfusion Systematic Review
목적: 메타분석용 데이터 + RoB 평가 정보 추출
"""

# =============================================================================
# MAIN EXTRACTION PROMPT
# =============================================================================

DATA_EXTRACTION_PROMPT = """You are a systematic review data extractor for liver transplantation machine perfusion studies.

## YOUR TASK
Extract ALL available data from this paper for meta-analysis. Do NOT make eligibility judgments - just collect data comprehensively. Missing data should be marked as null.

## STUDY CONTEXT
This systematic review compares:
- HOPE (Hypothermic Oxygenated Perfusion) vs SCS (Static Cold Storage)
- NMP (Normothermic Machine Perfusion) vs SCS
- In extended criteria donor (ECD) liver transplantation

## EXTRACTION INSTRUCTIONS

### 1. STUDY CHARACTERISTICS
Extract basic study information:
- First author, year, title, journal, DOI
- Study design (RCT, prospective cohort, retrospective cohort)
- Single/multicenter, country, enrollment period
- Registry ID (NCT number if available)
- Sample sizes for each arm
- Donor type (DCD, DBD, ECD-DBD, Mixed)
- Donor and recipient characteristics (age, BMI, MELD, DRI)
- For NRS: matching method and variables used

### 2. PERFUSION SETTINGS
Extract technical details:
- Device name (Liver Assist, OrganOx metra, OCS, etc.)
- Cannulation (Single PV only vs Dual PV+HA)
- Perfusate composition
- Temperature setting
- Oxygenation parameters
- **CO-INTERVENTIONS**: Any additives like tPA, defatting agents, stem cells (list all)
- Viability assessment: criteria used, discard rates

### 3. TIME METRICS
Extract timing data:
- Perfusion initiation point (donor hospital, transport, recipient hospital)
- Functional warm ischemia time (fWIT)
- Cold ischemia time (CIT)
- Perfusion duration
- Total preservation time
- Calculate perfusion-to-preservation ratio if possible

### 4. OUTCOME DATA
For each outcome, extract:
- Whether reported (true/false)
- Definition used (quote if available)
- Events and totals for intervention arm
- Events and totals for control arm
- Effect estimate (RR, OR, HR) with 95% CI and p-value if reported
- **source_quote**: Copy the exact sentence(s) from the paper containing this data
- **source_location**: Where in the paper (e.g., "Table 2", "Results p.5", "Figure 3")

**IMPORTANT: Every outcome with data MUST include source_quote and source_location for verification.**

**Outcomes to extract:**
- EAD (Early Allograft Dysfunction)
- NAS (Non-Anastomotic Biliary Stricture)
- TBC (Total Biliary Complications)
- Major complications (note: Clavien-Dindo ≥3 or ≥3b?)
- ACR (Acute Cellular Rejection)
- PNF (Primary Non-Function)
- HAT (Hepatic Artery Thrombosis)
- Retransplantation
- AKI (Acute Kidney Injury)
- RRT (Renal Replacement Therapy)
- PRS (Post-Reperfusion Syndrome)
- Hospital stay (days)
- ICU stay (days)
- 1-year graft survival
- 1-year patient survival

### 5. RISK OF BIAS INFORMATION
Do NOT judge risk of bias. Instead, extract INFORMATION that will help human reviewers make judgments.

**For RCTs, extract information about:**
- Randomization: How was it done? Computer-generated? Block/stratified?
- Allocation concealment: Sealed envelopes? Central allocation? Not mentioned?
- Blinding: Who was blinded? (participants, surgeons, outcome assessors)
- ITT analysis: Was intention-to-treat used? Any per-protocol analysis?
- Dropout/loss to follow-up: Numbers and reasons per arm
- Protocol registration: NCT number? Published protocol?
- Outcome reporting: Do reported outcomes match protocol?

**For Non-Randomized Studies, extract information about:**
- Confounding control: What variables were adjusted for? Method (PSM, regression)?
- Selection: How were groups formed? Any exclusions post-intervention?
- Co-interventions: Were they balanced between groups?
- Missing data: How much? How handled?
- Outcome assessment: Blinded? Objective measures?

**Always include direct quotes** from the paper that support these items.

### 6. NOTES
Flag any:
- Data quality concerns
- Items needing human verification
- Potential cohort overlaps with other studies (same center, overlapping dates)

## OUTPUT FORMAT
Return a JSON object with these sections:
{
  "study_characteristics": {...},
  "perfusion_settings": {...},
  "time_metrics": {...},
  "outcome_data": {...},
  "rob_information": {...},
  "extraction_notes": {...}
}

## PAPER CONTENT
<paper>
{{PAPER_CONTENT}}
</paper>

Extract all available data now. Use null for missing values."""


# =============================================================================
# RoB-SPECIFIC EXTRACTION PROMPT (더 자세한 RoB 정보 추출용)
# =============================================================================

ROB_EXTRACTION_PROMPT = """You are extracting Risk of Bias information for a systematic review.

## TASK
Extract INFORMATION and QUOTES that will help human reviewers assess risk of bias. 
Do NOT make final judgments - provide the evidence.

## STUDY TYPE: {{STUDY_TYPE}}  # "RCT" or "NRS"

{% if STUDY_TYPE == "RCT" %}
## FOR RANDOMIZED CONTROLLED TRIALS (RoB 2 Tool)

### Domain 1: Randomization Process
Search for and quote text about:
- Random sequence generation method
- Allocation concealment mechanism
- Any baseline imbalances between groups

### Domain 2: Deviations from Intended Interventions
Search for and quote text about:
- Blinding of participants and personnel
- Any protocol deviations mentioned
- Whether ITT or per-protocol analysis was used
- Crossovers between groups

### Domain 3: Missing Outcome Data
Search for and quote text about:
- Follow-up completion rates per arm
- Dropout numbers and reasons
- How missing data was handled
- Any sensitivity analyses for missing data

### Domain 4: Measurement of Outcome
Search for and quote text about:
- Outcome assessor blinding
- Outcome definitions used
- Whether outcomes are objective (lab values) or subjective
- Timing of outcome assessment

### Domain 5: Selection of Reported Result
Search for and quote text about:
- Pre-registration (NCT number, published protocol)
- Primary vs secondary outcomes specified
- Any evidence of multiple analyses
- Outcomes in protocol vs outcomes reported

{% else %}
## FOR NON-RANDOMIZED STUDIES (ROBINS-I Tool)

### Domain 1: Confounding
Search for and quote text about:
- Matching variables used
- Statistical adjustment methods (PSM, regression, IPTW)
- Variables controlled for
- Potential unmeasured confounders acknowledged

### Domain 2: Selection of Participants
Search for and quote text about:
- How intervention/control groups were selected
- Inclusion/exclusion criteria
- Whether selection could be related to outcome
- Start of follow-up relative to intervention

### Domain 3: Classification of Interventions
Search for and quote text about:
- How intervention status was determined
- Timing of classification (prospective vs retrospective)
- Potential for misclassification

### Domain 4: Deviations from Intended Interventions
Search for and quote text about:
- Co-interventions in each group
- Protocol adherence
- Switches between intervention groups

### Domain 5: Missing Data
Search for and quote text about:
- Completeness of outcome data
- Differential loss to follow-up
- Methods to handle missing data

### Domain 6: Measurement of Outcomes
Search for and quote text about:
- Outcome ascertainment methods
- Blinding of assessors
- Comparable measurement across groups

### Domain 7: Selection of Reported Result
Search for and quote text about:
- Pre-specified analysis plan
- Multiple outcomes or analyses mentioned
- Selective reporting concerns

{% endif %}

## OUTPUT FORMAT
```json
{
  "study_id": "FirstAuthor_Year",
  "study_type": "RCT" or "NRS",
  "rob_domains": {
    "domain_1": {
      "domain_name": "...",
      "extracted_information": "Summary of what was found",
      "supporting_quotes": [
        {"quote": "exact text from paper", "location": "section/page"},
        ...
      ],
      "missing_information": ["list of things not reported"]
    },
    ...
  },
  "overall_notes": "Any additional observations relevant to bias assessment"
}
```

## PAPER CONTENT
<paper>
{{PAPER_CONTENT}}
</paper>

Extract all risk of bias relevant information now."""


# =============================================================================
# OUTCOME-SPECIFIC EXTRACTION PROMPT (테이블에서 숫자 추출 집중)
# =============================================================================

OUTCOME_EXTRACTION_PROMPT = """You are extracting numerical outcome data for meta-analysis.

## TASK
Extract event counts and effect estimates for each outcome. Be precise with numbers.

## STUDY: {{STUDY_ID}}
## INTERVENTION: {{INTERVENTION}} (n={{N_INTERVENTION}})
## CONTROL: {{CONTROL}} (n={{N_CONTROL}})

## For each outcome, extract:

### Binary Outcomes Format:
- Events in intervention arm (numerator)
- Total in intervention arm (denominator) 
- Events in control arm (numerator)
- Total in control arm (denominator)
- Risk Ratio or Odds Ratio (if reported)
- 95% CI lower bound
- 95% CI upper bound
- P-value
- **source_quote**: Exact text from paper with the data
- **source_location**: Table/Figure/Page reference

### Continuous Outcomes Format:
- Mean or Median in intervention arm
- SD or IQR in intervention arm
- Mean or Median in control arm  
- SD or IQR in control arm
- Mean difference (if reported)
- 95% CI
- P-value
- **source_quote**: Exact text from paper with the data
- **source_location**: Table/Figure/Page reference

### Survival Outcomes Format:
- % survival at timepoint (intervention)
- % survival at timepoint (control)
- Events (deaths/graft losses) in intervention
- Events in control
- Hazard Ratio (if reported)
- 95% CI
- P-value
- **source_quote**: Exact text from paper with the data
- **source_location**: Table/Figure/Page reference

**CRITICAL: Every outcome MUST include source_quote and source_location for data verification.**

## OUTCOMES TO EXTRACT:

1. **EAD** (Early Allograft Dysfunction)
   - Definition used: ___
   
2. **NAS** (Non-Anastomotic Biliary Stricture)
   - Definition used: ___
   - Follow-up period for NAS: ___
   
3. **TBC** (Total Biliary Complications)
   - What's included: ___
   
4. **Major Complications**
   - Threshold: Clavien-Dindo ≥3 or ≥3b?
   
5. **ACR** (Acute Cellular Rejection)
   - Criteria: Biopsy-proven? Treated? Banff?
   - Timeframe: ___
   
6. **PNF** (Primary Non-Function)
   - Definition used: ___
   
7. **HAT** (Hepatic Artery Thrombosis)

8. **Retransplantation**
   - Timeframe: ___
   
9. **AKI** (Acute Kidney Injury)
   - Criteria: RIFLE? KDIGO? Grade?
   
10. **RRT** (Renal Replacement Therapy)

11. **PRS** (Post-Reperfusion Syndrome)
    - Definition used: ___

12. **Hospital Stay** (days)
    - Reported as mean or median?

13. **ICU Stay** (days)

14. **1-Year Graft Survival**

15. **1-Year Patient Survival**

## OUTPUT FORMAT
```json
{
  "study_id": "...",
  "outcomes": {
    "ead": {
      "reported": true/false,
      "definition": "...",
      "intervention_events": X,
      "intervention_total": X,
      "control_events": X,
      "control_total": X,
      "rr": X.XX,
      "ci_lower": X.XX,
      "ci_upper": X.XX,
      "p_value": X.XXX,
      "source_quote": "EAD occurred in 12/55 (21.8%) HOPE vs 24/55 (43.6%) SCS...",
      "source_location": "Table 2"
    },
    ...
  }
}
```

Use null for any values not reported. Do NOT calculate values not explicitly stated.

## PAPER CONTENT
<paper>
{{PAPER_CONTENT}}
</paper>

Extract all outcome data now."""


# =============================================================================
# QUICK SCREENING PROMPT (빠른 1차 확인용)
# =============================================================================

QUICK_SCREEN_PROMPT = """Quickly screen this paper for basic eligibility and data availability.

## QUESTIONS TO ANSWER:

1. **Study Design**: RCT, prospective cohort, retrospective cohort, case series, or other?

2. **Intervention**: What type of machine perfusion? (HOPE, NMP, HMP, other)

3. **Comparator**: What is the control group? (SCS, another perfusion type, none)

4. **Population**: 
   - Adult liver transplant?
   - Donor type (DCD, DBD, ECD)?
   - ECD percentage or subgroup available?

5. **Sample Size**: 
   - N in intervention arm?
   - N in control arm?
   - Is it matched?

6. **Co-interventions**: Any mentioned? (tPA, defatting, etc.)

7. **Outcomes Available**: Which of these are reported?
   □ EAD  □ NAS  □ TBC  □ Major complications
   □ ACR  □ PNF  □ HAT  □ Retransplantation
   □ AKI  □ RRT  □ Hospital stay  □ Survival

8. **Potential Concerns**:
   - Overlapping cohort with another study?
   - Unusual intervention protocol?
   - High risk of bias indicators?

## OUTPUT FORMAT:
```json
{
  "study_id": "FirstAuthor_Year",
  "design": "...",
  "intervention": "...",
  "comparator": "...",
  "n_intervention": X,
  "n_control": X,
  "donor_type": "...",
  "ecd_relevant": true/false,
  "co_interventions": ["..."] or null,
  "outcomes_available": ["ead", "nas", ...],
  "concerns": ["..."] or null,
  "proceed_to_full_extraction": true/false,
  "notes": "..."
}
```

## PAPER CONTENT
<paper>
{{PAPER_CONTENT}}
</paper>"""


# =============================================================================
# HELPER: Prompt Templates
# =============================================================================

def get_data_extraction_prompt(paper_content: str) -> str:
    """Main data extraction prompt"""
    return DATA_EXTRACTION_PROMPT.replace("{{PAPER_CONTENT}}", paper_content)


def get_rob_extraction_prompt(paper_content: str, study_type: str) -> str:
    """RoB information extraction prompt"""
    prompt = ROB_EXTRACTION_PROMPT.replace("{{PAPER_CONTENT}}", paper_content)
    prompt = prompt.replace("{{STUDY_TYPE}}", study_type)
    
    # Simple template rendering for conditional sections
    if study_type == "RCT":
        # Keep RCT section, remove NRS section
        start = prompt.find("{% if STUDY_TYPE == \"RCT\" %}")
        end = prompt.find("{% else %}")
        rct_content = prompt[start:end].replace("{% if STUDY_TYPE == \"RCT\" %}", "")
        
        nrs_start = prompt.find("{% else %}")
        nrs_end = prompt.find("{% endif %}")
        
        prompt = prompt[:start] + rct_content + prompt[nrs_end:].replace("{% endif %}", "")
    else:
        # Keep NRS section, remove RCT section
        start = prompt.find("{% if STUDY_TYPE == \"RCT\" %}")
        else_pos = prompt.find("{% else %}")
        endif_pos = prompt.find("{% endif %}")
        
        nrs_content = prompt[else_pos:endif_pos].replace("{% else %}", "")
        prompt = prompt[:start] + nrs_content + prompt[endif_pos:].replace("{% endif %}", "")
    
    return prompt


def get_outcome_extraction_prompt(paper_content: str, study_id: str, 
                                   intervention: str, control: str,
                                   n_intervention: int, n_control: int) -> str:
    """Outcome-focused extraction prompt"""
    prompt = OUTCOME_EXTRACTION_PROMPT.replace("{{PAPER_CONTENT}}", paper_content)
    prompt = prompt.replace("{{STUDY_ID}}", study_id)
    prompt = prompt.replace("{{INTERVENTION}}", intervention)
    prompt = prompt.replace("{{CONTROL}}", control)
    prompt = prompt.replace("{{N_INTERVENTION}}", str(n_intervention))
    prompt = prompt.replace("{{N_CONTROL}}", str(n_control))
    return prompt


def get_quick_screen_prompt(paper_content: str) -> str:
    """Quick screening prompt"""
    return QUICK_SCREEN_PROMPT.replace("{{PAPER_CONTENT}}", paper_content)


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    print("Available prompts:")
    print("1. DATA_EXTRACTION_PROMPT - Full data extraction")
    print("2. ROB_EXTRACTION_PROMPT - Risk of bias information")
    print("3. OUTCOME_EXTRACTION_PROMPT - Numerical outcomes focus")
    print("4. QUICK_SCREEN_PROMPT - Initial screening")
    print()
    print("Use helper functions:")
    print("  get_data_extraction_prompt(paper_content)")
    print("  get_rob_extraction_prompt(paper_content, 'RCT')")
    print("  get_outcome_extraction_prompt(paper_content, study_id, ...)")
    print("  get_quick_screen_prompt(paper_content)")
