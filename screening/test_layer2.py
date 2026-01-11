#!/usr/bin/env python3
"""
Small-Scale Test Runner for Layer 2 Inclusion
==============================================

Runs Layer 2 inclusion verification on a small sample of records
that passed Layer 1 screening.
"""

import os
import sys
import csv
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    pass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GEMINI_PRO, CLAUDE_SONNET, get_api_key
from token_logger import reset_logger, get_logger

# Import 03_layer2_inclusion dynamically
import importlib.util
spec = importlib.util.spec_from_file_location("layer2", "03_layer2_inclusion.py")
layer2 = importlib.util.module_from_spec(spec)
sys.modules["layer2"] = layer2
spec.loader.exec_module(layer2)

setup_gemini = layer2.setup_gemini
setup_anthropic = layer2.setup_anthropic
screen_with_gemini_pro = layer2.screen_with_gemini_pro
screen_with_claude = layer2.screen_with_claude
flatten_result = layer2.flatten_result


def clean_text_for_csv(text: str, max_length: int = None) -> str:
    """Clean text for CSV storage - remove problematic characters."""
    if not text:
        return ''
    # Replace newlines and carriage returns with spaces
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length] + '...'
    return text

def run_test(sample_size: int = 5):
    """Run Layer 2 on a small sample of passed records."""
    
    print(f"\n{'='*60}")
    print(f"LAYER 2 TEST RUN - {sample_size} RECORDS")
    print(f"{'='*60}")
    print(f"Models: {GEMINI_PRO.name} + {CLAUDE_SONNET.name}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Setup APIs
    try:
        gemini_key = get_api_key(GEMINI_PRO.api_key_env)
        anthropic_key = get_api_key(CLAUDE_SONNET.api_key_env)
        print(f"✓ API keys found")
    except ValueError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
        
    gemini_model = setup_gemini(gemini_key, GEMINI_PRO.name)
    anthropic_client = setup_anthropic(anthropic_key)
    
    # Load Layer 1 results
    input_file = "layer1_results.csv"
    if not os.path.exists(input_file):
        print(f"✗ Error: {input_file} not found. Run Layer 1 first.")
        sys.exit(1)
    
    df = pd.read_csv(input_file)
    
    # Filter for 'pass' records
    passed_df = df[df['L1_decision'] == 'pass'].copy()
    print(f"✓ Loaded {len(df)} records, {len(passed_df)} passed Layer 1")
    
    if len(passed_df) == 0:
        print("No records passed Layer 1. Nothing to test.")
        sys.exit(0)
        
    # Take sample
    sample_df = passed_df.head(sample_size).copy()
    print(f"✓ Selected {len(sample_df)} records for testing\n")
    
    # Reset logger
    reset_logger()
    logger = get_logger()
    
    results = []
    
    for idx, row in sample_df.iterrows():
        title = str(row.get('title', ''))
        abstract = str(row.get('abstract', ''))
        record_id = str(row.get('record_id', idx))
        
        print(f"\n[Record {record_id}] {title[:60]}...")
        
        # Run models in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            pro_future = executor.submit(
                screen_with_gemini_pro, gemini_model, title, abstract, record_id
            )
            sonnet_future = executor.submit(
                screen_with_claude, anthropic_client, title, abstract, record_id
            )
            
            pro_result = pro_future.result()
            sonnet_result = sonnet_future.result()
        
        # Print results
        print(f"  Gemini Pro: {pro_result['decision'].upper()} ({pro_result['confidence']})")
        print(f"  Claude Sonnet: {sonnet_result['decision'].upper()} ({sonnet_result['confidence']})")
        
        agree = pro_result['decision'] == sonnet_result['decision']
        print(f"  → Agreement: {'✅ YES' if agree else '❌ NO'}")
        
        # Token usage
        pro_tokens = pro_result.get('total_tokens', 0)
        sonnet_tokens = sonnet_result.get('total_tokens', 0)
        print(f"  → Tokens: Gemini {pro_tokens} / Claude {sonnet_tokens}")
        
        # Collect detailed results
        result_row = {
            'record_id': record_id,
            'title': title[:80],
            'gemini_decision': pro_result['decision'],
            'gemini_confidence': pro_result['confidence'],
            'gemini_reasoning': clean_text_for_csv(pro_result.get('reasoning', ''), 500),
            'claude_decision': sonnet_result['decision'],
            'claude_confidence': sonnet_result['confidence'],
            'claude_reasoning': clean_text_for_csv(sonnet_result.get('reasoning', ''), 500),
            'claude_thinking': clean_text_for_csv(sonnet_result.get('thinking', ''), 500),
            'agreement': agree,
            'gemini_tokens': pro_tokens,
            'claude_tokens': sonnet_tokens
        }
        
        # Add inclusion check details
        for tag in ['INC-1', 'INC-2', 'INC-3', 'INC-4', 'INC-5']:
            pro_inc = pro_result.get('inclusion_check', {}).get(tag, {})
            son_inc = sonnet_result.get('inclusion_check', {}).get(tag, {})
            result_row[f'gemini_{tag}_status'] = pro_inc.get('status', '')
            result_row[f'gemini_{tag}_evidence'] = clean_text_for_csv(pro_inc.get('evidence', ''), 300)
            result_row[f'claude_{tag}_status'] = son_inc.get('status', '')
            result_row[f'claude_{tag}_evidence'] = clean_text_for_csv(son_inc.get('evidence', ''), 300)
        
        results.append(result_row)
        
        # Save after each record for debugging
        results_df = pd.DataFrame(results)
        results_df.to_csv('test_layer2_results.csv', index=False, quoting=csv.QUOTE_ALL)
        print(f"  → Saved to test_layer2_results.csv")
        
    # Summary
    logger.print_summary()
    logger.save_report("test_layer2_cost_report.json")
    
    print(f"\n✓ Final results saved to test_layer2_results.csv")
    
    return results

if __name__ == "__main__":
    sample_size = 5
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
        except ValueError:
            pass
    run_test(sample_size)
