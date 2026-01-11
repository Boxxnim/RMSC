# LLM-Based Data Extraction: Prompting Techniques Documentation

## 개요

이 문서는 체계적 문헌고찰 데이터 추출에 사용된 LLM 프롬프팅 기법을 논문 Methods 섹션용으로 정리합니다.

---

## 1. 사용 모델 및 설정

| 항목 | 설정 |
|------|------|
| **Model** | Gemini 3 Flash Preview |
| **Temperature** | 0 (deterministic) |
| **Thinking Level** | High |
| **Output Format** | Structured JSON (Function Calling) |

---

## 2. 핵심 프롬프팅 기법

### 2.1 JIT Skill Injection + Dynamic Tool Switching

**개념**: 모델이 논문을 분석한 후 연구 설계(RCT/NRS)를 판단하면:
1. 해당 유형에 맞는 상세 평가 지침을 **런타임에 주입**
2. **사용 가능한 Tool을 동적으로 교체** (RCT용 or NRS용 스키마)

**워크플로우**:
```
[Phase 1: Initial - get_rob_skill만 사용 가능]
1. LLM이 PDF를 읽고 연구 설계 파악
2. LLM이 get_rob_skill(study_type="RCT") 호출

[Phase 2: Tool Switch - submit_extraction 활성화]
3. 시스템이 RoB 2 스킬 주입 + submit_extraction_rct Tool로 교체
4. LLM이 지침에 따라 평가 수행
5. LLM이 submit_extraction() 호출 (rob_rct만 required!)
```

**장점**:
- 초기 프롬프트 길이 최소화 (토큰 절약)
- 연구 유형별 맞춤 지침 제공
- **연구 유형에 맞는 스키마만 강제** (nullable 없이 필수 필드 처리)
- 모델이 스스로 필요한 도구를 호출하는 자율성 부여

### 2.2 Tool Calling (Function Calling)

**단계별 Tool 가용성**:

| 단계 | 사용 가능한 Tool |
|------|-----------------|
| **Initial** | `get_rob_skill` |
| **After RCT detected** | `submit_extraction` (rob_rct required) |
| **After NRS detected** | `submit_extraction` (rob_nrs required) |

**스키마 기반 출력**: JSON Schema로 출력 형식을 강제하여 구조화된 데이터 추출

### 2.3 Multimodal PDF-Direct Processing

**특징**: 텍스트 추출 없이 PDF를 직접 입력 → 표/그래프/이미지 정보 보존

---

## 3. 프롬프트 구조

### 3.1 System Prompt (Main Extraction)

```
You are a systematic review data extractor for liver transplantation machine perfusion studies.

## YOUR TASK
Extract ALL available data from this paper for meta-analysis and assess Risk of Bias.

## WORKFLOW
1. Read the paper carefully and determine the study design (RCT or NRS)
2. Call get_rob_skill(study_type, study_id) to get detailed RoB assessment instructions
3. Extract all data following the returned instructions
4. Call submit_extraction() with complete results

## STUDY CONTEXT
This systematic review compares:
- HOPE (Hypothermic Oxygenated Perfusion) vs SCS (Static Cold Storage)
- NMP (Normothermic Machine Perfusion) vs SCS
- In extended criteria donor (ECD) liver transplantation

## IMPORTANT
- Use null for missing values
- Include source_location for all extracted data points
- For RCT studies, complete rob_rct in submit_extraction
- For NRS studies, complete rob_nrs in submit_extraction
```

### 3.2 RoB 2 Skill (RCT용)

| Domain | Signaling Questions |
|--------|---------------------|
| D1. Randomization | Random sequence, Allocation concealment, Baseline differences |
| D2. Deviations | Blinding, Deviations, ITT analysis |
| D3. Missing Data | Data availability, Missingness bias |
| D4. Measurement | Assessor blinding, Objective outcome |
| D5. Selection | Pre-registration, Selective reporting |

### 3.3 ROBINS-I Skill (NRS용)

| Domain | Key Assessment Points |
|--------|----------------------|
| D1. Confounding | PSM, IPTW, key confounders (donor age, DRI, MELD, CIT) |
| D2. Selection | Exclusion criteria, selection bias |
| D3. Classification | Intervention definition, prospective vs retrospective |
| D4. Deviations | Co-interventions, switches |
| D5. Missing Data | Differential loss, completeness |
| D6. Measurement | Assessor awareness, objective vs subjective |
| D7. Selection | Selective reporting, multiple analyses |

---

## 4. 데이터 추출 스키마

### 4.1 Study Characteristics (필수)
- study_id, first_author, year, study_design
- intervention_type (HOPE/NMP/DHOPE/SNMP)
- n_intervention, n_control, n_total
- donor_type (DCD/DBD/ECD-DBD/Mixed)

### 4.2 Clinical Outcomes (15개)

| 유형 | Outcomes |
|------|----------|
| **Binary** | EAD, NAS, TBC, ACR, PNF, HAT, Retx, RRT, AKI, PRS, Major Complications |
| **Survival** | 1yr Graft Survival, 1yr Patient Survival |
| **Continuous** | Hospital Stay, ICU Stay |

**각 outcome별 추출 항목**:
- reported (boolean)
- definition
- intervention_events / intervention_total
- control_events / control_total
- effect estimate (RR/OR/HR)
- 95% CI, p-value
- source_location

---

## 5. 기술적 특징 요약

| 기법 | 설명 | 논문 기재 용어 |
|------|------|----------------|
| **JIT Skill Injection** | 런타임 맞춤 지침 주입 | Dynamic Skill Injection |
| **Dynamic Tool Switching** | 연구 유형에 따른 Tool 동적 교체 | Adaptive Schema Selection |
| **Tool Calling** | 구조화된 함수 호출 | Function Calling / Tool Use |
| **Multimodal Input** | PDF 직접 처리 | Multimodal Document Understanding |
| **Schema-Enforced Output** | JSON Schema 기반 출력 | Structured Output Generation |
| **Extended Thinking** | 고수준 추론 모드 | Chain-of-Thought Reasoning |

---

## 6. 재현성 (Reproducibility)

- **Model**: Gemini 3 Flash Preview (2025.01)
- **Temperature**: 0 (deterministic)
- **Code**: `Info_extractor/extractor_gemini.py`
- **Skills**: `Info_extractor/skills.py`
- **Schema**: `Info_extractor/tool_definitions.py`

---

*작성일: 2025-01-09*
