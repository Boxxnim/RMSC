"""
Tool Definitions for Gemini Function Calling
Machine Perfusion Systematic Review Data Extraction

Tools:
1. get_rob_skill - Get RoB assessment instructions based on study type (JIT injection)
2. submit_extraction_rct - Submit extraction with RoB 2 (for RCTs)
3. submit_extraction_nrs - Submit extraction with ROBINS-I (for NRS)
"""

from google.genai import types


# =============================================================================
# Tool: get_rob_skill
# JIT injects appropriate RoB assessment instructions
# =============================================================================

GET_ROB_SKILL_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_rob_skill",
            description="Get detailed Risk of Bias assessment instructions. Call this AFTER determining the study type (RCT or NRS) from the paper. Returns specific assessment criteria and domain descriptions.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "study_type": types.Schema(
                        type="STRING",
                        description="The study design type. Use 'RCT' for randomized controlled trials, 'NRS' for non-randomized studies (cohorts, case-control, etc.)",
                        enum=["RCT", "NRS"]
                    ),
                    "study_id": types.Schema(
                        type="STRING",
                        description="Study identifier in FirstAuthor_Year format (e.g., Mueller_2025)"
                    )
                },
                required=["study_type", "study_id"]
            )
        )
    ]
)


# =============================================================================
# Shared Schema Components
# =============================================================================

def _binary_outcome_schema(description: str) -> types.Schema:
    return types.Schema(
        type="OBJECT",
        description=description,
        properties={
            "reported": types.Schema(type="BOOLEAN", description="Whether this outcome is reported in the paper"),
            "definition": types.Schema(type="STRING", description="Definition used in the paper", nullable=True),
            "intervention_events": types.Schema(type="INTEGER", nullable=True),
            "intervention_total": types.Schema(type="INTEGER", nullable=True),
            "control_events": types.Schema(type="INTEGER", nullable=True),
            "control_total": types.Schema(type="INTEGER", nullable=True),
            "rr": types.Schema(type="NUMBER", description="Risk Ratio or Odds Ratio", nullable=True),
            "ci_lower": types.Schema(type="NUMBER", nullable=True),
            "ci_upper": types.Schema(type="NUMBER", nullable=True),
            "p_value": types.Schema(type="NUMBER", nullable=True),
            "source_location": types.Schema(type="STRING", description="Table/Figure/Page reference", nullable=True),
        },
        required=["reported"]
    )


def _rob_domain_schema(description: str) -> types.Schema:
    return types.Schema(
        type="OBJECT",
        description=description,
        properties={
            "judgment": types.Schema(type="STRING", description="Risk level judgment"),
            "rationale": types.Schema(type="STRING", description="Reasoning for the judgment"),
            "support_quotes": types.Schema(
                type="ARRAY",
                items=types.Schema(type="STRING"),
                description="Direct quotes from paper supporting the judgment",
                nullable=True
            ),
        },
        required=["judgment", "rationale"]
    )


# Shared study characteristics schema
STUDY_CHARACTERISTICS_SCHEMA = types.Schema(
    type="OBJECT",
    description="Basic study information",
    properties={
        "study_id": types.Schema(type="STRING", description="FirstAuthor_Year format"),
        "first_author": types.Schema(type="STRING"),
        "year": types.Schema(type="INTEGER"),
        "title": types.Schema(type="STRING"),
        "journal": types.Schema(type="STRING"),
        "doi": types.Schema(type="STRING", nullable=True),
        "study_design": types.Schema(type="STRING", description="RCT, Prospective cohort, or Retrospective cohort"),
        "is_multicenter": types.Schema(type="BOOLEAN"),
        "countries": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
        "centers": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
        "enrollment_period_start": types.Schema(type="STRING", nullable=True),
        "enrollment_period_end": types.Schema(type="STRING", nullable=True),
        "registry_id": types.Schema(type="STRING", description="NCT number if available", nullable=True),
        "intervention_type": types.Schema(type="STRING", description="HOPE, NMP, DHOPE, SNMP"),
        "comparator": types.Schema(type="STRING", nullable=True),
        "n_intervention": types.Schema(type="INTEGER"),
        "n_control": types.Schema(type="INTEGER"),
        "n_total": types.Schema(type="INTEGER"),
        "donor_type": types.Schema(type="STRING", description="DCD, DBD, ECD-DBD, or Mixed"),
        # NRS matching information
        "matching_method": types.Schema(
            type="STRING", 
            description="For NRS only: PSM, IPTW, case-control matching, caliper matching, etc. Null for RCTs.",
            nullable=True
        ),
        "matching_ratio": types.Schema(
            type="STRING",
            description="For NRS: matching ratio e.g. '1:1', '1:2', '1:3'. Null for RCTs.",
            nullable=True
        ),
        "matching_variables": types.Schema(
            type="ARRAY",
            items=types.Schema(type="STRING"),
            description="For NRS: variables used for matching (e.g., age, MELD, donor type). Null for RCTs.",
            nullable=True
        ),
    },
    required=["study_id", "first_author", "year", "study_design", "intervention_type", 
              "n_intervention", "n_control", "n_total", "donor_type"]
)

