"""
Gemini API용 Structured Output Schemas
google.genai.types.Schema 형식으로 정의
"""

from google.genai import types

# =============================================================================
# Full Extraction Schema
# =============================================================================

# Binary Outcome 공통 구조
def binary_outcome_schema(description: str = "") -> dict:
    return {
        "type": "OBJECT",
        "description": description,
        "properties": {
            "reported": {"type": "BOOLEAN", "description": "해당 outcome이 논문에 보고되었는가"},
            "definition": {"type": "STRING", "description": "논문에서 사용한 정의", "nullable": True},
            "intervention_events": {"type": "INTEGER", "description": "중재군 이벤트 수", "nullable": True},
            "intervention_total": {"type": "INTEGER", "description": "중재군 총 환자 수", "nullable": True},
            "control_events": {"type": "INTEGER", "description": "대조군 이벤트 수", "nullable": True},
            "control_total": {"type": "INTEGER", "description": "대조군 총 환자 수", "nullable": True},
            "rr": {"type": "NUMBER", "description": "Relative Risk 또는 다른 effect estimate", "nullable": True},
            "ci_lower": {"type": "NUMBER", "description": "95% CI 하한", "nullable": True},
            "ci_upper": {"type": "NUMBER", "description": "95% CI 상한", "nullable": True},
            "p_value": {"type": "NUMBER", "description": "p-value", "nullable": True},
            "source_quote": {"type": "STRING", "description": "원문에서 발췌한 인용문", "nullable": True},
            "source_location": {"type": "STRING", "description": "데이터 위치 (Table/Figure/Page)", "nullable": True},
        },
        "required": ["reported"]
    }


