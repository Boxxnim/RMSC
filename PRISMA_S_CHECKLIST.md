# PRISMA-S Checklist for LLM-Assisted Systematic Review Screening

**Study Title**: Ex vivo Machine Perfusion of Extended Criteria Donor Livers: A Systematic Review Update

**Authors**: [Author Names]

**Date Completed**: [YYYY-MM-DD]

---

## About PRISMA-S

PRISMA-S is an extension of PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) specifically for reporting literature searches. Since we use AI-assisted screening, additional transparency is required.

Reference: Rethlefsen ML, et al. PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews. Syst Rev. 2021;10(1):39.

---

## PRISMA-S Checklist Items

### DATABASE AND SOURCES

| # | Item | Checklist | Location |
|---|------|-----------|----------|
| 1 | **DATABASE NAME** | ☐ Name each database searched | Methods: Search Strategy |
| 2 | **MULTI-DATABASE SEARCHING** | ☐ If using platforms for multiple databases, report which databases on platform | Methods: Search Strategy |
| 3 | **STUDY REGISTRIES** | ☐ If any study registries were searched, report which | Methods: Search Strategy |
| 4 | **ONLINE RESOURCES AND BROWSING** | ☐ Describe any additional sources (websites, grey literature) | Methods: Search Strategy |
| 5 | **CITATION SEARCHING** | ☐ Indicate if forward/backward citation searching conducted | Methods: Search Strategy |
| 6 | **CONTACTS** | ☐ Indicate if experts/authors were contacted | Methods: Search Strategy |
| 7 | **OTHER METHODS** | ☐ Describe any other methods used to identify studies | Methods: Search Strategy |

### SEARCH STRATEGIES

| # | Item | Checklist | Location |
|---|------|-----------|----------|
| 8 | **FULL SEARCH STRATEGIES** | ☐ Include full search strategies for all databases | Appendix/Supplement |
| 9 | **LIMITS AND RESTRICTIONS** | ☐ If limits applied (date, language), report each | Methods: Search Strategy |
| 10 | **SEARCH FILTERS** | ☐ If validated search filters used, cite source | Methods: Search Strategy |
| 11 | **PRIOR WORK** | ☐ If prior reviews used as sources, cite them | Methods: Search Strategy |
| 12 | **UPDATES** | ☐ If search was updated, describe update process | Methods: Search Strategy |
| 13 | **DATES OF SEARCHES** | ☐ For each search, report date conducted | Methods: Search Strategy |

### PEER REVIEW

| # | Item | Checklist | Location |
|---|------|-----------|----------|
| 14 | **PEER REVIEW** | ☐ Describe peer review process for search strategy | Methods: Search Strategy |

### MANAGING RECORDS

| # | Item | Checklist | Location |
|---|------|-----------|----------|
| 15 | **TOTAL RECORDS** | ☐ Report total number of records identified from each source | Results: PRISMA Flow |
| 16 | **DEDUPLICATION** | ☐ Describe deduplication process | Methods: Study Selection |

---

## AI-ASSISTED SCREENING EXTENSION (Custom Section)

The following items are recommended for reporting AI-assisted screening approaches. These are not part of the official PRISMA-S but reflect emerging best practices for AI transparency.

### AI SYSTEM DESCRIPTION

| # | Item | Completed | Details |
|---|------|-----------|---------|
| AI-1 | **AI ROLE** | ☐ | Describe the role of AI in the screening process |
|   |  |   | _Our screening pipeline used AI for title/abstract screening (Layer 1 exclusion + Layer 2 inclusion verification). Final inclusion decisions were verified by human reviewers._ |
| AI-2 | **MODELS USED** | ☐ | Report model names, versions, and access dates |
|   |  |   | _Layer 1: gemini-flash-latest (Google), Layer 2: gemini-3-pro-preview (Google) + claude-sonnet-4-5-20250929 (Anthropic). Accessed [DATE]._ |
| AI-3 | **MODEL PARAMETERS** | ☐ | Report temperature, sampling, and output settings |
|   |  |   | _Temperature: 0.0 for reproducibility. Top-p: 0.95. JSON output format enforced._ |
| AI-4 | **PROMPTS** | ☐ | Make full prompts available (supplementary material) |
|   |  |   | _Complete prompts provided in Supplementary File S1 (prompts.py)._ |
| AI-5 | **CRITERIA ENCODING** | ☐ | Describe how inclusion/exclusion criteria were encoded |
|   |  |   | _See prompts.py: Layer 1 encodes 10 exclusion criteria (EXC-1 to EXC-10); Layer 2 encodes 5 inclusion criteria (INC-1 to INC-5)._ |

### AI VALIDATION

