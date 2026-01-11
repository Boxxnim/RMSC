# LLM-Based Systematic Review Extraction: Methodology

> 이 문서는 논문 작성 시 Methods 섹션 및 Supplementary Material에 활용할 수 있는 방법론 설명입니다.

---

## 1. Transparent LLM Extraction Framework

### 핵심 철학
LLM을 "black box"가 아닌 **검증 가능한 연구 도구**로 활용

### 4단계 워크플로우
```
1. Extract   → 모든 논문에서 target outcomes 추출
2. Record    → Thinking traces (reasoning process) 저장
3. Verify    → Traces 기반 human review
4. Discuss   → Ambiguous cases 연구팀 합의
```

---

## 2. Thinking Traces (Thought Signatures)

### 개념
- LLM이 데이터 추출 시 **reasoning process를 텍스트로 출력**
- Gemini API `include_thoughts=True` 옵션 사용

### 활용
1. **디버깅**: 추출 오류 원인 파악
2. **검증**: 추출 로직이 올바른지 확인
3. **교육**: 다른 연구자에게 LLM 작동 방식 설명

### 예시 (Hefler 2023)
```
"I identified the study as a Phase I/II nonrandomized clinical trial.
The paper provides subgroup data for DCD donors, and the instructions 
are clear: if subgroup data is reported, use it instead of pooled data.
I'm prioritizing DCD subgroup data from Supp Table 5..."
```

---

## 3. Prompt Engineering 전략

### 동의어 테이블
| Standard | Synonyms |
|----------|----------|
| NAS | IC, ITBL, ischemic cholangiopathy |
| MC | Clavien-Dindo ≥3, ≥IIIa, ≥IIIb |
| ACR | BPAR, acute rejection |

### 핵심 규칙
1. **NAS vs ITBL**: 둘 다 별도 보고되면 NAS 우선
2. **Supplementary 강제 확인**: Main text에서 언급된 Supp table은 반드시 확인
3. **DCD/ECD Subgroup 우선**: Mixed population에서는 subgroup 데이터 선호

---

## 4. 검증 결과

### Legacy 데이터 비교 (5 problem papers)
| Version | Match Rate |
|---------|------------|
| V1 (Original) | 60.7% (34/56) |
| V5 (Enhanced) | **96.4% (54/56)** |

### 주요 개선 사항
- 동의어 테이블 추가
- Supplementary extraction 강제
- NAS/ITBL 우선순위 규칙

---

## 5. GitHub Repository 구조 (계획)

```
llm-sr-extraction/
├── extract.py              # Main extraction script
├── prompts/
│   └── v5_prompt.md        # Current best prompt
├── examples/
│   ├── hefler_thoughts.json
│   └── debug_workflow.md
└── docs/
    └── methodology.md      # This document
```

---

## 6. 논문 인용 표현 (예시)

> "Our extraction framework provides full transparency into the LLM's reasoning process through thinking traces. This allows domain experts to verify extraction decisions and collaboratively resolve ambiguous cases, effectively transforming the AI from a black box into a transparent research assistant."
