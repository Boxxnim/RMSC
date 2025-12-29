"""
Data Extraction Schema for Machine Perfusion Systematic Review
목적: R 메타분석용 데이터 수집 + RoB 평가 정보 추출
참고: Kang et al. 2025 Table S3-S7
"""

# =============================================================================
# 1. STUDY CHARACTERISTICS (Table S3 형태)
# =============================================================================

STUDY_CHARACTERISTICS_SCHEMA = {
    "study_id": {
        "type": "string",
        "description": "FirstAuthor_Year format (e.g., Mueller_2025)",
        "required": True
    },
    "first_author": {"type": "string", "required": True},
    "year": {"type": "integer", "required": True},
    "title": {"type": "string", "required": True},
    "journal": {"type": "string", "required": True},
    "doi": {"type": "string", "required": False},
    
    # Study Design
    "study_design": {
        "type": "string",
        "enum": ["RCT", "Prospective cohort", "Retrospective cohort", "Case-control"],
        "required": True
    },
    "is_multicenter": {"type": "boolean", "required": True},
    "centers": {
        "type": "array",
        "items": "string",
        "description": "List of center names"
    },
    "countries": {"type": "array", "items": "string"},
    "enrollment_period": {
        "type": "object",
        "properties": {
            "start": {"type": "string", "format": "YYYY-MM or YYYY"},
            "end": {"type": "string", "format": "YYYY-MM or YYYY"}
        }
    },
    "registry_id": {"type": "string", "description": "NCT number or other registry"},
    
    # Intervention Details
    "intervention_type": {
        "type": "string",
        "enum": ["HOPE", "NMP", "DHOPE", "Other"],
        "required": True
    },
    "comparator": {
        "type": "string",
        "enum": ["SCS", "HMP", "Other"],
        "default": "SCS"
    },
    
    # Sample Size
    "n_total": {"type": "integer", "required": True},
    "n_intervention": {"type": "integer", "required": True},
    "n_control": {"type": "integer", "required": True},
    "n_analyzed_intervention": {
        "type": "integer",
        "description": "If different from randomized (per-protocol)"
    },
    "n_analyzed_control": {"type": "integer"},
    
    # Population
    "donor_type": {
        "type": "string",
        "enum": ["DCD", "DBD", "ECD-DBD", "Mixed"],
        "required": True
    },
    "ecd_definition_used": {
        "type": "string",
        "description": "How study defined ECD (quote or paraphrase)"
    },
    "ecd_percentage": {"type": "number", "description": "% of grafts meeting ECD criteria"},
    
    # Donor characteristics (median or mean)
    "donor_age": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"},
            "measure": {"type": "string", "enum": ["median", "mean"]}
        }
    },
    "donor_bmi": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"}
        }
    },
    "donor_risk_score": {
        "type": "object",
        "properties": {
            "score_type": {"type": "string", "enum": ["DRI", "UK-DCD", "BAR", "ET-DRI", "Other"]},
            "intervention": {"type": "number"},
            "control": {"type": "number"}
        }
    },
    
    # Recipient characteristics
    "recipient_age": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"},
            "measure": {"type": "string", "enum": ["median", "mean"]}
        }
    },
    "meld_score": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"},
            "measure": {"type": "string", "enum": ["median", "mean"]}
        }
    },
    
    # Matching (for NRS)
    "matching_method": {
        "type": "string",
        "description": "PSM, covariate matching, historical control, etc."
    },
    "matching_variables": {
        "type": "array",
        "items": "string"
    }
}


# =============================================================================
# 2. PERFUSION SETTINGS (Table S4 형태)
# =============================================================================

PERFUSION_SETTINGS_SCHEMA = {
    "study_id": {"type": "string", "required": True},
    
    # Device
    "device_name": {
        "type": "string",
        "description": "e.g., Liver Assist, OrganOx metra, OCS, VitaSmart"
    },
    "device_portable": {"type": "boolean"},
    
    # Cannulation
    "cannulation": {
        "type": "string",
        "enum": ["Single (PV)", "Dual (PV+HA)", "Not specified"],
        "description": "Portal vein only vs dual"
    },
    
    # Perfusate
    "perfusate_type": {
        "type": "string",
        "description": "e.g., Belzer MPS, UW solution, blood-based"
    },
    "perfusate_additives": {
        "type": "array",
        "items": "string",
        "description": "Any additives (important for co-intervention detection)"
    },
    
    # Temperature
    "temperature_setting": {
        "type": "string",
        "enum": ["Hypothermic (4-12°C)", "Subnormothermic (20-34°C)", "Normothermic (35-38°C)"]
    },
    "temperature_celsius": {"type": "number"},
    
    # Oxygenation
    "oxygenation": {
        "type": "object",
        "properties": {
            "active": {"type": "boolean"},
            "pO2_target": {"type": "string"},
            "flow_rate": {"type": "string"}
        }
    },
    
    # Pressure
    "pressure_settings": {
        "type": "object",
        "properties": {
            "portal_vein_mmHg": {"type": "number"},
            "hepatic_artery_mmHg": {"type": "number"}
        }
    },
    
    # Co-interventions (RED FLAGS)
    "co_interventions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "dose": {"type": "string"},
                "timing": {"type": "string"}
            }
        },
        "description": "tPA, defatting cocktails, stem cells, etc."
    },
    
    # Viability Assessment
    "viability_assessment": {
        "type": "object",
        "properties": {
            "performed": {"type": "boolean"},
            "criteria_used": {"type": "array", "items": "string"},
            "discard_based_on_viability": {"type": "boolean"},
            "discard_rate_intervention": {"type": "number"},
            "discard_rate_control": {"type": "number"}
        },
        "description": "Important for selection bias assessment"
    }
}


