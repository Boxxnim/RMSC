"""
JSON Schemas for LLM-based study data extraction
Systematic Review: Ex vivo Machine Perfusion in ECD Liver Transplantation
"""

STUDY_REGISTRY_SCHEMA = {
    "type": "object",
    "properties": {
        "study_id": {
            "type": "string",
            "description": "Format: {INTERVENTION}_{CENTER}_{YEAR}{suffix} e.g., NMP_CCF_2025a"
        },
        "first_author": {"type": "string"},
        "year": {"type": "integer"},
        "title": {"type": "string"},
        "journal": {"type": "string"},
        "doi": {"type": "string"},
        "study_design": {
            "type": "string",
            "enum": ["RCT", "Prospective Cohort", "Retrospective Cohort", "Matched Cohort", "Registry Study"]
        },
        "centers": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Use standardized center codes from Codebook"
        },
        "countries": {
            "type": "array",
            "items": {"type": "string"},
            "description": "ISO 3166-1 alpha-2 codes"
        },
        "enrollment_period": {
            "type": "string",
            "description": "Format: YYYY-MM/YYYY-MM"
        },
        "registry_id": {
            "type": "string",
            "description": "NCT number or other registry ID"
        },
        "sample_size": {
            "type": "object",
            "properties": {
                "total": {"type": "integer"},
                "intervention": {"type": "integer"},
                "control": {"type": "integer"}
            }
        },
        "intervention_type": {
            "type": "string",
            "enum": ["SCS", "HOPE", "D-HOPE", "HMP", "NMP", "SNMP", "COR", "NRP", "IFLT", "OTHER"]
        },
        "comparator_type": {
            "type": "string",
            "enum": ["SCS", "HOPE", "D-HOPE", "HMP", "NMP", "SNMP", "COR", "NRP", "IFLT", "OTHER", "NONE"]
        },
        "donor_type": {
            "type": "array",
            "items": {"type": "string", "enum": ["DBD", "DCD", "ECD", "Mixed"]}
        },
        "co_interventions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any additional interventions: tPA, defatting, FMN-guided selection, etc."
        },
        "viability_criteria": {
            "type": "string",
            "description": "Description of viability assessment criteria used, if any"
        },
        "perfusion_timing": {
            "type": "string",
            "enum": ["End-ischemic", "Continuous", "Back-to-base", "In-transit", "Not specified"]
        },
        "outcomes_reported": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["EAD", "NAS", "TBC", "ACR", "PNF", "HAT", "Retransplantation", 
                        "RRT", "AKI", "Graft_survival", "Patient_survival", "Hospital_stay", "Other"]
            }
        },
        "ecd_definition": {
            "type": "string",
            "description": "How ECD/high-risk donors were defined in this study"
        },
        "notes": {"type": "string"}
    },
    "required": ["study_id", "first_author", "year", "study_design", "intervention_type"]
}

ELIGIBILITY_ASSESSMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "study_id": {"type": "string"},
        "decision": {
            "type": "string",
            "enum": ["Include", "Exclude", "Pending", "Sensitivity only"]
        },
        "exclusion_category": {
            "type": "string",
            "enum": [
                "Co-intervention",
                "Viability-guided selection",
                "Heterogeneous technique",
                "Overlapping cohort",
                "Non-ECD population",
                "Wrong comparator",
                "Insufficient data",
                "High RoB",
                "Other",
                ""
            ]
        },
        "rationale": {
            "type": "string",
            "description": "Detailed explanation of eligibility decision"
        },
        "pico_violation": {
            "type": "string",
            "enum": ["Population", "Intervention", "Comparator", "Outcome", "Multiple", "None"]
        },
        "precedent": {
            "type": "string",
            "description": "Reference to guideline or previous decision supporting this judgment"
        },
        "concerns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "concern_type": {"type": "string"},
                    "detail": {"type": "string"},
                    "severity": {"type": "string", "enum": ["Minor", "Moderate", "Major"]}
                }
            }
        },
        "confidence": {
            "type": "string",
            "enum": ["High", "Medium", "Low"],
            "description": "Confidence in this eligibility assessment"
        }
    },
    "required": ["study_id", "decision", "rationale", "confidence"]
}

COHORT_LINKAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "study_id_a": {"type": "string"},
        "study_id_b": {"type": "string"},
        "overlap_type": {
            "type": "string",
            "enum": ["Confirmed Duplicate", "Likely Overlap", "Subset", "No Overlap", "Unknown"]
        },
        "overlap_evidence": {
            "type": "string",
            "description": "Evidence supporting overlap assessment"
        },
        "shared_elements": {
            "type": "object",
            "properties": {
                "centers": {"type": "array", "items": {"type": "string"}},
                "enrollment_overlap": {"type": "string"},
                "registry_id": {"type": "string"},
                "author_overlap": {"type": "array", "items": {"type": "string"}}
            }
        },
        "estimated_overlap_percent": {"type": "integer"},
        "resolution_recommendation": {
            "type": "string",
            "enum": ["Use A only", "Use B only", "Merge data", "Exclude both", "Pending author contact", "Outcome-specific"]
        },
        "resolution_rationale": {"type": "string"}
    },
    "required": ["study_id_a", "study_id_b", "overlap_type", "overlap_evidence"]
}

# Combined schema for full extraction
FULL_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "registry_data": STUDY_REGISTRY_SCHEMA,
        "eligibility": ELIGIBILITY_ASSESSMENT_SCHEMA,
        "potential_overlaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "related_study": {"type": "string"},
                    "relationship_type": {"type": "string"},
                    "evidence": {"type": "string"}
                }
            }
        }
    }
}
