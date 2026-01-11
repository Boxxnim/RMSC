# LLM-Based Data Extraction: Challenges & Lessons Learned

> 이 문서는 간이식 기계관류 메타분석을 위한 LLM 기반 데이터 추출 과정에서 직면한 문제점들을 정리한 것입니다.

## 1. 임상 용어의 이질성 (Terminology Heterogeneity)

### 동일 outcome, 다양한 표현
| Target | 실제 논문에서 사용된 표현들 |
|--------|---------------------------|
| **NAS** | IC, ITBL, ischemic cholangiopathy, non-anastomotic stricture |
| **MC** | Clavien-Dindo ≥3, ≥3a, ≥3b, "severe complications" |
| **EAD** | Olthoff criteria, modified Olthoff, 기관별 정의 |

**문제점**: Rule-based synthesis가 어려움. 동일 개념을 다른 용어로 보고하여 자동 매핑이 실패함.

---

## 2. Cohort 선택의 복잡성

### 한 논문 내 여러 코호트 존재
| 논문 | 가용 코호트 |
|------|------------|
| Hefler 2023 | Full (386 vs 79), Matched 1:1 (79 vs 79), DCD subgroup (51 vs 16) |
| Wehrle 2024 | DCD (74 vs 37), E-DBD (236 vs 118) |

**문제점**: 어떤 코호트를 추출해야 하는지 명시적 가이드 없이는 LLM이 일관된 선택 불가능.

---

## 3. 테이블 구조 문제

### 3.1 셀 내 중첩 데이터
```
Biliary complications at 1yr | 18 (35.3)   | 7 (43.8)
  Anastomotic stricture      | 10 (19.6)   | 6 (37.5)  
  Leak                       | 6 (11.8)    | 0 (0.0)
```
- 한 셀에 여러 값이 줄바꿈으로 구분됨
- NAS = TBC - AS - Leak **역산 필요** (직접 보고 안 됨)

### 3.2 Supplementary 파일
- 핵심 subgroup 데이터가 supplementary에만 존재
- 형식 다양 (DOCX, PDF), 품질 불균일

---

## 4. 정의 불일치

| 항목 | Paper A | Paper B |
|------|---------|---------|
| Follow-up | 1 year | 90 days |
| MC threshold | CD ≥3b | CD ≥3a |
| NAS | directly reported | calculated from TBC |

---

## 5. 제안된 해결 방안

1. **Multi-mention extraction**: 모든 언급을 캡처 후 후처리에서 선택
2. **Definition 명시적 기록**: 각 outcome의 정의를 함께 추출
3. **Uncertainty flagging**: 애매한 케이스는 human review로 전달
4. **동의어 사전**: NAS ↔ IC ↔ ITBL 매핑 테이블 구축

---

## 6. 시사점

- **완전 자동화는 한계 존재**: 임상적 판단 필요한 edge case 다수
- **Human-in-the-loop 필수**: 특히 cohort 선택, 정의 매핑에서
- **Outcome ontology 필요**: 표준화된 용어집이 이질성 감소에 도움