# =============================================================================
# 3. TIME METRICS (Table S5 형태)
# =============================================================================

TIME_METRICS_SCHEMA = {
    "study_id": {"type": "string", "required": True},
    
    # Perfusion initiation
    "perfusion_initiation": {
        "type": "string",
        "enum": ["Donor hospital", "During transport", "Recipient hospital (end-ischemic)", "Mixed"],
        "required": True
    },
    
    # Warm ischemia
    "functional_wit_minutes": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"},
            "measure": {"type": "string", "enum": ["median", "mean"]}
        },
        "description": "Functional warm ischemia time"
    },
    
    # Cold ischemia
    "cold_ischemia_time_hours": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"},
            "measure": {"type": "string", "enum": ["median", "mean"]}
        }
    },
    
    # Perfusion time
    "perfusion_time_hours": {
        "type": "object",
        "properties": {
            "value": {"type": "number"},
            "measure": {"type": "string", "enum": ["median", "mean"]},
            "range_or_sd": {"type": "string"}
        }
    },
    
    # Total preservation
    "total_preservation_time_hours": {
        "type": "object",
        "properties": {
            "intervention": {"type": "number"},
            "control": {"type": "number"}
        }
    },
    
    # Calculated ratio (for long-term vs short-term classification)
    "perfusion_to_preservation_ratio": {
        "type": "number",
        "description": "Perfusion time / Total preservation time (%)"
    }
}


# =============================================================================
# 4. OUTCOME DATA (메타분석용 핵심)
# =============================================================================