# Shared perfusion settings schema
PERFUSION_SETTINGS_SCHEMA = types.Schema(
    type="OBJECT",
    description="Machine perfusion technical settings",
    properties={
        "device_name": types.Schema(type="STRING", nullable=True),
        "cannulation": types.Schema(type="STRING", description="Single (PV) or Dual (PV+HA)", nullable=True),
        "perfusate_type": types.Schema(type="STRING", nullable=True),
        "temperature_setting": types.Schema(type="STRING", nullable=True),
        "temperature_celsius": types.Schema(type="NUMBER", nullable=True),
    },
    required=[]
)

# Helper for continuous outcome (mean ± SD, or median with IQR)
def _continuous_outcome_schema(description: str):
    return types.Schema(
        type="OBJECT",
        description=description,
        nullable=True,
        properties={
            "mean": types.Schema(type="NUMBER", nullable=True),
            "sd": types.Schema(type="NUMBER", nullable=True),
            "median": types.Schema(type="NUMBER", nullable=True),
            "iqr_lower": types.Schema(type="NUMBER", nullable=True),
            "iqr_upper": types.Schema(type="NUMBER", nullable=True),
            "n": types.Schema(type="INTEGER", nullable=True),
            "source": types.Schema(type="STRING", nullable=True),
        }
    )

# Shared time metrics schema (extended for meta-regression)
TIME_METRICS_SCHEMA = types.Schema(
    type="OBJECT",
    description="Time-related metrics for meta-regression analysis",
    properties={
        # Basic info
        "perfusion_initiation": types.Schema(type="STRING", description="When perfusion started: back-to-base, transport, etc.", nullable=True),
        
        # Perfusion duration
        "perfusion_duration_intervention": _continuous_outcome_schema("Perfusion duration in hours for intervention group"),
        
        # Cold Ischemia Time (CIT) by group
        "cit_intervention": _continuous_outcome_schema("Cold ischemia time (hours) for intervention group"),
        "cit_control": _continuous_outcome_schema("Cold ischemia time (hours) for control group"),
        
        # Warm Ischemia Time (WIT) by group - important for DCD
        "wit_intervention": _continuous_outcome_schema("Warm ischemia time (minutes) for intervention group"),
        "wit_control": _continuous_outcome_schema("Warm ischemia time (minutes) for control group"),
        
        # Total Ischemia Time
        "total_ischemia_intervention": _continuous_outcome_schema("Total ischemia time (hours) for intervention group"),
        "total_ischemia_control": _continuous_outcome_schema("Total ischemia time (hours) for control group"),
        
        # Hospital/ICU stay - continuous outcomes
        "hospital_stay_intervention": _continuous_outcome_schema("Hospital stay (days) for intervention group"),
        "hospital_stay_control": _continuous_outcome_schema("Hospital stay (days) for control group"),
        "icu_stay_intervention": _continuous_outcome_schema("ICU stay (days) for intervention group"),
        "icu_stay_control": _continuous_outcome_schema("ICU stay (days) for control group"),
    },
    required=[]
)

