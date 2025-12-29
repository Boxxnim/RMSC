# Machine Perfusion Data Extractor v2

Systematic Review를 위한 LLM 기반 데이터 추출 도구입니다.
Kang et al. (2025) 메타분석 업데이트용으로 설계되었습니다.

## 설치

```bash
# 1. 필요한 패키지 설치
pip install -r requirements.txt

# 2. API 키 설정
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows의 경우:
set ANTHROPIC_API_KEY=your-api-key-here
```

## 사용법

### 기본 사용 (단일 논문)
```bash
python extractor_v2.py -i paper.pdf -o results.xlsx
```

### Supplementary 파일과 함께
```bash
# 단일 supplementary
python extractor_v2.py -i paper.pdf -s supplementary.pdf -o results.xlsx

# 여러 supplementary 파일
python extractor_v2.py -i paper.pdf -s supp1.pdf supp2.pdf -o results.xlsx
```

### Quick Screen만 (Eligibility 확인)
```bash
python extractor_v2.py -i paper.pdf --quick
```

### JSON도 함께 저장
```bash
python extractor_v2.py -i paper.pdf -o results.xlsx --json
```

### 배치 처리 (폴더 내 모든 PDF)
```bash
python extractor_v2.py -i ./papers_folder/ -o results.xlsx --batch
```

## 옵션 전체 목록

| 옵션 | 단축 | 설명 |
|------|------|------|
| `--input` | `-i` | 입력 파일 또는 폴더 (필수) |
| `--supplementary` | `-s` | Supplementary 파일들 |
| `--output` | `-o` | 출력 Excel 파일 (기본: extraction_results.xlsx) |
| `--template` | `-t` | 템플릿 Excel 파일 |
| `--model` | `-m` | Claude 모델 (기본: claude-sonnet-4-20250514) |
| `--quick` | | Quick screen만 실행 |
| `--no-rob` | | RoB 추출 건너뛰기 |
| `--batch` | | 배치 처리 모드 |
| `--json` | | JSON 파일도 저장 |

## 출력 Excel 구조 (8개 시트)

1. **Study_Characteristics**: 연구 기본 정보 (저자, 연도, 국가, 디자인 등)
2. **Perfusion_Settings**: 관류 설정 (장치, 온도, 용액 등)
3. **Time_Metrics**: 시간 지표 (CIT, WIT, 관류 시간 등)
4. **Outcome_Data**: 11개 이진 결과 (EAD, NAS, TBC, MC, ACR, PNF, HAT, ReTx, AKI, RRT, PRS)
5. **Continuous_Outcomes**: 연속형 결과 (재원일수, ICU, 생존율, 이용률)
6. **RoB2_Assessment**: RCT용 Risk of Bias 평가
7. **ROBINS_I_Assessment**: NRS용 Risk of Bias 평가
8. **Extraction_Notes**: 추출 관련 메모

## Source Citation 기능

모든 outcome 데이터에는 다음 필드가 포함됩니다:
- `source_quote`: 원문에서 발췌한 인용문
- `source_location`: 데이터 위치 (예: "Table 2", "Figure 3", "Page 5")

이를 통해 추출된 데이터를 원본 논문과 대조 검증할 수 있습니다.

## 파일 구조

```
extractor_package/
├── extractor_v2.py              # 메인 스크립트
├── schemas_v2_data_collection.py # JSON 스키마 정의
├── prompts_v2_data_collection.py # LLM 프롬프트
├── pdf_utils.py                  # PDF 처리 유틸리티
├── data_extraction_template_v2.xlsx # Excel 템플릿
├── requirements.txt              # Python 의존성
└── README.md                     # 이 파일
```

## 추출 대상 Outcomes (Kang et al. 기준)

### Binary Outcomes (11개)
- EAD (Early Allograft Dysfunction)
- NAS (Non-Anastomotic Stricture)
- TBC (Total Biliary Complications)
- Major Complications (Clavien-Dindo ≥3)
- ACR (Acute Cellular Rejection)
- PNF (Primary Non-Function)
- HAT (Hepatic Artery Thrombosis)
- Retransplantation
- AKI (Acute Kidney Injury)
- RRT (Renal Replacement Therapy)
- PRS (Post-Reperfusion Syndrome)

### Continuous Outcomes
- Hospital Stay (days)
- ICU Stay (days)
- 1-Year Graft Survival
- 1-Year Patient Survival
- Utilization Rate

## 문제 해결

### API 키 오류
```
Error: ANTHROPIC_API_KEY environment variable not set
```
→ API 키를 환경변수로 설정하세요.

### PDF 읽기 오류
```
Error reading PDF
```
→ pymupdf가 설치되어 있는지 확인하세요: `pip install pymupdf`

### 템플릿 파일 오류
```
Template file not found
```
→ `data_extraction_template_v2.xlsx`가 같은 폴더에 있는지 확인하세요.

## 참고

- 모델: Claude Sonnet 4 사용 (비용 효율적, 충분한 성능)
- 한 논문당 약 3회 API 호출 (quick screen + full extraction + RoB)
- Supplementary 포함 시 토큰 사용량 증가 주의