OUTCOME_DATA_SCHEMA = {
    "study_id": {"type": "string", "required": True},
    "follow_up_months": {"type": "number", "description": "Primary follow-up duration"},
    
    # Binary outcomes - structure for each
    # Format: events / total for each arm
    
    "ead": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string", "description": "Olthoff, other, or not specified"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number", "description": "RR, OR, or HR if reported"},
            "effect_type": {"type": "string", "enum": ["RR", "OR", "HR"]},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string", "description": "Verbatim text from paper supporting this data"},
            "source_location": {"type": "string", "description": "Table/Figure/Page reference (e.g., 'Table 2', 'Results p.5')"}
        }
    },
    
    "nas": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string"},
            "follow_up_for_nas_months": {"type": "number"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "tbc": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string", "description": "What's included in TBC"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "major_complications": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string", "description": "Clavien-Dindo ≥3 or ≥3b"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "acr": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string", "description": "Biopsy-proven, treated, Banff criteria"},
            "timeframe": {"type": "string"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "pnf": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "hat": {
        "type": "object",
        "description": "Hepatic artery thrombosis",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "retransplantation": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "timeframe": {"type": "string"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "aki": {
        "type": "object",
        "description": "Acute kidney injury",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string", "description": "RIFLE, KDIGO, etc."},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "rrt": {
        "type": "object",
        "description": "Renal replacement therapy",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "prs": {
        "type": "object",
        "description": "Post-reperfusion syndrome",
        "properties": {
            "reported": {"type": "boolean"},
            "definition": {"type": "string"},
            "intervention_events": {"type": "integer"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "effect_estimate": {"type": "number"},
            "effect_type": {"type": "string"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    # Continuous outcome
    "hospital_stay_days": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_mean_or_median": {"type": "number"},
            "intervention_sd_or_iqr": {"type": "string"},
            "control_mean_or_median": {"type": "number"},
            "control_sd_or_iqr": {"type": "string"},
            "measure": {"type": "string", "enum": ["mean", "median"]},
            "mean_difference": {"type": "number"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "icu_stay_days": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_mean_or_median": {"type": "number"},
            "intervention_sd_or_iqr": {"type": "string"},
            "control_mean_or_median": {"type": "number"},
            "control_sd_or_iqr": {"type": "string"},
            "measure": {"type": "string", "enum": ["mean", "median"]},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    # Survival outcomes
    "graft_survival_1yr": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_percent": {"type": "number"},
            "control_percent": {"type": "number"},
            "intervention_events": {"type": "integer", "description": "Graft loss events"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "hr": {"type": "number"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    "patient_survival_1yr": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_percent": {"type": "number"},
            "control_percent": {"type": "number"},
            "intervention_events": {"type": "integer", "description": "Death events"},
            "intervention_total": {"type": "integer"},
            "control_events": {"type": "integer"},
            "control_total": {"type": "integer"},
            "hr": {"type": "number"},
            "ci_lower": {"type": "number"},
            "ci_upper": {"type": "number"},
            "p_value": {"type": "number"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    },
    
    # Utilization (if applicable for NMP)
    "utilization_rate": {
        "type": "object",
        "properties": {
            "reported": {"type": "boolean"},
            "intervention_utilized": {"type": "integer"},
            "intervention_offered": {"type": "integer"},
            "control_utilized": {"type": "integer"},
            "control_offered": {"type": "integer"},
            "source_quote": {"type": "string"},
            "source_location": {"type": "string"}
        }
    }
}


# =============================================================================
# 5. RISK OF BIAS - RoB 2 for RCTs (Table S7)
# =============================================================================

ROB2_SCHEMA = {
    "study_id": {"type": "string", "required": True},
    "applies_to": {"type": "string", "default": "RCT"},
    
    # Domain 1: Randomization process
    "d1_randomization": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Some concerns", "High", "No information"]
            },
            "support_quotes": {
                "type": "array",
                "items": "string",
                "description": "Direct quotes from paper supporting judgment"
            },
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "random_sequence_generation": {
                        "type": "string",
                        "description": "How was the random sequence generated?"
                    },
                    "allocation_concealment": {
                        "type": "string",
                        "description": "Was allocation concealed until assignment?"
                    },
                    "baseline_imbalances": {
                        "type": "string",
                        "description": "Any baseline imbalances suggesting randomization problems?"
                    }
                }
            }
        }
    },
    
    # Domain 2: Deviations from intended interventions
    "d2_deviations": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Some concerns", "High", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "participants_blinded": {"type": "string"},
                    "personnel_blinded": {"type": "string"},
                    "deviations_occurred": {"type": "string"},
                    "intention_to_treat": {
                        "type": "string",
                        "description": "Was ITT analysis used?"
                    }
                }
            }
        }
    },
    
    # Domain 3: Missing outcome data
    "d3_missing_data": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Some concerns", "High", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "outcome_data_available": {
                        "type": "string",
                        "description": "Was outcome data available for all/nearly all participants?"
                    },
                    "dropout_rate_intervention": {"type": "number"},
                    "dropout_rate_control": {"type": "number"},
                    "dropout_reasons_balanced": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 4: Measurement of outcome
    "d4_measurement": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Some concerns", "High", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "outcome_assessor_blinded": {"type": "string"},
                    "outcome_objective": {
                        "type": "string",
                        "description": "Is outcome measurement objective (e.g., lab values) or subjective?"
                    },
                    "outcome_definition_appropriate": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 5: Selection of reported result
    "d5_selection": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Some concerns", "High", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "preregistered_protocol": {
                        "type": "string",
                        "description": "Was there a pre-registered protocol? Registry ID?"
                    },
                    "outcomes_match_protocol": {"type": "string"},
                    "multiple_analyses": {
                        "type": "string",
                        "description": "Evidence of multiple analyses with selective reporting?"
                    }
                }
            }
        }
    },
    
    # Overall
    "overall_judgment": {
        "type": "string",
        "enum": ["Low", "Some concerns", "High"]
    },
    "overall_rationale": {"type": "string"}
}


# =============================================================================
# 6. RISK OF BIAS - ROBINS-I for NRS (Table S6)
# =============================================================================

