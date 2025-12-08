---
title: "Ex vivo machine perfusion of extended criteria donor livers: a Bayesian network meta-analysis"
authors:
  - Minseok Kang
  - Nguyen Thi Huyen Trang
  - Seonju Kim
  - Ji Hyun Shin
  - Yun Kyung Jung
  - Kyung Keun Lee
  - Kyeong Sik Kim
  - Boyoung Park
  - Dongho Choi
journal: (International Journal of Surgery)
year: 2025
tags:
  - 논문노트
status: (읽는 중)
rating: 5
---

# 📝 Ex vivo machine perfusion of extended criteria donor livers: a Bayesian network meta-analysis

## Ⅰ. 기본 정보 (Bibliographic Details)
- **논문 제목 (Title):** Ex vivo machine perfusion of extended criteria donor livers: a Bayesian network meta-analysis
- **저자 (Authors):** Minseok Kang, Nguyen Thi Huyen Trang, Seonju Kim, Ji Hyun Shin, Yun Kyung Jung, Kyung Keun Lee, Kyeong Sik Kim, Boyoung Park, Dongho Choi
- **학술지 (Journal):** International Journal of Surgery
- **게재 연도 (Year):** 2025
- **DOI / URL:** 10.1097/JS9.0000000000002525

## Ⅱ. 연구 개요
- **연구 종류 (Study Type/Design):** Bayesian network meta-analysis
- **핵심 질문 (Key Questions):**
    1. 이 연구가 답하고자 하는 핵심 질문은 무엇인가?
    - Different perfusion protocols (HOPE vs NMP)
    - Cannulation techniques (single vs dual)
    - Perfusion duration (long-term vs short-term)
    - Initiation timing (donor vs recipient hospital)

## Ⅲ. PICO 분석
- **P (Patient/Problem):** Extended criteria donor (ECD) liver grafts
- **I (Intervention):** Ex vivo machine perfusion (HOPE and NMP)
- **C (Comparison):** Static cold storage (SCS), and different machine perfusion protocols compared with each other
- **O (Outcome):** Early allograft dysfunction (EAD), major complications, non-anastomotic biliary stricture (NAS), total biliary complications (TBC), acute cellular rejection (ACR), retransplantation, hepatic artery thrombosis (HAT), primary non-function (PNF), and renal replacement therapy (RRT)

## Ⅳ. 연구 방법 (Methods)
- **연구 대상 (Study Population):** Randomized controlled trials (RCTs) and matched non-randomized studies (NRSs) comparing HOPE or NMP with SCS in adult liver transplants, conducted until December 2024. The study focused on extended criteria donor (ECD) liver grafts.
- **중재/실험 설계 (Intervention/Experimental Design):** A Bayesian network meta-analysis was performed to assess the effects of varying temperature settings (hypothermic vs. normothermic), cannulation techniques (single vs. dual), and perfusion duration (short-term vs. long-term).
- **주요 측정 변수 (Primary Endpoint / Key Variables):** Early allograft dysfunction (EAD), major complications, non-anastomotic biliary stricture (NAS), total biliary complications (TBC), acute cellular rejection (ACR), retransplantation, hepatic artery thrombosis (HAT), primary non-function (PNF), and renal replacement therapy (RRT).
- **통계 분석 (Statistical Analysis):** [[Bayesian Network Meta Analysis]] was performed using the gemtc package in R Studio (v4.3.3). The deviance information criterion was used to choose between random and fixed effects models. -- [[Meta-Analysis]]

