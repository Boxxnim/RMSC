#!/usr/bin/env python3
"""
Batch Extraction Script
Extract data from all papers in the systematic review.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extractor_gemini import DataExtractorGemini
from document_classifier import DocumentClassifier


# Global classifier instance (lazy initialization)
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = DocumentClassifier()
    return _classifier


def find_pdf_in_folder(folder: Path, use_llm_classification: bool = True, verbose: bool = True) -> tuple:
    """Find main PDF, supplementary files, and RoB-related files in a folder.
    
    Args:
        folder: Path to folder containing PDFs
        use_llm_classification: If True, use LLM to classify non-main files
        verbose: Print classification details
    
    Returns:
        (main_pdf_path, list_of_supplementary_paths, list_of_rob_files)
    """
    pdfs = list(folder.glob("*.pdf"))
    
    if not pdfs:
        return None, [], []
    
    # Find main paper (explicit main_ prefix)
    main_pdf = None
    other_pdfs = []
    
    for pdf in pdfs:
        if pdf.name.lower().startswith("main_"):
            main_pdf = str(pdf)
        else:
            other_pdfs.append(pdf)
    
    # If no main_ prefix found, fall back to shortest name
    if main_pdf is None and other_pdfs:
        # Simple pattern-based exclusion first
        EXCLUDE_SIMPLE = ['cover', 'checklist', 'ctat']
        candidates = [p for p in other_pdfs if not any(x in p.name.lower() for x in EXCLUDE_SIMPLE)]
        if candidates:
            candidates.sort(key=lambda x: len(x.name))
            main_pdf = str(candidates[0])
            other_pdfs = [p for p in other_pdfs if str(p) != main_pdf]
    
    if not other_pdfs:
        return main_pdf, [], []
    
    # Classify other PDFs
    supplementary = []
    rob_files = []
    
    if use_llm_classification:
        classifier = get_classifier()
        for pdf in other_pdfs:
            try:
                result = classifier.classify(str(pdf), verbose=verbose)
                doc_type = result.get("document_type", "supplementary")
                
                if doc_type == "supplementary":
                    supplementary.append(str(pdf))
                elif doc_type == "rob_document":
                    rob_files.append(str(pdf))
                elif doc_type == "unknown":
                    # Unknown files: include in supplementary to be safe
                    supplementary.append(str(pdf))
                    if verbose:
                        print(f"    ⚠️ Unknown type, including as supplementary")
                # exclude files are simply not added
            except Exception as e:
                if verbose:
                    print(f"    ⚠️ Classification failed for {pdf.name}: {e}")
                supplementary.append(str(pdf))  # Default to supplementary
    else:
        # Fallback: simple pattern matching
        SUPP_PATTERNS = ['supplement', 'appendix', 'supp', 'mmc', 'sdc', 'moesm', 'esm']
        ROB_PATTERNS = ['disclosure', 'protocol', 'coi', 'conflict', 'author']
        
        for pdf in other_pdfs:
            name_lower = pdf.name.lower()
            if any(x in name_lower for x in ROB_PATTERNS):
                rob_files.append(str(pdf))
            elif any(x in name_lower for x in SUPP_PATTERNS):
                supplementary.append(str(pdf))
            else:
                supplementary.append(str(pdf))
    
    return main_pdf, supplementary, rob_files


def batch_extract(output_excel: str = "batch_extraction_results.xlsx", 
                  use_tool_calling: bool = True,
                  verbose: bool = True):
    """Extract data from all papers."""
    
    base_path = Path(__file__).parent.parent / "Papers"
    legacy_folder = base_path / "기존 논문들"
    new_folder = base_path / "새 논문들"
    
    # Collect all paper folders
    all_folders = []
    
    if legacy_folder.exists():
        all_folders.extend([f for f in legacy_folder.iterdir() if f.is_dir()])
    
    if new_folder.exists():
        all_folders.extend([f for f in new_folder.iterdir() if f.is_dir()])
    
    print(f"\n{'='*70}")
    print(f"BATCH EXTRACTION - {len(all_folders)} papers")
    print(f"{'='*70}")
    print(f"Output: {output_excel}")
    print(f"Mode: {'Tool Calling' if use_tool_calling else 'Standard'}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Initialize extractor
    extractor = DataExtractorGemini()
    
    # Track results
    success = []
    failed = []
    skipped = []
    total_tokens = 0
    
    for i, folder in enumerate(sorted(all_folders), 1):
        print(f"\n[{i}/{len(all_folders)}] Processing: {folder.name}")
        print("-" * 50)
        
        main_pdf, supplementary, rob_files = find_pdf_in_folder(folder)
        
        if not main_pdf:
            print(f"  ⚠️ No PDF found, skipping")
            skipped.append(folder.name)
            continue
        
        if rob_files:
            print(f"  📋 RoB files: {len(rob_files)}")
        
        try:
            # Use process_paper method
            extractor.process_paper(
                file_path=main_pdf,
                output_path=output_excel,
                supplementary_files=supplementary if supplementary else None,
                rob_files=rob_files if rob_files else None,
                tool_calling=use_tool_calling,
                verbose=verbose
            )
            
            success.append(folder.name)
            
            # Get token usage from latest state file
            states_dir = Path(__file__).parent / "extraction_states"
            state_files = sorted(states_dir.glob("extraction_state_*.json"), 
                               key=lambda x: x.stat().st_mtime, reverse=True)
            if state_files:
                with open(state_files[0]) as f:
                    state = json.load(f)
                    tokens = state.get("token_usage", {}).get("total_tokens", 0)
                    total_tokens += tokens
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            failed.append(folder.name)
        
        # Rate limiting - avoid hitting API limits
        if i < len(all_folders):
            time.sleep(2)
    
    # Summary
    print(f"\n{'='*70}")
    print("BATCH EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Success: {len(success)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏭️ Skipped: {len(skipped)}")
    print(f"📊 Total tokens: {total_tokens:,}")
    print(f"💾 Output: {output_excel}")
    print(f"{'='*70}")
    
    if failed:
        print(f"\nFailed papers:")
        for f in failed:
            print(f"  - {f}")
    
    if skipped:
        print(f"\nSkipped papers (no PDF):")
        for s in skipped:
            print(f"  - {s}")
    
    return success, failed, skipped


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch extract data from all papers")
    parser.add_argument("--output", "-o", default="batch_extraction_results.xlsx",
                        help="Output Excel file")
    parser.add_argument("--no-tool-calling", action="store_true",
                        help="Use standard mode instead of tool calling")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Less verbose output")
    
    args = parser.parse_args()
    
    batch_extract(
        output_excel=args.output,
        use_tool_calling=not args.no_tool_calling,
        verbose=not args.quiet
    )
