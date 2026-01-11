#!/usr/bin/env python3
"""
Test v2.0 Comprehensive Extraction Prompt
Tests the new mentions-based extraction on problem papers.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from google import genai
from google.genai import types

# Test papers (problem cases from batch 1) - using study IDs
TEST_STUDIES = [
    "Hefler_2023",      # cohort selection - 0/14 match
    "Wehrle_2024",      # N mismatch
    "Panayotova_2024",  # N mismatch  
    "Dutkowski_2015",   # MC None
    "Fodor_2021",       # TBC number difference
]

V2_PROMPT = '''# Comprehensive Outcome Extraction Prompt (v2.0)

## Role

You are a precise data extractor for liver transplantation meta-analysis. Your task is to find **ALL mentions** of clinical outcomes in the provided document(s) and extract n/N event data from each mention.

---

## Target Outcomes & Definitions

Extract all mentions of the following outcomes. **Note synonyms carefully - they refer to the same outcome.**

| Standard Name | Synonyms / Alternative Terms | Standard Definition |
|---------------|------------------------------|---------------------|
| **EAD** | Early graft dysfunction, EGD | Bilirubin ≥10 mg/dL or INR >1.6 on day 7, or ALT/AST >2000 IU/L in first 7 days (Olthoff criteria) |
| **PNF** | Primary graft non-function | Irreversible graft dysfunction leading to death/retransplant within 7-10 days |
| **NAS** | **IC, ITBL, ischemic cholangiopathy, ischemic-type biliary lesion, non-anastomotic stricture** | Stricture/dilation of bile ducts on MRCP, excluding anastomotic strictures, with patent vasculature |
| **TBC** | BC, biliary complications, biliary morbidity | Total biliary complications (includes AS + Leak + NAS) |
| **HAT** | HA thrombosis, hepatic artery occlusion | Hepatic artery thrombosis |
| **ACR** | BPAR, acute rejection, rejection episode, treated rejection | Acute cellular rejection (biopsy-proven or treated) |
| **AKI** | Acute kidney failure | Based on RIFLE or KDIGO criteria |
| **RRT** | CRRT, dialysis, renal replacement | Need for renal replacement therapy |
| **MC** | Clavien-Dindo ≥3, ≥3a, ≥3b, ≥IIIa, ≥IIIb, grade 3+, severe complications | Major surgical complications requiring intervention. **FALLBACK**: If Clavien-Dindo not used, look for IC/NAS with retransplantation as proxy for major complications |
| **PRS** | Post-reperfusion syndrome | MAP decrease ≥30% within 5 min after reperfusion |
| **Retx** | Retransplantation, re-LT, regraft | Need for liver retransplantation |
| **Graft Survival** | Graft survival, liver graft survival | Graft still functioning (extract at ALL available timepoints: 30d, 90d, 1yr, 3yr, 5yr) |
| **Patient Survival** | Patient survival, overall survival, mortality | Patient alive (extract at ALL available timepoints: 30d, 90d, 1yr, 3yr, 5yr) |

> **Survival Timepoints**: For Graft Survival and Patient Survival, create SEPARATE mentions for each timepoint reported (e.g., if paper reports 1yr and 3yr survival, create two separate mentions with appropriate timeframe field).

> **NAS vs ITBL Priority**: If the paper reports BOTH "Non-Anastomotic Strictures (NAS)" AND "Ischemic-Type Biliary Lesions (ITBL)" as separate rows, **prefer NAS**. Only treat NAS=IC=ITBL as synonyms if the paper uses them interchangeably (not separately reported).

---

## 3-Step Extraction Protocol

### Step 1. Eligibility (적합성)
1. **Population Check:** Is this study about liver transplantation with machine perfusion (HOPE, NMP, HMP)?
2. **ECD/DCD Focus:** If mixed population, look for ECD/DCD subgroup data first.
   - ECD = Age ≥60, or DCD, or high DRI (>1.5)
3. **Separation:** If subgroup data is separately reported, USE THAT instead of pooled data.

### Step 2. Sourcing (출처)
1. **Document Priority:** Main paper > Supplementary (unless Supp has subgroup data)
2. **Data Type Priority:** Table > Text > Figure (NEVER estimate from figures)
3. **Record Location:** Always note exact source (Table 2, Supp Table S3, Page 5 para 2)

### Step 3. Processing (가공)
1. **Direct Values:** Extract n/N exactly as stated
2. **Calculate from %:** If only % given, calculate n = round(N × %)
3. **Flag Estimates:** Mark any calculated values with is_estimated: true

### Step 4. Supplementary Table Extraction (CRITICAL)
When the main text mentions supplementary tables for subgroup data (e.g., "outcomes in Supplementary Table 5"):
1. **MUST** locate and read that specific supplementary table
2. **MUST** extract ALL target outcomes from that table (EAD, NAS, MC, etc.)
3. **Include outcomes NOT mentioned in the main text** - if a target outcome appears in the supplementary table, extract it even if the main text only says "no difference" or doesn't discuss it

---

## Output Format (JSON)

```json
{
  "study_id": "FirstAuthor_Year",
  "study_design": "RCT or NRS",
  "population": {
    "type": "Exclusive_ECD | Exclusive_DCD | Mixed | Unknown",
    "subgroup_available": true/false,
    "subgroup_used": "describe if using subgroup",
    "matching": "PSM 1:2 | IPTW | None | RCT"
  },
  "arms": {
    "intervention": {"name": "HOPE/NMP/HMP", "N": null},
    "control": {"name": "SCS", "N": null}
  },
  "outcomes": [
    {
      "outcome_name": "EAD",
      "definition": {
        "criteria": "Olthoff criteria",
        "timeframe": "within 7 days",
        "source": "Methods, p.3"
      },
      "mentions": [
        {
          "location": {"section": "Results", "element": "Table 2", "page": 5},
          "quote": "EAD occurred in 20 (29.4%) vs 33 (48.5%)",
          "intervention": {"n": 20, "N": 68, "pct": 29.4},
          "control": {"n": 33, "N": 68, "pct": 48.5},
          "is_subgroup": false,
          "is_estimated": false
        },
        {
          "location": {"section": "Supplementary", "element": "Table S3", "page": "supp-12"},
          "quote": "DCD subgroup: EAD 7/16 vs 12/25",
          "intervention": {"n": 7, "N": 16},
          "control": {"n": 12, "N": 25},
          "is_subgroup": true,
          "subgroup_type": "DCD",
          "is_estimated": false
        }
      ],
      "selected_mention": 1,
      "selection_reason": "DCD subgroup data prioritized per extraction rules"
    }
  ],
  "extraction_notes": {
    "data_quality_concerns": [],
    "ambiguities": [],
    "general_notes": ""
  }
}
```

---

## Important Rules

1. **Exhaustive Search**: Check ALL Tables, ALL Figures captions, ALL Supplementary
2. **No Inference**: Only extract explicitly stated values
3. **Flag Subgroups**: Clearly mark if data is from subgroup (DCD, matched, etc.)
4. **Multiple Mentions OK**: Same outcome in multiple places = multiple mentions
5. **Select Best**: After collecting all mentions, select the best one and explain why

---

## Handling Ambiguity

If N differs between intervention/control across outcomes:
- Record the inconsistency in data_quality_concerns
- Use the N from the most reliable source (usually the demographics table)

If subgroup vs pooled is unclear:
- Record BOTH in mentions array
- Flag in ambiguities
'''


def find_paper_folder(doi_prefix: str) -> Path:
    """Find paper folder by DOI prefix."""
    base = Path(__file__).parent.parent / "Papers"
    
    for folder_type in ["기존 논문들", "새 논문들"]:
        folder_path = base / folder_type
        if folder_path.exists():
            for paper_folder in folder_path.iterdir():
                if paper_folder.is_dir() and doi_prefix in paper_folder.name:
                    return paper_folder
    return None


def get_pdfs(folder: Path) -> list:
    """Get main PDF and relevant supplementary files."""
    pdfs = list(folder.glob("*.pdf"))
    
    # Exclude patterns
    exclude = ['disclosure', 'protocol', 'data-sharing', 'checklist', 'ctat', 'cover']
    
    result = []
    for pdf in pdfs:
        name_lower = pdf.name.lower()
        if not any(x in name_lower for x in exclude):
            result.append(pdf)
    
    # Limit to 4 files max
    return result[:4]


def extract_v2_from_paths(pdf_paths: list, verbose: bool = True) -> dict:
    """Run v2.0 extraction using provided PDF paths."""
    
    pdfs = [Path(p) for p in pdf_paths if Path(p).exists()]
    if not pdfs:
        return {"error": "No PDFs found from paths"}
    
    if verbose:
        print(f"  Files: {[p.name for p in pdfs]}")
    
    # Initialize client with API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY not set"}
    
    client = genai.Client(api_key=api_key)
    
    # Prepare content with file labels
    contents = []
    
    # Identify main vs supplementary
    supp_patterns = ['supplement', 'appendix', 'supp', 'mmc', 'sdc', 'moesm', '_s1', '_s2']
    
    for pdf in pdfs:
        name_lower = pdf.name.lower()
        is_supp = any(p in name_lower for p in supp_patterns)
        file_type = "SUPPLEMENTARY" if is_supp else "MAIN PAPER"
        
        # Add label
        contents.append(f"=== {file_type}: {pdf.name} ===")
        
        # Add PDF
        with open(pdf, "rb") as f:
            pdf_data = f.read()
        contents.append(types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"))
    
    contents.append(V2_PROMPT)
    
    # Call API
    config = types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(thinking_level="medium"),
        response_mime_type="application/json",
    )
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=contents,
        config=config
    )
    
    # Parse response
    try:
        result = json.loads(response.text)
    except json.JSONDecodeError:
        result = {"raw_text": response.text[:2000], "error": "JSON parse failed"}
    
    # Extract thoughts (thinking signature)
    thoughts = None
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content') and candidate.content:
            for part in candidate.content.parts:
                if hasattr(part, 'thought') and part.thought:
                    thoughts = part.text
                    break
    
    # Token usage
    usage = {}
    if response.usage_metadata:
        usage = {
            "prompt": response.usage_metadata.prompt_token_count,
            "output": response.usage_metadata.candidates_token_count,
            "thoughts": getattr(response.usage_metadata, 'thoughts_token_count', 0),
            "total": response.usage_metadata.total_token_count
        }
    
    return {"result": result, "usage": usage, "thoughts": thoughts}


def main():
    print("="*70)
    print("V2.0 EXTRACTION TEST - Problem Papers")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Studies: {len(TEST_STUDIES)}")
    print("="*70)
    
    states_dir = Path(__file__).parent / "extraction_states"
    output_dir = Path(__file__).parent / "v2_test_results"
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    total_tokens = 0
    
    for i, study_id in enumerate(TEST_STUDIES, 1):
        print(f"\n[{i}/{len(TEST_STUDIES)}] {study_id}")
        print("-"*50)
        
        # Load existing state to get PDF paths
        state_file = states_dir / f"extraction_state_{study_id}.json"
        if not state_file.exists():
            print(f"  ❌ State file not found")
            continue
        
        with open(state_file) as f:
            state = json.load(f)
        
        pdf_paths = state.get("pdf_paths", [])
        if not pdf_paths:
            print(f"  ❌ No PDF paths in state")
            continue
        
        try:
            result = extract_v2_from_paths(pdf_paths, verbose=True)
            results[study_id] = result
            
            usage = result.get("usage", {})
            tokens = usage.get("total", 0)
            total_tokens += tokens
            print(f"  ✅ Tokens: {tokens:,}")
            
            # Save result
            with open(output_dir / f"{study_id}_v2.json", "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print(f"Total tokens: {total_tokens:,}")
    print(f"Estimated cost: ${total_tokens * 0.5 / 1_000_000 + total_tokens * 3.0 / 1_000_000:.4f}")
    print(f"Results saved to: v2_test_results/")
    print("="*70)


if __name__ == "__main__":
    main()

