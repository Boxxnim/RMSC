# Documentation Strategy for Reviewers & Publication

## 📋 Purpose

This document outlines the documentation strategy for the LLM-assisted systematic review screening pipeline, ensuring transparency, reproducibility, and compliance with PRISMA-S guidelines.

---

## 🎯 Target Audiences

1. **Journal Reviewers**: Need to assess methodological rigor
2. **Supplementary Material Readers**: Want to replicate or adapt the approach
3. **Zenodo Archive Users**: Looking for complete reproducibility package

---

## 📁 Recommended Repository Structure for Publication

```
LLM-Screening-Pipeline/
├── README.md                    # Quick start guide
├── METHODS.md                   # Detailed methodology (reviewer focus)
├── TRANSPARENCY.md              # AI transparency statement
├── LICENSE                      # CC BY 4.0
│
├── code/
│   ├── 01_parse_ris.py
│   ├── 02_layer1_exclusion.py
│   ├── 03_layer2_inclusion.py
│   ├── 04_merge_results.py
│   ├── config.py
│   └── prompts.py               # CRITICAL: Full prompts for reproducibility
│
├── data/
│   ├── input/
│   │   └── MP_Liver_Update.ris  # Original search results
│   ├── intermediate/
│   │   ├── layer1_results.csv
│   │   └── layer2_results.csv
│   └── output/
│       ├── final_screening.csv
│       └── human_review_*.csv
│
├── docs/
│   ├── PRISMA_checklist.pdf     # Completed PRISMA-S checklist
│   ├── screening_flowchart.svg  # PRISMA flow diagram
│   └── inter_model_agreement.md # Detailed agreement analysis
│
└── supplementary/
    ├── model_outputs_sample.json  # Raw API responses (sample)
    ├── cost_analysis.md           # API cost breakdown
    └── error_analysis.md          # Error rates and handling
```

---

## 📝 Key Documents to Prepare

### 1. METHODS.md (For Reviewers)

```markdown
# Detailed Methodology

## AI-Assisted Screening Framework

### Model Selection Rationale

| Model | Role | Justification |
|-------|------|---------------|
| Gemini 2.5 Flash | Layer 1 Exclusion | High speed, cost-effective for simple classification |
| Gemini 3 Pro Preview | Layer 2 Inclusion | State-of-the-art reasoning for nuanced criteria |
| Claude Sonnet 4.5 | Cross-validation | Independent vendor for bias mitigation |

### Prompt Engineering

All prompts are provided in `prompts.py` and follow these principles:
- Explicit criteria definitions with examples
- Decision logic clearly specified
- Conservative "when in doubt, include" approach
- Structured JSON output for parsing reliability

### Quality Control Measures

1. **Dual-model verification**: All Layer 2 decisions require agreement
2. **Human review triggers**: Any disagreement or inclusion flagged
3. **Temperature = 0.0**: Maximum determinism
4. **Error handling**: API failures default to "include" (safe failure)
```

### 2. TRANSPARENCY.md (AI Disclosure)

```markdown
# AI Transparency Statement

## Models Used

| Component | Provider | Model Version | Access Date |
|-----------|----------|---------------|-------------|
| Layer 1 | Google | gemini-2.5-flash | 2024-12-XX |
| Layer 2a | Google | gemini-3-pro-preview | 2024-12-XX |
| Layer 2b | Anthropic | claude-sonnet-4-5-20250929 | 2024-12-XX |

## AI Role

- **Screening assistance**: AI performed initial title/abstract screening
- **Final decisions**: All inclusions verified by human reviewers
- **Exclusions**: Sample verification conducted (10% of AI-excluded records)

## Limitations Acknowledged

1. Model knowledge cutoffs may miss recent developments
2. Abstracts lacking key details may lead to false negatives
3. Model updates may affect reproducibility over time

## Reproducibility

- All prompts provided in full
- Temperature set to 0.0 for deterministic outputs
- Random seed = 42 for any sampling operations
```

### 3. Inter-Model Agreement Analysis

```markdown
# Inter-Model Agreement Report

## Cohen's κ Calculation

| Comparison | κ | Interpretation |
|------------|---|---------------|
| Gemini 3 Pro vs Claude Sonnet 4.5 | 0.XX | Substantial/Good |

## Disagreement Analysis

| Type | Count | Resolution |
|------|-------|------------|
| Both include | XX | Human verified |
| Both exclude | XX | 10% spot-checked |
| Disagreement | XX | Human adjudicated |

## Common Disagreement Patterns

1. Abstracts with ambiguous comparator groups
2. Studies mentioning multiple organ types
3. Conference abstracts with limited methodology details
```

---

## ✅ Checklist for Submission

### Required for Main Paper

- [ ] Methods section describes AI-assisted screening approach
- [ ] Models and versions clearly stated
- [ ] Human oversight described
- [ ] Agreement metrics reported

### Required for Supplementary

- [ ] Complete prompts (prompts.py content)
- [ ] PRISMA-S checklist completed
- [ ] Screening flowchart with AI decision points
- [ ] Inter-model agreement analysis

### Recommended for Zenodo

- [ ] Full code repository
- [ ] Input RIS file (if not copyrighted)
- [ ] All intermediate CSV outputs
- [ ] Sample raw API responses

---

## 🔗 PRISMA-S Compliance Notes

When completing PRISMA-S checklist, note:

- **Item 16 (Screening)**: Describe AI-assisted screening with dual-model approach
- **Item 17 (Data extraction)**: If AI-assisted, specify here too
- **Supplementary**: Provide full prompts as per ICMJE recommendations

---

## 📊 Reporting Metrics

Include in your paper:

```
Layer 1 screening:
- Records screened: 460
- Excluded by AI: XXX (XX.X%)
- Passed to Layer 2: XXX (XX.X%)

Layer 2 verification:
- Inter-model agreement: XX.X% (κ = 0.XX)
- Both models include: XX
- Both models exclude: XX
- Disagreements: XX

Human review:
- Records reviewed: XX (all inclusions + disagreements)
- Final inclusions: XX
```

---

## 💰 Cost Transparency (Optional)

| Model | Records | Input Tokens | Output Tokens | Cost |
|-------|---------|--------------|---------------|------|
| Gemini 2.5 Flash | 460 | ~XXX,XXX | ~XX,XXX | $X.XX |
| Gemini 3 Pro Preview | XXX | ~XXX,XXX | ~XX,XXX | $X.XX |
| Claude Sonnet 4.5 | XXX | ~XXX,XXX | ~XX,XXX | $X.XX |
| **Total** | | | | **$X.XX** |

---

*This documentation strategy was created on 2024-12-07.*
