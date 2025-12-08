#!/usr/bin/env python3
"""
Layer 1: Exclusion Screening with Gemini Flash
===============================================

This script performs first-pass exclusion screening using Gemini Flash.
Records that clearly meet exclusion criteria are marked as "exclude".
All other records are passed to Layer 2 for inclusion verification.

Part of: Systematic Review Update - Machine Perfusion in Liver Transplantation

Usage:
    export GEMINI_API_KEY="your-key-here"
    python 02_layer1_exclusion.py screening_records.csv layer1_results.csv

Dependencies:
    pip install google-generativeai pandas tqdm
"""

import os
import sys
import json
import time
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import local modules
from prompts import format_layer1_prompt
from config import GEMINI_FLASH, get_api_key, EXCLUSION_TAGS
from token_logger import get_logger

# Try to import Gemini SDK
try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed")
    print("Run: pip install google-generativeai")
    sys.exit(1)


def setup_gemini(api_key: str, model_name: str) -> Any:
    """Initialize Gemini client."""
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.0,
        "top_p": 0.95,
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "decision": {"type": "string", "enum": ["exclude", "pass"]},
                "exclusion_tags": {"type": "array", "items": {"type": "string"}},
                "evidence": {"type": "string"},
                "reasoning": {"type": "string"}
            },
            "required": ["decision", "exclusion_tags", "evidence", "reasoning"]
        }
    }
    
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )
    
    return model


def parse_json_response(response_text: str) -> Optional[Dict]:
    """Parse JSON from model response, handling common issues."""
    try:
        # Try direct parsing
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object pattern
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    
    return None