FULL_EXTRACTION_SCHEMA = types.Schema(
    type="OBJECT",
    description="Machine Perfusion 연구의 전체 데이터 추출 결과",
    properties={
        "study_characteristics": types.Schema(
            type="OBJECT",
            description="연구 기본 정보",
            properties={
                "study_id": types.Schema(type="STRING", description="FirstAuthor_Year 형식 (예: Mueller_2025)"),
                "first_author": types.Schema(type="STRING", description="제1저자 성"),
                "year": types.Schema(type="INTEGER", description="출판 연도"),
                "title": types.Schema(type="STRING", description="논문 제목"),
                "journal": types.Schema(type="STRING", description="저널명"),
                "doi": types.Schema(type="STRING", description="DOI", nullable=True),
                "study_design": types.Schema(type="STRING", description="RCT, Prospective cohort, Retrospective cohort 중 하나"),
                "is_multicenter": types.Schema(type="BOOLEAN", description="다기관 연구 여부"),
                "countries": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), description="연구 수행 국가", nullable=True),
                "centers": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), description="참여 기관/센터명 리스트", nullable=True),
                "enrollment_period_start": types.Schema(type="STRING", description="등록 시작 시기 (YYYY-MM 또는 YYYY 형식)", nullable=True),
                "enrollment_period_end": types.Schema(type="STRING", description="등록 종료 시기 (YYYY-MM 또는 YYYY 형식)", nullable=True),
                "registry_id": types.Schema(type="STRING", description="NCT number 등 clinical trial registry ID", nullable=True),
                "data_source": types.Schema(type="STRING", description="데이터 소스 (SRTR, UNOS, Eurotransplant, single center 등)", nullable=True),
                "intervention_type": types.Schema(type="STRING", description="HOPE, NMP, DHOPE, SNMP 중 하나"),
                "comparator": types.Schema(type="STRING", description="SCS가 기본", nullable=True),
                "n_intervention": types.Schema(type="INTEGER", description="중재군 환자 수"),
                "n_control": types.Schema(type="INTEGER", description="대조군 환자 수"),
                "n_total": types.Schema(type="INTEGER", description="총 환자 수"),
                "donor_type": types.Schema(type="STRING", description="DCD, DBD, ECD-DBD, Mixed 중 하나"),
            },
            required=["study_id", "first_author", "year", "study_design", "intervention_type", "n_intervention", "n_control", "n_total", "donor_type"]
        ),
        "perfusion_settings": types.Schema(
            type="OBJECT",
            description="관류 설정",
            properties={
                "device_name": types.Schema(type="STRING", description="장비명 (Liver Assist, OrganOx metra 등)", nullable=True),
                "cannulation": types.Schema(type="STRING", description="Single (PV) 또는 Dual (PV+HA)", nullable=True),
                "perfusate_type": types.Schema(type="STRING", description="관류액 종류", nullable=True),
                "temperature_setting": types.Schema(type="STRING", description="Hypothermic, Subnormothermic, Normothermic", nullable=True),
                "temperature_celsius": types.Schema(type="NUMBER", description="온도 (°C)", nullable=True),
            },
            required=[]
        ),
        "time_metrics": types.Schema(
            type="OBJECT",
            description="시간 지표",
            properties={
                "perfusion_initiation": types.Schema(type="STRING", description="관류 시작 장소/시점", nullable=True),
                "perfusion_time_hours": types.Schema(type="NUMBER", description="관류 시간 (시간)", nullable=True),
                "cold_ischemia_time_hours": types.Schema(type="NUMBER", description="냉허혈 시간 (시간)", nullable=True),
                "warm_ischemia_time_minutes": types.Schema(type="NUMBER", description="온허혈 시간 (분)", nullable=True),
            },
            required=[]
        ),
        "outcome_data": types.Schema(
            type="OBJECT",
            description="결과 데이터 - 각 outcome에 대해 reported가 true면 데이터 있음, false면 논문에서 보고하지 않음",
            properties={
                "follow_up_months": types.Schema(type="NUMBER", description="추적 기간 (개월)", nullable=True),
                # Binary outcomes
                "ead": types.Schema(
                    type="OBJECT",
                    description="Early Allograft Dysfunction",
                    properties={
                        "reported": types.Schema(type="BOOLEAN", description="보고 여부"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "rr": types.Schema(type="NUMBER", nullable=True),
                        "ci_lower": types.Schema(type="NUMBER", nullable=True),
                        "ci_upper": types.Schema(type="NUMBER", nullable=True),
                        "p_value": types.Schema(type="NUMBER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "nas": types.Schema(
                    type="OBJECT",
                    description="Non-Anastomotic Biliary Stricture",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "follow_up_for_nas_months": types.Schema(type="NUMBER", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "rr": types.Schema(type="NUMBER", nullable=True),
                        "ci_lower": types.Schema(type="NUMBER", nullable=True),
                        "ci_upper": types.Schema(type="NUMBER", nullable=True),
                        "p_value": types.Schema(type="NUMBER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "tbc": types.Schema(
                    type="OBJECT",
                    description="Total Biliary Complications (NAS + anastomotic stricture)",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "pnf": types.Schema(
                    type="OBJECT",
                    description="Primary Non-Function",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "acr": types.Schema(
                    type="OBJECT",
                    description="Acute Cellular Rejection",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "timeframe": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "hat": types.Schema(
                    type="OBJECT",
                    description="Hepatic Artery Thrombosis",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "retransplantation": types.Schema(
                    type="OBJECT",
                    description="Retransplantation",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "timeframe": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "rrt": types.Schema(
                    type="OBJECT",
                    description="Renal Replacement Therapy",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "aki": types.Schema(
                    type="OBJECT",
                    description="Acute Kidney Injury",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "prs": types.Schema(
                    type="OBJECT",
                    description="Post-Reperfusion Syndrome",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                "major_complications": types.Schema(
                    type="OBJECT",
                    description="Major Surgical Complications (Clavien-Dindo ≥3)",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "definition": types.Schema(type="STRING", nullable=True),
                        "intervention_events": types.Schema(type="INTEGER", nullable=True),
                        "intervention_total": types.Schema(type="INTEGER", nullable=True),
                        "control_events": types.Schema(type="INTEGER", nullable=True),
                        "control_total": types.Schema(type="INTEGER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                # Survival outcomes
                "graft_survival_1yr": types.Schema(
                    type="OBJECT",
                    description="1년 이식편 생존율",
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
                    description="1년 환자 생존율",
                    properties={
                        "reported": types.Schema(type="BOOLEAN"),
                        "intervention_percent": types.Schema(type="NUMBER", nullable=True),
                        "control_percent": types.Schema(type="NUMBER", nullable=True),
                        "hr": types.Schema(type="NUMBER", nullable=True),
                        "source_location": types.Schema(type="STRING", nullable=True),
                    },
                    required=["reported"]
                ),
                # Continuous outcomes
                "hospital_stay_days": types.Schema(
                    type="OBJECT",
                    description="Hospital length of stay",
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
                    description="ICU length of stay",
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
            },
            required=["ead", "nas", "tbc", "pnf", "acr", "hat", "retransplantation", "rrt", "aki", "prs", "major_complications", "graft_survival_1yr", "patient_survival_1yr", "hospital_stay_days", "icu_stay_days"]
        ),
        "extraction_notes": types.Schema(
            type="OBJECT",
            description="추출 관련 메모",
            properties={
                "data_quality_concerns": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
                "unclear_items_for_review": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
                "general_notes": types.Schema(type="STRING", nullable=True),
            },
            required=[]
        ),
    },
    required=["study_characteristics", "outcome_data"]
)


# =============================================================================
# RoB2 Schema (RCT용)
# =============================================================================

ROB2_EXTRACTION_SCHEMA = types.Schema(
    type="OBJECT",
    description="RCT에 대한 RoB2 평가",
    properties={
        "study_id": types.Schema(type="STRING", description="연구 ID"),
        "d1_randomization": types.Schema(
            type="OBJECT",
            description="Domain 1: Randomization Process",
            properties={
                "judgment": types.Schema(type="STRING", description="Low, Some concerns, High 중 하나"),
                "rationale": types.Schema(type="STRING", description="판단 근거"),
                "support_quotes": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), description="원문 인용", nullable=True),
            },
            required=["judgment", "rationale"]
        ),
        "d2_deviations": types.Schema(
            type="OBJECT",
            description="Domain 2: Deviations from Intended Interventions",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
                "support_quotes": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
            },
            required=["judgment", "rationale"]
        ),
        "d3_missing_data": types.Schema(
            type="OBJECT",
            description="Domain 3: Missing Outcome Data",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
                "support_quotes": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
            },
            required=["judgment", "rationale"]
        ),
        "d4_measurement": types.Schema(
            type="OBJECT",
            description="Domain 4: Measurement of Outcome",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
                "support_quotes": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
            },
            required=["judgment", "rationale"]
        ),
        "d5_selection": types.Schema(
            type="OBJECT",
            description="Domain 5: Selection of Reported Result",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
                "support_quotes": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
            },
            required=["judgment", "rationale"]
        ),
        "overall_judgment": types.Schema(type="STRING", description="전체 판단: Low, Some concerns, High"),
        "overall_rationale": types.Schema(type="STRING", description="전체 판단 근거"),
    },
    required=["study_id", "d1_randomization", "d2_deviations", "d3_missing_data", "d4_measurement", "d5_selection", "overall_judgment", "overall_rationale"]
)


# =============================================================================
# ROBINS-I Schema (NRS용)
# =============================================================================

ROBINS_I_EXTRACTION_SCHEMA = types.Schema(
    type="OBJECT",
    description="Non-randomized study에 대한 ROBINS-I 평가",
    properties={
        "study_id": types.Schema(type="STRING", description="연구 ID"),
        "d1_confounding": types.Schema(
            type="OBJECT",
            description="Domain 1: Confounding",
            properties={
                "judgment": types.Schema(type="STRING", description="Low, Moderate, Serious, Critical 중 하나"),
                "rationale": types.Schema(type="STRING"),
                "confounders_addressed": types.Schema(type="ARRAY", items=types.Schema(type="STRING"), nullable=True),
            },
            required=["judgment", "rationale"]
        ),
        "d2_selection": types.Schema(
            type="OBJECT",
            description="Domain 2: Selection of Participants",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
            },
            required=["judgment", "rationale"]
        ),
        "d3_classification": types.Schema(
            type="OBJECT",
            description="Domain 3: Classification of Interventions",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
            },
            required=["judgment", "rationale"]
        ),
        "d4_deviations": types.Schema(
            type="OBJECT",
            description="Domain 4: Deviations from Intended Interventions",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
            },
            required=["judgment", "rationale"]
        ),
        "d5_missing_data": types.Schema(
            type="OBJECT",
            description="Domain 5: Missing Data",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
            },
            required=["judgment", "rationale"]
        ),
        "d6_measurement": types.Schema(
            type="OBJECT",
            description="Domain 6: Measurement of Outcomes",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
            },
            required=["judgment", "rationale"]
        ),
        "d7_selection": types.Schema(
            type="OBJECT",
            description="Domain 7: Selection of Reported Result",
            properties={
                "judgment": types.Schema(type="STRING"),
                "rationale": types.Schema(type="STRING"),
            },
            required=["judgment", "rationale"]
        ),
        "overall_judgment": types.Schema(type="STRING"),
        "overall_rationale": types.Schema(type="STRING"),
    },
    required=["study_id", "overall_judgment", "overall_rationale"]
)