# Shared outcome data schema
OUTCOME_DATA_SCHEMA = types.Schema(
    type="OBJECT",
    description="Clinical outcomes",
    properties={
        "follow_up_months": types.Schema(type="NUMBER", nullable=True),
        "ead": _binary_outcome_schema(
            "Early Allograft Dysfunction (EAD) - commonly defined by Olthoff criteria: "
            "bilirubin ≥10 mg/dL on day 7, INR ≥1.6 on day 7, or ALT/AST >2000 U/L within first 7 days"
        ),
        "nas": _binary_outcome_schema(
            "Non-Anastomotic Biliary Stricture (NAS) / Ischemic-type Biliary Lesions (ITBL) - "
            "biliary strictures NOT at the anastomosis site, typically ischemic in origin"
        ),
        "tbc": _binary_outcome_schema(
            "Total Biliary Complications - SUM of ALL biliary complications including: "
            "NAS (non-anastomotic strictures) + anastomotic biliary strictures + bile leaks/leakage. "
            "Count each type and sum them for total."
        ),
        "pnf": _binary_outcome_schema(
            "Primary Non-Function (PNF) - irreversible graft failure requiring retransplantation or "
            "leading to death within 7-10 days without identifiable cause"
        ),
        "acr": _binary_outcome_schema(
            "Acute Cellular Rejection (ACR) - biopsy-proven acute rejection episode"
        ),
        "hat": _binary_outcome_schema(
            "Hepatic Artery Thrombosis (HAT) - arterial thrombosis confirmed by imaging"
        ),
        "retransplantation": _binary_outcome_schema(
            "Retransplantation - need for liver retransplantation for any cause"
        ),
        "rrt": _binary_outcome_schema(
            "Renal Replacement Therapy (RRT) - need for dialysis post-transplant"
        ),
        "aki": _binary_outcome_schema(
            "Acute Kidney Injury (AKI) - commonly defined by KDIGO criteria or RIFLE criteria"
        ),
        "prs": _binary_outcome_schema(
            "Post-Reperfusion Syndrome (PRS) - typically defined as >30% decrease in mean arterial "
            "pressure within 5-10 minutes after reperfusion, lasting at least 1 minute"
        ),
        "major_complications": _binary_outcome_schema(
            "Major complications - Clavien-Dindo grade ≥3 (requiring surgical, endoscopic, or "
            "radiological intervention, or life-threatening/requiring ICU, or death)"
        ),
        "graft_survival_1yr": types.Schema(
            type="OBJECT",
            properties={
                "reported": types.Schema(type="BOOLEAN"),
                "intervention_percent": types.Schema(type="NUMBER", nullable=True),
                "control_percent": types.Schema(type="NUMBER", nullable=True),
                "hr": types.Schema(type="NUMBER", nullable=True),
                "ci_lower": types.Schema(type="NUMBER", nullable=True),
                "ci_upper": types.Schema(type="NUMBER", nullable=True),
                "p_value": types.Schema(type="NUMBER", nullable=True),
                "source_location": types.Schema(type="STRING", nullable=True),
            },
            required=["reported"]
        ),
        "patient_survival_1yr": types.Schema(
            type="OBJECT",
            properties={
                "reported": types.Schema(type="BOOLEAN"),
                "intervention_percent": types.Schema(type="NUMBER", nullable=True),
                "control_percent": types.Schema(type="NUMBER", nullable=True),
                "hr": types.Schema(type="NUMBER", nullable=True),
                "source_location": types.Schema(type="STRING", nullable=True),
            },
            required=["reported"]
        ),
        "hospital_stay_days": types.Schema(
            type="OBJECT",
            properties={
                "reported": types.Schema(type="BOOLEAN"),
                "intervention_value": types.Schema(type="NUMBER", nullable=True),
                "intervention_sd_or_iqr": types.Schema(type="STRING", nullable=True),
                "control_value": types.Schema(type="NUMBER", nullable=True),
                "control_sd_or_iqr": types.Schema(type="STRING", nullable=True),
                "measure": types.Schema(type="STRING", description="mean or median", nullable=True),
                "source_location": types.Schema(type="STRING", nullable=True),
            },
            required=["reported"]
        ),
        "icu_stay_days": types.Schema(
            type="OBJECT",
            properties={
                "reported": types.Schema(type="BOOLEAN"),
                "intervention_value": types.Schema(type="NUMBER", nullable=True),
                "intervention_sd_or_iqr": types.Schema(type="STRING", nullable=True),
                "control_value": types.Schema(type="NUMBER", nullable=True),
                "control_sd_or_iqr": types.Schema(type="STRING", nullable=True),
                "measure": types.Schema(type="STRING", nullable=True),
                "source_location": types.Schema(type="STRING", nullable=True),
            },
            required=["reported"]
        ),
    },
    required=["ead", "nas", "tbc", "pnf", "acr", "hat", "retransplantation", 
              "rrt", "aki", "prs", "major_complications", 
              "graft_survival_1yr", "patient_survival_1yr", 
              "hospital_stay_days", "icu_stay_days"]
)

# Shared extraction notes schema
EXTRACTION_NOTES_SCHEMA = types.Schema(
    type="OBJECT",
    properties={
        "data_quality_concerns": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
        "unclear_items_for_review": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
        "potential_overlaps": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
        "general_notes": types.Schema(type="STRING", nullable=True),
    },
    required=[]
)


# =============================================================================
# RoB 2 Schema (for RCTs only)
# =============================================================================

