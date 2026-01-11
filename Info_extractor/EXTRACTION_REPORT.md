# 데이터 추출 종합 보고서

## 1. 연구 개요

| 항목 | 값 |
|------|-----|
| **총 연구 수** | 34개 |
| 기존 논문 | 21개 |
| 새 논문 | 13개 |
| **총 환자 수** | 6,597명 |

### Study Design
| Design | N |
|--------|---|
| RCT | 14 |
| Retrospective cohort | 17 |
| Prospective cohort | 3 |

### Intervention Type
| Type | N |
|------|---|
| HOPE | 21 |
| NMP | 12 |
| Mixed | 1 |

---

## 2. Outcome Reporting

| Outcome | 기존 (21) | 새 (13) | 전체 (34) |
|---------|-----------|---------|-----------|
| PNF | 18/21 | 8/13 | 26/34 |
| ReTx | 16/21 | 8/13 | 24/34 |
| TBC | 17/21 | 6/13 | 23/34 |
| EAD | 17/21 | 5/13 | 22/34 |
| HAT | 16/21 | 6/13 | 22/34 |
| NAS | 15/21 | 6/13 | 21/34 |
| MC | 13/21 | 6/13 | 19/34 |
| ACR | 11/21 | 7/13 | 18/34 |
| RRT | 14/21 | 2/13 | 16/34 |
| Survival | 19/21 | 12/13 | 31/34 |

---

## 3. Follow-up Duration

| 구분 | 기존 | 새 |
|------|------|-----|
| Median | 12개월 | **24개월** |
| Range | 3-60개월 | 12-62개월 |

> 새 논문들의 Long-term follow-up 증가

---

## 4. Cohort Overlap 분석

### 4.1 NCT Registry Clusters
| NCT | Trial | Papers |
|-----|-------|--------|
| NCT02584283 | DHOPE-DCD | vanRijn_2021, vanRijn_2025, Endo_2025 |
| NCT03124641 | HOPE-ECD | Czigany_2021, Czigany_2024 |
| NCT04812054 | - | Grat_2023, Morawski_2024 |

### 4.2 Database Overlaps
| Database | Papers | 주의사항 |
|----------|--------|----------|
| **UNOS** | Okumura_2024, Wang_2024, Shu_2025 | ⚠️ 미국 환자 중복 |

### 4.3 Center Clusters
| Center | Papers |
|--------|--------|
| Zurich | Dutkowski_2015, Eden_2025, Schlegel_2019 |
| Birmingham | Dutkowski_2015, Mergental_2020, Schlegel_2019 |
| London | Elgosbi_2025, Jassem_2019, Nasralla_2018 |
| Groningen/Leiden | Endo_2025, vanRijn_2021, vanRijn_2025 |

---

## 5. 새 논문 상세 (13개)

| Study | Design | Intervention | Donor | FU |
|-------|--------|--------------|-------|-----|
| Coquelle_2025 | NRS | HOPE | ECD-DBD | 62mo |
| vanRijn_2025 | RCT* | HOPE | DCD | 60mo |
| Elgosbi_2025 | RCT* | HOPE | Mixed | 55mo |
| Czigany_2024 | RCT* | HOPE | ECD-DBD | 48mo |
| DeStefano_2025 | NRS | HOPE | Mixed | 32mo |
| Morawski_2024 | RCT* | HOPE | ECD-DBD | 24mo |
| Okumura_2024 | NRS | NMP | DCD | 24mo |
| Shu_2025 | NRS | Mixed | Mixed | 24mo |
| Lesurtel_2025 | **RCT** | HOPE | ECD-DBD | 12mo |
| Wang_2024 | NRS | NMP | Mixed | 12mo |
| Corcione_2025 | NRS | HOPE | ECD-DBD | 12mo |
| Eden_2025 | NRS | HOPE | DBD | - |
| Endo_2025 | RCT* | HOPE | DCD | - |

> *RCT*: Post-hoc/Follow-up analysis  
> **RCT**: New independent trial

---

## 6. 향후 수정 필요사항

1. **ECD subgroup 우선 추출**: 프롬프트 강화 필요
2. **Matched cohort 우선**: NRS에서 matched data 사용
3. **Survival 형식**: n/N 형식으로 스키마 수정
