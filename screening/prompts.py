"""
Prompt Templates for Systematic Review Screening
================================================

Layer 1: Exclusion screening (Gemini Flash)
Layer 2: Inclusion verification (Gemini Pro + Claude Sonnet)
"""

LAYER1_EXCLUSION_PROMPT = """# LAYER 1: EXCLUSION SCREENING

You are performing first-pass screening for a systematic review update on ex vivo machine perfusion in extended criteria donor liver transplantation.

Reference: Kang et al. "Ex vivo machine perfusion of extended criteria donor livers: a Bayesian network meta-analysis" (Int J Surg 2025)

Your ONLY task is to identify records that should be EXCLUDED.

## EXCLUSION CRITERIA (from PDF Methods & Figure 1)

From PDF Methods:
> "Non-comparative, non-human, multi-organ transplant studies, and studies with combinatorial perfusion methods were excluded."

From PDF Figure 1 (PRISMA):
> Excluded: Unmatched cohort study (n=6), Heterogenous perfusion technique (n=5), Insufficient data (n=5), Retransplanted patient population (n=1)

| Tag | Criterion | Key terms |
|-----|-----------|-----------|
| EXC-1 | Non-human study | porcine, rat, mouse, canine, swine, rabbit, sheep, pig, rodent, animal model |
| EXC-2 | Multi-organ transplant only | kidney/heart/lung transplant WITHOUT liver |
| EXC-3 | Combinatorial perfusion | sequential HOPE then NMP, NMP then HOPE, combined perfusion |
| EXC-4 | Retransplantation population | retransplantation only, re-LT only |
| EXC-5 | Review/meta-analysis | systematic review, meta-analysis, narrative review |
| EXC-6 | Editorial/letter/commentary | editorial, letter to editor, commentary, correspondence |
| EXC-7 | Case report | case report, single case, <5 patients |
| EXC-8 | Conference abstract only | abstract only, meeting abstract |
| EXC-9 | Pediatric only | pediatric, children, infant, neonatal |
| EXC-10 | Insufficient data | no abstract, protocol only |

## IMPORTANT CLARIFICATIONS

- EXC-2: If study includes liver (even with other organs), do NOT exclude
- EXC-3: Single perfusion method (HOPE or NMP alone) is NOT exclusion
- EXC-4: If retransplantation is part of a larger cohort, do NOT exclude
- NON-COMPARATIVE studies: Pass to Layer 2 for study design verification (not excluded at Layer 1)

## DECISION LOGIC

- If ANY exclusion criterion is CLEARLY met → "exclude"
- If UNCERTAIN whether exclusion applies → "pass" (let Layer 2 decide)
- If NO exclusion criterion applies → "pass"

⚠️ CRITICAL: When in doubt, choose "pass". Better to pass an irrelevant study than wrongly exclude a relevant one.

## OUTPUT FORMAT

Respond with valid JSON only:

{{
  "decision": "exclude" | "pass",
  "exclusion_tags": ["EXC-1"],
  "evidence": "exact quote from title or abstract",
  "reasoning": "brief explanation"
}}

If decision is "pass":
{{
  "decision": "pass",
  "exclusion_tags": [],
  "evidence": null,
  "reasoning": "No clear exclusion criteria met"
}}

---

TITLE: {title}

ABSTRACT: {abstract}
"""


LAYER2_INCLUSION_PROMPT = """# LAYER 2: INCLUSION VERIFICATION

This record passed Layer 1 exclusion screening. Your task is to verify whether ALL inclusion criteria are met for a systematic review update on ex vivo machine perfusion in extended criteria donor liver transplantation.

Reference: Kang et al. "Ex vivo machine perfusion of extended criteria donor livers: a Bayesian network meta-analysis" (Int J Surg 2025)

## ORIGINAL STUDY CRITERIA (from Methods section)

> "Randomized controlled trials (RCTs), matched non-randomized studies (NRSs) comparing HOPE or NMP with SCS in adult liver transplants were included."

## INCLUSION CRITERIA

| Tag | Criterion | Definition from PDF |
|-----|-----------|---------------------|
| INC-1 | Study design | RCTs OR matched non-randomized studies (NRSs) |
| INC-2 | Intervention | HOPE (hypothermic oxygenated perfusion) OR NMP (normothermic machine perfusion) |
| INC-3 | Comparator | SCS (static cold storage) |
| INC-4 | Population | Adult liver transplants |
| INC-5 | Donor type | ECD (extended criteria donor) - includes DCD, high DRI, donor-specific indications |

---

## EVALUATION GUIDELINES

### INC-1: Study Design

**"yes":** RCT, randomized, propensity score matching, matched cohort, matched pairs
**"no":** Unmatched cohort study, retrospective cohort WITHOUT matching, registry study without PSM
**"unclear":** Matching implied but not explicit (rare)

### INC-2: Intervention

**"yes":** HOPE, HMP, D-HOPE (dual), NMP, ex vivo machine perfusion
**"no":** NRP alone, in-situ perfusion, combinatorial perfusion (HOPE+NMP sequential)

### INC-3: Comparator


**"yes":** SCS, static cold storage, cold storage, conventional preservation
**"no":** No control group, HOPE vs NMP without SCS arm

### INC-4: Population

**"yes":** Adult liver transplantation, deceased donor LT
**"no":** Pediatric, multi-organ transplant without liver, retransplantation only

### INC-5: Donor Type

**"yes":** ECD, DCD (donation after circulatory death), high DRI, marginal donor, steatotic liver, elderly donor
**"no":** Only standard/optimal DBD donors explicitly
**"unclear":** Donor criteria not specified

---

## DECISION LOGIC

| Scenario | Decision |
|----------|----------|
| All criteria "yes" | include (high confidence) |
| Mix of "yes"/"unclear", no "no" | include (low confidence) |
| Any criterion is "no" | exclude |

⚠️ INC-1 (study design) is critical: Unmatched cohort studies MUST be excluded.

---

## OUTPUT FORMAT

Respond with valid JSON only:

{{
  "inclusion_check": {{
    "INC-1": {{"status": "yes|unclear|no", "evidence": "quote or null"}},
    "INC-2": {{"status": "yes|unclear|no", "evidence": "quote or null"}},
    "INC-3": {{"status": "yes|unclear|no", "evidence": "quote or null"}},
    "INC-4": {{"status": "yes|unclear|no", "evidence": "quote or null"}},
    "INC-5": {{"status": "yes|unclear|no", "evidence": "quote or null"}}
  }},
  "decision": "include" | "exclude",
  "confidence": "high" | "low",
  "reasoning": "one sentence summary"
}}

---

TITLE: {title}

ABSTRACT: {abstract}
"""


def format_layer1_prompt(title: str, abstract: str) -> str:
    """Format Layer 1 prompt with title and abstract."""
    if not abstract or abstract.strip() == "":
        abstract = "[No abstract available]"
    return LAYER1_EXCLUSION_PROMPT.format(title=title, abstract=abstract)


def format_layer2_prompt(title: str, abstract: str) -> str:
    """Format Layer 2 prompt with title and abstract."""
    if not abstract or abstract.strip() == "":
        abstract = "[No abstract available]"
    return LAYER2_INCLUSION_PROMPT.format(title=title, abstract=abstract)