def screen_record_layer1(
    model: Any,
    title: str,
    abstract: str,
    record_id: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Dict[str, Any]:
    """
    Screen a single record for exclusion criteria.
    
    Returns:
        Dict with keys: decision, exclusion_tags, evidence, reasoning, error, input_tokens, output_tokens
    """
    prompt = format_layer1_prompt(title, abstract)
    logger = get_logger()
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Extract token usage from response (including thinking tokens)
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(response.usage_metadata, 'total_token_count', input_tokens + output_tokens)
            
            # Log token usage with total tokens (includes thinking)
            logger.log_usage(
                model=GEMINI_FLASH.name,
                input_tokens=input_tokens,
                output_tokens=total_tokens - input_tokens,  # Includes thinking tokens
                layer="L1",
                record_id=record_id
            )
            
            parsed = parse_json_response(response_text)
            
            if parsed and "decision" in parsed:
                return {
                    "decision": parsed.get("decision", "pass"),
                    "exclusion_tags": parsed.get("exclusion_tags", []),
                    "evidence": parsed.get("evidence"),
                    "reasoning": parsed.get("reasoning"),
                    "error": None,
                    "raw_response": response_text[:500],
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens
                }
            else:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {
                    "decision": "pass",
                    "exclusion_tags": [],
                    "evidence": None,
                    "reasoning": "JSON parsing failed",
                    "error": f"Invalid JSON: {response_text[:200]}",
                    "raw_response": response_text[:500]
                }
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            return {
                "decision": "pass",
                "exclusion_tags": [],
                "evidence": None,
                "reasoning": None,
                "error": str(e),
                "raw_response": None
            }
    
    # Should not reach here
    return {
        "decision": "pass",
        "exclusion_tags": [],
        "evidence": None,
        "reasoning": None,
        "error": "Max retries exceeded",
        "raw_response": None
    }


def process_screening(
    input_csv: str,
    output_csv: str,
    model: Any,
    batch_size: int = 50,  # Process 50 records in parallel per batch
    delay_between_batches: float = 1.0,
    resume_from: Optional[int] = None
) -> None:
    """
    Process all records through Layer 1 screening using parallel execution.
    """
    # Load input data
    df = pd.read_csv(input_csv)
    total_records = len(df)
    
    print(f"\n{'='*60}")
    print(f"LAYER 1: EXCLUSION SCREENING (PARALLEL)")
    print(f"{'='*60}")
    print(f"Total records: {total_records}")
    print(f"Model: {GEMINI_FLASH.name}")
    print(f"Batch size: {batch_size}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize output columns
    new_columns = [
        'L1_decision',
        'L1_exclusion_tags',
        'L1_evidence',
        'L1_reasoning',
        'L1_error',
        'L1_timestamp',
        'L1_input_tokens',
        'L1_output_tokens',
        'L1_total_tokens'
    ]
    
    for col in new_columns:
        if col not in df.columns:
            df[col] = None
    
    # Determine starting point
    start_idx = 0
    if resume_from is not None:
        start_idx = resume_from
    elif os.path.exists(output_csv):
        # Check existing progress
        existing_df = pd.read_csv(output_csv)
        if 'L1_decision' in existing_df.columns:
            processed = existing_df['L1_decision'].notna().sum()
            if processed > 0:
                print(f"Found existing progress: {processed}/{total_records} processed")
                response = input("Resume from last position? (y/n): ")
                if response.lower() == 'y':
                    df = existing_df
                    start_idx = processed
    
    # Process records in batches
    exclude_count = 0
    pass_count = 0
    error_count = 0
    
    # Recalculate counts if resuming
    if start_idx > 0:
        exclude_count = (df['L1_decision'] == 'exclude').sum()
        pass_count = (df['L1_decision'] == 'pass').sum()
        error_count = df['L1_error'].notna().sum()
    
    try:
        # Loop through batches
        for batch_start in range(start_idx, total_records, batch_size):
            batch_end = min(batch_start + batch_size, total_records)
            batch_indices = range(batch_start, batch_end)
            
            print(f"\nProcessing batch {batch_start} to {batch_end} ({batch_end - batch_start} records)...")
            
            futures = []
            with ThreadPoolExecutor(max_workers=min(batch_size, 50)) as executor:
                for idx in batch_indices:
                    row = df.iloc[idx]
                    title = str(row.get('title', ''))
                    abstract = str(row.get('abstract', ''))
                    record_id = str(row.get('record_id', idx))
                    
                    if not title.strip():
                        # Handle empty title immediately without API call
                        df.at[idx, 'L1_decision'] = 'pass'
                        df.at[idx, 'L1_reasoning'] = 'No title available'
                        df.at[idx, 'L1_timestamp'] = datetime.now().isoformat()
                        pass_count += 1
                        continue
                        
                    future = executor.submit(screen_record_layer1, model, title, abstract, record_id=record_id)
                    futures.append((idx, future))
                
                # Collect results as they complete
                for idx, future in tqdm(futures, total=len(futures), desc=f"Batch Progress"):
                    try:
                        result = future.result()
                        
                        # Update dataframe
                        df.at[idx, 'L1_decision'] = result['decision']
                        df.at[idx, 'L1_exclusion_tags'] = ','.join(result['exclusion_tags']) if result['exclusion_tags'] else ''
                        df.at[idx, 'L1_evidence'] = result['evidence']
                        df.at[idx, 'L1_reasoning'] = result['reasoning']
                        df.at[idx, 'L1_error'] = result['error']
                        df.at[idx, 'L1_timestamp'] = datetime.now().isoformat()
                        df.at[idx, 'L1_input_tokens'] = result.get('input_tokens', 0)
                        df.at[idx, 'L1_output_tokens'] = result.get('output_tokens', 0)
                        df.at[idx, 'L1_total_tokens'] = result.get('total_tokens', 0)
                        
                        # Update counts
                        if result['decision'] == 'exclude':
                            exclude_count += 1
                        else:
                            pass_count += 1
                        if result['error']:
                            error_count += 1
                            
                    except Exception as e:
                        print(f"Error processing record {idx}: {e}")
                        df.at[idx, 'L1_error'] = str(e)
                        error_count += 1
            
            # Save after each batch
            df.to_csv(output_csv, index=False)
            
            # Rate limiting between batches
            if batch_end < total_records:
                time.sleep(delay_between_batches)
    
    except KeyboardInterrupt:
        print(f"\n\nInterrupted! Saving progress...")
        df.to_csv(output_csv, index=False)
        print(f"Progress saved to {output_csv}")
        print(f"Resume with: python {sys.argv[0]} {input_csv} {output_csv} --resume {batch_start}")
        sys.exit(1)
    
    # Final save
    df.to_csv(output_csv, index=False)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"LAYER 1 COMPLETE")
    print(f"{'='*60}")
    print(f"Total processed: {total_records}")
    print(f"Excluded: {exclude_count} ({100*exclude_count/total_records:.1f}%)")
    print(f"Passed to Layer 2: {pass_count} ({100*pass_count/total_records:.1f}%)")
    print(f"Errors: {error_count}")
    print(f"\nResults saved to: {output_csv}")
    
    # Token usage summary
    logger = get_logger()
    logger.print_summary()
    
    # Save cost report
    report_prefix = output_csv.replace('.csv', '')
    logger.save_report(f"{report_prefix}_cost_report.json")
    logger.save_summary_csv(f"{report_prefix}_cost_summary.csv")
    
    # Exclusion breakdown
    if exclude_count > 0:
        print(f"\nExclusion breakdown:")
        for tag, desc in EXCLUSION_TAGS.items():
            count = df['L1_exclusion_tags'].str.contains(tag, na=False).sum()
            if count > 0:
                print(f"  {tag}: {count} ({desc})")
    
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.csv> <output.csv> [--resume N]")
        print(f"Example: {sys.argv[0]} screening_records.csv layer1_results.csv")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    resume_from = None
    if '--resume' in sys.argv:
        resume_idx = sys.argv.index('--resume')
        if resume_idx + 1 < len(sys.argv):
            resume_from = int(sys.argv[resume_idx + 1])
            
    batch_size = 50
    if '--batch' in sys.argv:
        batch_idx = sys.argv.index('--batch')
        if batch_idx + 1 < len(sys.argv):
            batch_size = int(sys.argv[batch_idx + 1])
    
    if not os.path.exists(input_csv):
        print(f"Error: Input file not found: {input_csv}")
        sys.exit(1)
    
    # Setup API
    try:
        api_key = get_api_key(GEMINI_FLASH.api_key_env)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Set your API key with: export GEMINI_API_KEY='your-key'")
        sys.exit(1)
    
    model = setup_gemini(api_key, GEMINI_FLASH.name)
    
    # Run screening
    process_screening(
        input_csv=input_csv,
        output_csv=output_csv,
        model=model,
        batch_size=batch_size,
        delay_between_batches=1.0,
        resume_from=resume_from
    )


if __name__ == '__main__':
    main()
