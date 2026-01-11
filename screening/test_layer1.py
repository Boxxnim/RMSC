#!/usr/bin/env python3
"""
Small-Scale Test Runner for Layer 1 Screening
==============================================

Runs Layer 1 exclusion screening on a small sample of records
to validate the pipeline before full execution.

Usage:
    export GEMINI_API_KEY="your-key-here"
    python test_layer1.py [sample_size]

Default sample size: 10 records
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Load .env file if exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    pass  # dotenv not installed, use system env vars

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GEMINI_FLASH, get_api_key
from token_logger import reset_logger, get_logger


def run_test(sample_size: int = 10):
    """Run Layer 1 on a small sample of records."""
    
    print(f"\n{'='*60}")
    print(f"LAYER 1 TEST RUN - {sample_size} RECORDS")
    print(f"{'='*60}")
    print(f"Model: {GEMINI_FLASH.name}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Check API key
    try:
        api_key = get_api_key(GEMINI_FLASH.api_key_env)
        print(f"✓ API key found")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print(f"Set your API key with: export GEMINI_API_KEY='your-key'")
        sys.exit(1)
    
    # Load data
    input_file = "screening_records.csv"
    if not os.path.exists(input_file):
        print(f"✗ Error: {input_file} not found")
        sys.exit(1)
    
    df = pd.read_csv(input_file)
    print(f"✓ Loaded {len(df)} records from {input_file}")
    
    # Take sample
    sample_df = df.head(sample_size).copy()
    print(f"✓ Selected {len(sample_df)} records for testing\n")
    
    # Reset token logger for clean test
    reset_logger()
    
    # Import and setup
    import google.generativeai as genai
    from prompts import format_layer1_prompt
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=GEMINI_FLASH.name,
        generation_config={
            "temperature": 0.0,
            "top_p": 0.95,
            "max_output_tokens": 2000,
            "response_mime_type": "application/json",
        }
    )
    
    # Process each record
    results = []
    logger = get_logger()
    
    for idx, row in sample_df.iterrows():
        title = str(row.get('title', ''))
        abstract = str(row.get('abstract', ''))[:500]  # Truncate for display
        record_id = str(row.get('record_id', idx))
        
        print(f"\n[Record {idx + 1}/{sample_size}] {title[:60]}...")
        
        try:
            prompt = format_layer1_prompt(title, str(row.get('abstract', '')))
            response = model.generate_content(prompt)
            
            # Extract token usage - use total_token_count for thinking tokens
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(response.usage_metadata, 'total_token_count', input_tokens + output_tokens)
            
            # Log usage with total tokens (includes thinking)
            logger.log_usage(
                model=GEMINI_FLASH.name,
                input_tokens=input_tokens,
                output_tokens=total_tokens - input_tokens,  # Includes thinking tokens
                layer="L1",
                record_id=record_id
            )
            
            # Parse response
            import json
            reasoning = None
            evidence = None
            try:
                parsed = json.loads(response.text)
                decision = parsed.get('decision', 'unknown')
                tags = parsed.get('exclusion_tags', [])
                reasoning = parsed.get('reasoning', '')
                evidence = parsed.get('evidence', '')
            except json.JSONDecodeError as je:
                print(f"  [DEBUG] JSON parse error: {je}")
                print(f"  [DEBUG] Full response: {response.text}")
                decision = 'parse_error'
                tags = []
            
            result = {
                'record_id': record_id,
                'title': title[:80] + '...' if len(title) > 80 else title,
                'decision': decision,
                'exclusion_tags': ','.join(tags) if tags else '',
                'evidence_quote': evidence if evidence else '',  # Exact quote from original text
                'reasoning': reasoning if reasoning else '',
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': total_tokens
            }
            results.append(result)
            
            print(f"  → Decision: {decision.upper()}", end='')
            if tags:
                print(f" ({', '.join(tags)})")
            else:
                print()
            if evidence:
                print(f"  → Evidence: \"{evidence[:70]}...\"")
            print(f"  → Reasoning: {reasoning[:60] if reasoning else 'N/A'}...")
            print(f"  → Tokens: {input_tokens} in / {output_tokens} out / {total_tokens} total")
            
        except Exception as e:
            import traceback
            print(f"  ✗ Error: {e}")
            print(f"  [DEBUG] Error type: {type(e).__name__}")
            print(f"  [DEBUG] Traceback: {traceback.format_exc()[:500]}")
            results.append({
                'record_id': record_id,
                'title': title[:80],
                'decision': 'error',
                'exclusion_tags': '',
                'evidence_quote': '',
                'reasoning': str(e),
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    results_df = pd.DataFrame(results)
    
    exclude_count = (results_df['decision'] == 'exclude').sum()
    pass_count = (results_df['decision'] == 'pass').sum()
    error_count = (results_df['decision'].isin(['error', 'parse_error'])).sum()
    
    print(f"Processed: {sample_size}")
    print(f"Excluded: {exclude_count} ({100*exclude_count/sample_size:.1f}%)")
    print(f"Passed: {pass_count} ({100*pass_count/sample_size:.1f}%)")
    print(f"Errors: {error_count}")
    
    # Token usage summary
    logger.print_summary()
    
    # Estimate full run cost
    total_cost = logger.get_total_cost()
    total_tokens = logger.get_total_tokens()
    full_run_records = len(df)
    estimated_full_cost = total_cost * (full_run_records / sample_size)
    
    print(f"\n{'='*60}")
    print("COST ESTIMATION")
    print(f"{'='*60}")
    print(f"Test ({sample_size} records): ${total_cost:.4f}")
    print(f"Full run ({full_run_records} records): ~${estimated_full_cost:.4f}")
    print(f"Avg tokens per record: {total_tokens['input']//sample_size} in / {total_tokens['output']//sample_size} out")
    print(f"{'='*60}\n")
    
    # Save test results
    output_file = "test_layer1_results.csv"
    results_df.to_csv(output_file, index=False)
    print(f"Test results saved to: {output_file}")
    
    logger.save_report("test_layer1_cost_report.json")
    
    return results_df


if __name__ == "__main__":
    sample_size = 10
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
        except ValueError:
            print(f"Invalid sample size: {sys.argv[1]}")
            sys.exit(1)
    
    run_test(sample_size)