ROB_RCT_SCHEMA = types.Schema(
    type="OBJECT",
    description="RoB 2 assessment for RCTs",
    properties={
        "d1_randomization": _rob_domain_schema("Domain 1: Randomization Process"),
        "d2_deviations": _rob_domain_schema("Domain 2: Deviations from Intended Interventions"),
        "d3_missing_data": _rob_domain_schema("Domain 3: Missing Outcome Data"),
        "d4_measurement": _rob_domain_schema("Domain 4: Measurement of Outcome"),
        "d5_selection": _rob_domain_schema("Domain 5: Selection of Reported Result"),
        "overall_judgment": types.Schema(type="STRING", description="Low, Some concerns, or High"),
        "overall_rationale": types.Schema(type="STRING"),
    },
    required=["d1_randomization", "d2_deviations", "d3_missing_data", 
              "d4_measurement", "d5_selection", "overall_judgment", "overall_rationale"]
)


# =============================================================================
# ROBINS-I Schema (for NRS only)
# =============================================================================

ROB_NRS_SCHEMA = types.Schema(
    type="OBJECT",
    description="ROBINS-I assessment for non-randomized studies",
    properties={
        "d1_confounding": _rob_domain_schema("Domain 1: Confounding"),
        "d2_selection": _rob_domain_schema("Domain 2: Selection of Participants"),
        "d3_classification": _rob_domain_schema("Domain 3: Classification of Interventions"),
        "d4_deviations": _rob_domain_schema("Domain 4: Deviations from Intended Interventions"),
        "d5_missing_data": _rob_domain_schema("Domain 5: Missing Data"),
        "d6_measurement": _rob_domain_schema("Domain 6: Measurement of Outcomes"),
        "d7_selection": _rob_domain_schema("Domain 7: Selection of Reported Result"),
        "overall_judgment": types.Schema(type="STRING", description="Low, Moderate, Serious, or Critical"),
        "overall_rationale": types.Schema(type="STRING"),
    },
    required=["d1_confounding", "d2_selection", "d3_classification", "d4_deviations",
              "d5_missing_data", "d6_measurement", "d7_selection", 
              "overall_judgment", "overall_rationale"]
)


# =============================================================================
# Tool: submit_extraction_rct (for RCTs - uses RoB 2)
# =============================================================================

SUBMIT_EXTRACTION_RCT_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="submit_extraction",
            description="Submit the complete extraction including study characteristics, outcomes, and RoB 2 assessment. Call this AFTER completing all data extraction and RoB assessment for RCT studies.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "study_characteristics": STUDY_CHARACTERISTICS_SCHEMA,
                    "perfusion_settings": PERFUSION_SETTINGS_SCHEMA,
                    "time_metrics": TIME_METRICS_SCHEMA,
                    "outcome_data": OUTCOME_DATA_SCHEMA,
                    "rob_rct": ROB_RCT_SCHEMA,
                    "extraction_notes": EXTRACTION_NOTES_SCHEMA,
                },
                required=["study_characteristics", "outcome_data", "rob_rct", "extraction_notes"]
            )
        )
    ]
)


# =============================================================================
# Tool: submit_extraction_nrs (for NRS - uses ROBINS-I)
# =============================================================================

SUBMIT_EXTRACTION_NRS_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="submit_extraction",
            description="Submit the complete extraction including study characteristics, outcomes, and ROBINS-I assessment. Call this AFTER completing all data extraction and RoB assessment for non-randomized studies.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "study_characteristics": STUDY_CHARACTERISTICS_SCHEMA,
                    "perfusion_settings": PERFUSION_SETTINGS_SCHEMA,
                    "time_metrics": TIME_METRICS_SCHEMA,
                    "outcome_data": OUTCOME_DATA_SCHEMA,
                    "rob_nrs": ROB_NRS_SCHEMA,
                    "extraction_notes": EXTRACTION_NOTES_SCHEMA,
                },
                required=["study_characteristics", "outcome_data", "rob_nrs", "extraction_notes"]
            )
        )
    ]
)


# =============================================================================
# Tools for Initial Call (only get_rob_skill available)
# =============================================================================

INITIAL_TOOLS = [GET_ROB_SKILL_TOOL]


# =============================================================================
# Helper function to get tools based on study type
# =============================================================================

def get_extraction_tools(study_type: str) -> list:
    """Get the appropriate submit_extraction tool based on study type.
    
    Args:
        study_type: "RCT" or "NRS"
        
    Returns:
        List of tools with the appropriate submit_extraction tool
    """
    if study_type == "RCT":
        return [SUBMIT_EXTRACTION_RCT_TOOL]
    else:
        return [SUBMIT_EXTRACTION_NRS_TOOL]


# Legacy compatibility - combined tools (deprecated)
SUBMIT_EXTRACTION_TOOL = SUBMIT_EXTRACTION_RCT_TOOL  # Default to RCT for backwards compat
EXTRACTION_TOOLS = [GET_ROB_SKILL_TOOL, SUBMIT_EXTRACTION_RCT_TOOL]
