# LLM-based Study Data Extraction Pipeline

Systematic review data extraction for **Ex vivo Machine Perfusion in ECD Liver Transplantation**

## Overview

이 파이프라인은 LLM API를 활용하여:
1. 논문에서 구조화된 데이터 추출 (Study Registry)
2. PICO 기준에 따른 eligibility 자동 판정 (Eligibility Log)
3. Dual verification으로 추출 품질 검증
4. 결과를 Excel 템플릿에 자동 기록

## Setup

### 1. Dependencies

```bash
pip install anthropic google-generativeai openpyxl PyMuPDF
```

### 2. API Keys

```bash
export ANTHROPIC_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
```

### 3. Template

`cohort_tracking_template_v3.xlsx` 파일이 작업 디렉토리에 있어야 합니다.

## Usage

### Single Paper

```bash
python extractor.py --input paper.txt --output results.xlsx
```

### Batch Processing

```bash
python extractor.py --input papers_folder/ --output results.xlsx --batch
```

### Skip Validation (faster, less accurate)

```bash
python extractor.py --input paper.txt --output results.xlsx --no-validate
```

## Pipeline Flow

```
PDF/Text Input
      ↓
┌─────────────────┐
│  Claude (Extract)│  ← Primary extraction
└────────┬────────┘
         ↓
┌─────────────────┐
│  Gemini (Validate)│  ← Cross-validation
└────────┬────────┘
         ↓
   ┌─────┴─────┐
   │ Agreement? │
   └─────┬─────┘
     Yes │ No
         ↓   ↓
   Auto-accept  Flag for manual review
         ↓
   Write to Excel
```

## Output Structure

### Study Registry Sheet
- 기본 서지 정보
- 연구 설계, 기관, 등록번호
- 샘플 사이즈, intervention 정보

### Eligibility Log Sheet
- Include/Exclude/Pending 결정
- Exclusion category 분류
- PICO violation 명시
- 판단 근거 (rationale)
- Precedent/guideline 참조

### Color Coding
- 🟢 녹색: Include
- 🔴 빨간색: Exclude  
- 🟡 노란색: Pending / Manual review needed

## Key Exclusion Triggers

파이프라인이 자동으로 감지하여 exclude하는 패턴:

### Co-interventions
- tPA / alteplase / thrombolytic therapy during perfusion
- Defatting cocktails
- Stem cell therapy
- Gene therapy

### Selection Bias
- FMN-guided discard decisions
- Viability criteria that change utilization rates
- Any selection mechanism that differs between groups

### Protocol Issues
- Sequential/combined perfusion (HOPE → NMP)
- Non-standard temperature protocols
- Ischemia-free liver transplantation (IFLT)

## Customization

### Adding New Exclusion Criteria

`config.toml`에서:

```toml
[eligibility]
auto_exclude_co_interventions = [
    "tPA",
    "alteplase",
    "your_new_trigger"  # 추가
]
```

### Modifying Prompts

`prompts.py`의 `SYSTEM_PROMPT`와 템플릿을 수정하여 추출 로직 변경 가능

### Custom Output Fields

`schemas.py`에서 JSON schema 수정 후 `extractor.py`의 `write_*` 메서드 업데이트

## Quality Control

### Dual Verification
- Model A (Claude): Primary extraction
- Model B (Gemini): Validation
- 불일치 시 자동으로 "Pending" + manual review flag

### Confidence Levels
- **High**: 명확한 데이터, 모델 간 일치
- **Medium**: 일부 추론 필요, 대체로 일치
- **Low**: 불완전한 데이터, 모델 간 불일치

### Manual Review Queue
`Reviewer Confirmed = "No"` 인 항목들은 수동 검토 필요

## Integration with Existing Workflow

기존 screening 파이프라인과 통합:

```python
# After Layer 2 screening passes
from extractor import process_paper, ExcelWriter

writer = ExcelWriter("template.xlsx", "output.xlsx")

for paper in passed_layer2_screening:
    results = process_paper(
        paper_content=paper.text,
        paper_id=paper.id,
        excel_writer=writer
    )
    
writer.save()
```

## Limitations

1. **PDF Extraction**: 현재 텍스트 파일만 지원. PDF는 PyMuPDF 등으로 전처리 필요
2. **Table Data**: 복잡한 테이블의 수치 추출은 정확도 낮을 수 있음
3. **Language**: 영어 논문에 최적화됨

## Troubleshooting

### "No JSON found in response"
- 모델 응답이 JSON 형식이 아님
- `max_tokens` 늘리거나 재시도

### Validation Disagreement
- 정상적인 경우도 있음 (모델 간 해석 차이)
- Manual review로 최종 판단

### API Rate Limits
- Batch 처리 시 적절한 delay 추가
- `config.toml`에서 retry 설정 조정

## References

- Kang et al. (2025) - Reference meta-analysis methodology
- Cochrane Handbook Section 5.3 - Overlapping cohort handling
- PRISMA-DFLLM guidelines - LLM-assisted systematic reviews
