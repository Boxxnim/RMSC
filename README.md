# LLM-Assisted Systematic Review Screening

Multi-model screening pipeline for systematic review title/abstract screening.

## Overview

This pipeline implements a two-layer screening approach for systematic reviews:

1. **Layer 1 (Exclusion)**: Gemini 2.5 Flash identifies clearly excludable records
2. **Layer 2 (Inclusion)**: Gemini 3 Pro Preview + Claude Sonnet 4.5 verify inclusion criteria
   - ⚡ **100 records processed in parallel** for maximum throughput

## Study Context

**Systematic Review Update**: Ex vivo machine perfusion of extended criteria donor livers

**Original Study**: Kang et al. (2025) International Journal of Surgery
- DOI: 10.1097/JS9.0000000000002525

## Pipeline Architecture

```
                    460 records (EndNote RIS)
                           │
                           ▼
    ┌──────────────────────────────────────────────┐
    │         01_parse_ris.py                      │
    │         Parse RIS → CSV                      │
    └──────────────────────┬───────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────┐
    │         02_layer1_exclusion.py               │
    │         Gemini 2.5 Flash                     │
    │         Exclusion screening (EXC-1 to 10)    │
    └──────────────────────┬───────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
         EXCLUDE                      PASS
         (done)                         │
                                        ▼
    ┌──────────────────────────────────────────────┐
    │         03_layer2_inclusion.py               │
    │         Gemini 3 Pro + Claude Sonnet 4.5     │
    │         Inclusion verification (INC-1 to 5)  │
    │         ⚡ 100 RECORDS PARALLEL BATCH         │
    └──────────────────────┬───────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────┐
    │         04_merge_results.py                  │
    │         Final decisions + Human review list  │
    └──────────────────────────────────────────────┘
```

## Criteria

### Exclusion Criteria (Layer 1)

| Tag | Criterion |
|-----|-----------|
| EXC-1 | Animal study |
| EXC-2 | Pediatric population |
| EXC-3 | Non-liver organ only |
| EXC-4 | Non-comparative design |
| EXC-5 | Combined perfusion (HOPE+NMP) |
| EXC-6 | NRP alone without ex vivo MP |
| EXC-7 | Review/meta-analysis |
| EXC-8 | Editorial/letter/commentary |
| EXC-9 | Case report (<5 cases) |
| EXC-10 | Conference abstract only |

### Inclusion Criteria (Layer 2)

| Tag | Criterion |
|-----|-----------|
| INC-1 | RCT or matched comparative study |
| INC-2 | HOPE or NMP intervention |
| INC-3 | SCS comparator |
| INC-4 | Adult liver transplantation |
| INC-5 | ECD or DCD donor |

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install google-generativeai anthropic pandas tqdm
```

## Usage

### 1. Set API Keys

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 2. Parse RIS File

```bash
python 01_parse_ris.py MP_Liver_Update.ris screening_records.csv
```

### 3. Layer 1: Exclusion Screening

```bash
python 02_layer1_exclusion.py screening_records.csv layer1_results.csv
```

### 4. Layer 2: Inclusion Verification

```bash
# Default: 100 records per batch
python 03_layer2_inclusion.py layer1_results.csv layer2_results.csv

# Custom batch size
python 03_layer2_inclusion.py layer1_results.csv layer2_results.csv --batch 50
```

### 5. Merge Results

```bash
python 04_merge_results.py layer2_results.csv final_screening
```

### Resume After Interruption

```bash
python 02_layer1_exclusion.py input.csv output.csv --resume 150
```

## Output Files

| File | Description |
|------|-------------|
| `screening_records.csv` | Parsed records from RIS |
| `layer1_results.csv` | After Layer 1 exclusion |
| `layer2_results.csv` | After Layer 2 verification |
| `final_screening.csv` | Complete results |
| `final_screening_summary.txt` | Statistics summary |
| `final_screening_human_review_high.csv` | Records needing review |
| `final_screening_human_review_low_sample.csv` | Spot-check sample |

## CSV Schema

### Layer 1 Columns

```
L1_decision          # exclude / pass
L1_exclusion_tags    # e.g., "EXC-1,EXC-7"
L1_evidence          # Quote from abstract
L1_reasoning         # Explanation
```

### Layer 2 Columns (per model)

```
L2_{model}_decision      # include / exclude
L2_{model}_confidence    # high / low
L2_{model}_reasoning     # Summary
L2_{model}_inc{N}_status    # yes / unclear / no
L2_{model}_inc{N}_evidence  # Quote
```

### Agreement & Review

```
L2_models_agree      # TRUE / FALSE
needs_human_review   # TRUE / FALSE
auto_decision        # include / exclude / uncertain
review_priority      # high / low / none
```

## Model Configuration

| Layer | Model | Temperature | Purpose |
|-------|-------|-------------|---------|
| 1 | Gemini 2.5 Flash | 0.0 | Fast exclusion |
| 2 | Gemini 3 Pro Preview | 0.0 | Inclusion verification (state-of-the-art) |
| 2 | Claude Sonnet 4.5 | 0.0 | Cross-validation (100 parallel batches) |

## Reproducibility

- Temperature = 0.0 for all models
- Top_p = 0.95
- Random seed for sampling: 42
- All prompts stored in `prompts.py`

## Methods Statement (for paper)

```
Title and abstract screening was performed using a two-layer 
LLM-assisted pipeline. Layer 1 used Gemini 2.5 Flash (Google) 
to identify records meeting exclusion criteria. Layer 2 used 
Gemini 3 Pro Preview (Google) and Claude Sonnet 4.5 (Anthropic),
processing 100 records in parallel batches to verify inclusion 
criteria. Temperature was set to 0.0 for reproducibility. 
All records marked as "include" by either model, plus all 
disagreements, underwent human verification. Inter-model 
agreement was calculated using Cohen's κ. Complete prompts 
and code are available at [Zenodo DOI].
```

## License

CC BY 4.0

## Citation

[To be added after Zenodo upload]