## Ⅴ. 주요 결과 (Key Findings/Results)
- HOPE is more effective than NMP in preventing EAD, TBC, NAS, and ACR in ECD grafts.
- Both single and dual HOPE are effective, and dual HOPE did not show superiority over single HOPE.
- Early initiation of NMP (long-term NMP) may prevent NAS compared to short-term NMP.
- Compared to SCS, HOPE reduced the risks of EAD, major complications, and ACR (high-certainty evidence), as well as NAS, TBC, and retransplantation (moderate-certainty evidence).
- Compared to NMP, HOPE reduced the risks of EAD, NAS, TBC, and ACR (moderate-certainty evidence).
- **핵심 도표/그림 (Key Figures/Tables):**
    - Figure 3 & 5: Forest plots summarizing the network meta-analysis. HOPE consistently shows benefits over SCS and NMP for most outcomes. Long-term HOPE shows more significant benefits than short-term HOPE.
    ![[Pasted image 20251006014950.png]]
	 ![[Pasted image 20251006015139.png]]
	- Figure 4: Single vs Dual HOPE via Network MA
	![[Pasted image 20251006015334.png]]
	* Figure2: Network map & Rankogram
	![[Pasted image 20251006015519.png]]
## Ⅵ. 한계점 (Limitations)
- The **difference between portable and non-portable devices** was not addressed.
- The analysis of graft loss and patient death was limited due to their multifactorial etiology and rarity.
- The **perfusion-to-preservation time ratio was calculated from median or mean values,** which may not fully represent the individual studies.
- The coherence assumption was weakly verified due to the lack of direct comparison studies between different machine perfusion protocols.

## Ⅶ. 나의 생각 및 연결 (My Thoughts & Connections)
- **핵심 메시지 (Take-home Message):**
    - Extended criteria donor 간 이식에서, 저온 산소 기계관류(HOPE)는 전통적인 냉장 보관(SCS)이나 정상온 기계관류(NMP)보다 주요 합병증을 줄이는 데 더 효과적인 장기 보존 전략으로 보인다.
- **나의 비판적 사고 (Critical Thoughts):**
    - 이 연구는 **간접 비교에 의존하는 네트워크 메타분석**이다. 다른 기계관류 프로토콜(예: HOPE 대 NMP) 간의 직접적인 비교 연구가 부족하다는 점이 중요한 한계이다.
    - 관류 시간을 **단순히 perfusion-to-preservation time ratio의 50번째 백분위수를 기준으로 '장기'와 '단기'로 나눈 것**은 다소 임의적이며, 임상적으로 의미 있는 차이를 반영하지 못할 수 있다.
- **연결할 노트 (Connections):**
    - [[(논문) 신장 기계관류 방식 RCT의 MA]] 
    - `[[Organ Preservation]]`
    - [[Liver Transplantation]]
    - [[의과학자 RMSC]] 
- **후속 질문 (Future Questions):**
    - **HOPE의 최적 지속 시간과 시작 시점**은 언제인가?
    - HOPE의 이점은 다양한 유형의 extended criteria donor(예: DCD 대 고령 기증자)에 걸쳐 일관되게 나타나는가?
    - **HOPE가 NMP보다 우수한 구체적인 생물학적 기전은 무엇인가?**
    - 관류 시간

## Ⅷ. 세부 분석: Long-term HOPE vs. Short-term HOPE
이 논문은 long-term HOPE와 short-term HOPE를 직접 비교한 결과도 제시합니다.

- **1. 원발성 무기능(PNF, Primary Non-Function):**
    - 가장 중요한 발견으로, Long-term HOPE가 Short-term HOPE에 비해 **PNF 발생 위험을 유의미하게 감소시킨다**는 점을 높은 확실성(high-certainty)의 근거로 확인했습니다 (Figure 5 참조).

- **2. 기타 결과 지표:**
    - PNF를 제외한 다른 주요 결과들(예: 조기 이식편 기능장애(EAD), 주요 합병증, 비문합부 담도 협착(NAS), 총 담도계 합병증(TBC) 등)에 대해서는, long-term HOPE가 short-term HOPE보다 명백히 우월하다는 근거를 찾지 못했습니다 (근거 수준이 낮거나 매우 낮음).

- **3. 결론:**
    - 따라서, 이 메타분석에서 두 그룹 간의 직접 비교를 통해 입증된 long-term HOPE의 명확한 임상적 이점은 **PNF 예방 효과**에 집중되어 있습니다.
---