ROBINS_I_SCHEMA = {
    "study_id": {"type": "string", "required": True},
    "applies_to": {"type": "string", "default": "NRS"},
    
    # Domain 1: Confounding
    "d1_confounding": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "confounders_considered": {
                        "type": "array",
                        "items": "string",
                        "description": "Which confounders were controlled for?"
                    },
                    "adjustment_method": {
                        "type": "string",
                        "description": "PSM, regression, stratification, etc."
                    },
                    "residual_confounding_likely": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 2: Selection of participants
    "d2_selection": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "selection_into_study": {
                        "type": "string",
                        "description": "Was selection related to intervention and outcome?"
                    },
                    "start_of_followup": {"type": "string"},
                    "exclusions_post_intervention": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 3: Classification of interventions
    "d3_classification": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "intervention_well_defined": {"type": "string"},
                    "classification_based_on": {
                        "type": "string",
                        "description": "Prospective or retrospective classification?"
                    },
                    "misclassification_possible": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 4: Deviations from intended interventions
    "d4_deviations": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "co_interventions_balanced": {"type": "string"},
                    "implementation_differences": {"type": "string"},
                    "switches_between_groups": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 5: Missing data
    "d5_missing_data": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "data_available_for_all": {"type": "string"},
                    "missing_data_handled": {"type": "string"},
                    "differential_missingness": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 6: Measurement of outcomes
    "d6_measurement": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "outcome_assessors_aware": {"type": "string"},
                    "outcome_ascertainment_comparable": {"type": "string"},
                    "measurement_error_differential": {"type": "string"}
                }
            }
        }
    },
    
    # Domain 7: Selection of reported result
    "d7_selection": {
        "type": "object",
        "properties": {
            "judgment": {
                "type": "string",
                "enum": ["Low", "Moderate", "Serious", "Critical", "No information"]
            },
            "support_quotes": {"type": "array", "items": "string"},
            "signaling_questions": {
                "type": "object",
                "properties": {
                    "prespecified_analysis": {"type": "string"},
                    "multiple_outcomes_measured": {"type": "string"},
                    "multiple_analyses_performed": {"type": "string"}
                }
            }
        }
    },
    
    # Overall
    "overall_judgment": {
        "type": "string",
        "enum": ["Low", "Moderate", "Serious", "Critical"]
    },
    "overall_rationale": {"type": "string"}
}


# =============================================================================
# 7. COMBINED FULL EXTRACTION SCHEMA
# =============================================================================

FULL_EXTRACTION_SCHEMA = {
    "extraction_metadata": {
        "type": "object",
        "properties": {
            "extraction_date": {"type": "string", "format": "date-time"},
            "extractor_model": {"type": "string"},
            "paper_source": {"type": "string", "description": "PDF filename or source"}
        }
    },
    "study_characteristics": STUDY_CHARACTERISTICS_SCHEMA,
    "perfusion_settings": PERFUSION_SETTINGS_SCHEMA,
    "time_metrics": TIME_METRICS_SCHEMA,
    "outcome_data": OUTCOME_DATA_SCHEMA,
    "risk_of_bias": {
        "type": "object",
        "description": "Use ROB2 for RCTs, ROBINS-I for NRS",
        "oneOf": [ROB2_SCHEMA, ROBINS_I_SCHEMA]
    },
    "extraction_notes": {
        "type": "object",
        "properties": {
            "data_quality_concerns": {"type": "array", "items": "string"},
            "unclear_items_for_review": {"type": "array", "items": "string"},
            "potential_overlaps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "study_id": {"type": "string"},
                        "overlap_reason": {"type": "string"}
                    }
                }
            }
        }
    }
}


# =============================================================================
# Helper: Schema Summary for Quick Reference
# =============================================================================

SCHEMA_SUMMARY = """
DATA EXTRACTION SCHEMA SUMMARY
==============================

1. STUDY_CHARACTERISTICS (Table S3)
   - Study ID, design, centers, enrollment
   - Sample sizes (N intervention/control)
   - Donor/recipient characteristics
   - Matching method for NRS

2. PERFUSION_SETTINGS (Table S4)
   - Device, cannulation, perfusate
   - Temperature, oxygenation, pressure
   - Co-interventions (⚠️ RED FLAG)
   - Viability assessment protocols

3. TIME_METRICS (Table S5)
   - Perfusion initiation point
   - fWIT, CIT, perfusion time
   - Total preservation time
   - Perfusion:preservation ratio

4. OUTCOME_DATA (for R meta-analysis)
   Binary: EAD, NAS, TBC, ACR, PNF, HAT, RRT, PRS, retransplantation
   Continuous: Hospital stay, ICU stay
   Survival: 1-yr graft, 1-yr patient
   Each includes: events/total, RR/OR, 95% CI, p-value, definition

5. ROB2 (RCTs) - Table S7
   D1: Randomization
   D2: Deviations from intervention
   D3: Missing data
   D4: Outcome measurement
   D5: Selective reporting
   + Signaling questions & support quotes

6. ROBINS-I (NRS) - Table S6
   D1: Confounding
   D2: Selection
   D3: Classification
   D4: Deviations
   D5: Missing data
   D6: Measurement
   D7: Selective reporting
   + Signaling questions & support quotes
"""

if __name__ == "__main__":
    print(SCHEMA_SUMMARY)