| # | Item | Completed | Details |
|---|------|-----------|---------|
| AI-6 | **DUAL-MODEL APPROACH** | ☐ | If multiple models used, describe cross-validation |
|   |  |   | _Layer 2 used two independent models (Gemini 3 Pro + Claude Sonnet 4.5) for cross-validation. Records required agreement from both models, or underwent human review._ |
| AI-7 | **INTER-MODEL AGREEMENT** | ☐ | Report agreement metrics (e.g., Cohen's κ) |
|   |  |   | _Inter-model agreement: XX.X% (Cohen's κ = 0.XX, 95% CI: X.XX-X.XX)._ |
| AI-8 | **ERROR ANALYSIS** | ☐ | Report error rates and handling |
|   |  |   | _API errors: X records (X.X%). Error cases defaulted to "pass" (conservative approach)._ |
| AI-9 | **HUMAN OVERSIGHT** | ☐ | Describe human review process |
|   |  |   | _All records marked "include" by either model underwent human verification. 10% spot-check of AI-excluded records._ |

### AI TRANSPARENCY

| # | Item | Completed | Details |
|---|------|-----------|---------|
| AI-10 | **CODE AVAILABILITY** | ☐ | Report code/pipeline availability |
|   |  |   | _Complete code available at: [Zenodo DOI]. Repository includes all scripts, prompts, and configuration._ |
| AI-11 | **REPRODUCIBILITY** | ☐ | Describe measures for reproducibility |
|   |  |   | _Temperature=0.0 for deterministic outputs. Random seed=42 for sampling. Model versions pinned._ |
| AI-12 | **COST TRANSPARENCY** | ☐ | Report API costs (optional but recommended) |
|   |  |   | _Total API cost: $X.XX. Breakdown: Layer 1 $X.XX, Layer 2 $X.XX._ |
| AI-13 | **LIMITATIONS** | ☐ | Acknowledge AI-specific limitations |
|   |  |   | _Model knowledge cutoffs may affect detection of recent publications. Abstracts lacking key details may lead to conservative "pass" decisions._ |

---

## How to Complete This Checklist

### Step 1: Fill in Study Information
- Add your author names and completion date at the top

### Step 2: Check Each Item
- For each item, mark ☐ → ☑ when addressed
- Note the location in your manuscript

### Step 3: Write the AI Extensions
- Use the example text as a template
- Customize with your actual results (fill in XX values)

### Step 4: Prepare Supplementary Materials
- **Supplementary File S1**: Complete prompts (prompts.py)
- **Supplementary File S2**: PRISMA flow diagram (include AI decision points)
- **Supplementary File S3**: Inter-model agreement analysis
- **Supplementary File S4**: Code repository information

### Step 5: Review and Finalize
- Ensure all items are addressed or marked N/A
- Have co-authors review for completeness

---

## PRISMA Flow Diagram Template (with AI)

```
                ┌─────────────────────────────────────┐
                │ Records identified from databases:  │
                │ - PubMed (n = XXX)                   │
                │ - EMBASE (n = XXX)                  │
                │ - Other (n = XXX)                   │
                └───────────────┬─────────────────────┘
                                │
                                ▼
                ┌─────────────────────────────────────┐
                │ Records after duplicates removed   │
                │ (n = 460)                          │
                └───────────────┬─────────────────────┘
                                │
                     ╔══════════════════════════╗
                     ║   AI-ASSISTED SCREENING   ║
                     ╚══════════════════════════╝
                                │
                                ▼
                ┌─────────────────────────────────────┐
                │ Layer 1: Exclusion Screening       │
                │ (Gemini Flash)                     │
                │ Records screened: 460              │
                └───────────────┬─────────────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │ Excluded (n=XXX)│         │ Passed (n=XXX)  │
        │ EXC-1: n=XX     │         │                 │
        │ EXC-2: n=XX     │         │                 │
        │ ...             │         │                 │
        └─────────────────┘         └────────┬────────┘
                                             │
                                             ▼
                ┌─────────────────────────────────────┐
                │ Layer 2: Inclusion Verification    │
                │ (Gemini Pro + Claude Sonnet)       │
                │ Records screened: XXX              │
                └───────────────┬─────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
    ┌───────────┐         ┌───────────┐         ┌───────────┐
    │Both Include│         │Disagreement│        │Both Exclude│
    │(n=XX)      │         │(n=XX)      │         │(n=XXX)    │
    └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
          │                     │                     │
          └──────────┬──────────┘                     │
                     │                                │
                     ▼                           10% spot-check
                ┌─────────────────┐                   │
                │ HUMAN REVIEW    │                   │
                │ (n=XX)          │◄──────────────────┘
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────────────────────────┐
                │ Studies included in review         │
                │ (n = XX)                           │
                └─────────────────────────────────────┘
```

---

## Journal-Specific Considerations

### If using AI for screening:

1. **Check journal policy** on AI disclosure
2. **Add AI methods section** to manuscript
3. **Cite AI models** appropriately (see Anthropic and Google citation guidelines)
4. **Submit complete prompts** as supplementary material

### Example Methods Statement:

```
Title and abstract screening was performed using a two-layer LLM-assisted 
pipeline developed for this review (code available at [Zenodo DOI]). 

Layer 1 used Gemini Flash (Google) to identify records clearly meeting 
exclusion criteria (EXC-1 through EXC-10). Records not meeting exclusion 
criteria were passed to Layer 2.

Layer 2 used two independent models—Gemini 3 Pro (Google) and Claude 
Sonnet 4.5 (Anthropic)—to verify inclusion criteria (INC-1 through INC-5) 
in parallel. Temperature was set to 0.0 for reproducibility.

All records marked as "include" by either model, plus all inter-model 
disagreements, underwent human verification. Inter-model agreement was 
XX.X% (Cohen's κ = 0.XX). A 10% random sample of AI-excluded records was 
spot-checked for quality assurance.
```

---

*This checklist template created: 2024-12-07*
*For the latest PRISMA-S guidelines, visit: https://www.prisma-statement.org/*
