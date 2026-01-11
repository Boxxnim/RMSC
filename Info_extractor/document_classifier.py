#!/usr/bin/env python3
"""
Document Classification Subagent
Classifies PDFs into: supplementary, rob_document, or exclude
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Literal
from google import genai
from google.genai import types


CLASSIFICATION_PROMPT = """You are a document classifier for systematic review data extraction.

## TASK
Classify this PDF document into ONE of the following categories:

### Categories

1. **supplementary** - Supplementary material for the main paper:
   - Additional tables, figures, methods
   - Extended data, appendix
   - Supplementary results
   - Statistical analysis plans
   - Protocol documents WITH outcome data
   
2. **rob_document** - Documents ONLY useful for Risk of Bias assessment:
   - PURE conflict of interest / disclosure statements (no data)
   - PURE author information (no data)
   - Standalone data sharing statements
   - NOTE: If the document contains outcome data/results, classify as 'supplementary' instead!
   
3. **exclude** - Documents NOT useful for data extraction:
   - Cover letters
   - Submission checklists (CONSORT, PRISMA, etc.)
   - Reporting guidelines
   - Editorial policies
   - Reviewer responses

4. **unknown** - Cannot determine document type:
   - Document is unclear or corrupted
   - Mixed content that doesn't fit other categories
   - Uncertain classification

## PRIORITY RULE
If a document contains BOTH disclosure/COI AND outcome data/tables/results:
→ Classify as **supplementary** (data extraction takes priority!)

## OUTPUT FORMAT
Return ONLY a JSON object:
{
  "document_type": "supplementary" | "rob_document" | "exclude" | "unknown",
  "reason": "Brief explanation"
}
"""


class DocumentClassifier:
    """Classify documents using Gemini Flash for cost efficiency."""
    
    def __init__(self, model: str = "gemini-flash-latest"):
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Try loading from .env file
            env_path = Path(__file__).parent / ".env"
            if env_path.exists():
                with open(env_path) as f:
                    for line in f:
                        if "GOOGLE_API_KEY" in line or "GEMINI_API_KEY" in line:
                            api_key = line.split("=")[1].strip().strip('"\'')
                            break
        
        if not api_key:
            raise ValueError("No API key found")
        
        self.client = genai.Client(api_key=api_key)
        self.model = model
    
    def classify(self, pdf_path: str, verbose: bool = False) -> Dict:
        """Classify a single PDF document.
        
        Returns:
            {
                "document_type": "supplementary" | "rob_document" | "exclude",
                "confidence": float,
                "reason": str
            }
        """
        pdf_path = Path(pdf_path)
        
        if verbose:
            print(f"  Classifying: {pdf_path.name}")
        
        # Read PDF
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Build request
        contents = [
            types.Part.from_bytes(data=pdf_data, mime_type='application/pdf'),
            CLASSIFICATION_PROMPT
        ]
        
        config = types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            
            result = json.loads(response.text)
            
            if verbose:
                print(f"    → {result['document_type']}: {result['reason']}")
            
            return result
            
        except Exception as e:
            if verbose:
                print(f"    ⚠️ Classification failed: {e}")
            # Default to unknown if classification fails
            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "reason": f"Classification failed: {str(e)}"
            }
    
    def classify_folder(self, folder_path: str, verbose: bool = True) -> Dict[str, List[str]]:
        """Classify all PDFs in a folder (excluding main_ prefixed files).
        
        Returns:
            {
                "main": [list of main_ prefixed files],
                "supplementary": [list of supplementary files],
                "rob_document": [list of RoB-related files],
                "exclude": [list of excluded files]
            }
        """
        folder = Path(folder_path)
        pdfs = list(folder.glob("*.pdf"))
        
        result = {
            "main": [],
            "supplementary": [],
            "rob_document": [],
            "exclude": []
        }
        
        if verbose:
            print(f"\n📁 Classifying {len(pdfs)} PDFs in {folder.name}")
        
        for pdf in pdfs:
            name_lower = pdf.name.lower()
            
            # Main paper - explicitly marked
            if name_lower.startswith("main_"):
                result["main"].append(str(pdf))
                if verbose:
                    print(f"  ✅ {pdf.name} → main (explicit)")
                continue
            
            # Classify other files
            classification = self.classify(str(pdf), verbose=verbose)
            doc_type = classification.get("document_type", "supplementary")
            result[doc_type].append(str(pdf))
        
        if verbose:
            print(f"\n📊 Classification Summary:")
            for cat, files in result.items():
                if files:
                    print(f"  {cat}: {len(files)} file(s)")
        
        return result


# Convenience function
def classify_folder(folder_path: str, verbose: bool = True) -> Dict[str, List[str]]:
    """Classify all PDFs in a folder."""
    classifier = DocumentClassifier()
    return classifier.classify_folder(folder_path, verbose=verbose)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_classifier.py <folder_path>")
        sys.exit(1)
    
    folder = sys.argv[1]
    result = classify_folder(folder)
    
    print("\n" + "="*50)
    print("FINAL RESULT")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))
