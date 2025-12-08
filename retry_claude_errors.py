#!/usr/bin/env python3
"""
Retry Claude API calls for records that had errors.
"""

import os
import sys
import time
import pandas as pd
from tqdm import tqdm

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import CLAUDE_SONNET, get_api_key
from token_logger import reset_logger, get_logger

# Import layer2 functions
import importlib.util
spec = importlib.util.spec_from_file_location("layer2", "03_layer2_inclusion.py")
layer2 = importlib.util.module_from_spec(spec)
sys.modules["layer2"] = layer2
spec.loader.exec_module(layer2)

setup_anthropic = layer2.setup_anthropic
screen_with_claude = layer2.screen_with_claude
flatten_result = layer2.flatten_result


def retry_claude_errors(batch_size: int = 10, delay_between_batches: float = 10.0, delay_between_calls: float = 1.0):
    """Retry Claude calls for records with errors, with batching to avoid rate limits."""
    
    # Load results
    df = pd.read_csv('layer2_results.csv')
    
    # Find records with Claude errors
    error_mask = df['L2_sonnet_error'].notna()
    error_indices = df[error_mask].index.tolist()
    
    print(f"Found {len(error_indices)} records with Claude errors")
    print(f"Batch size: {batch_size}, Delay between batches: {delay_between_batches}s")
    
    if len(error_indices) == 0:
        print("No errors to retry!")
        return
    
    # Setup API
    try:
        anthropic_key = get_api_key(CLAUDE_SONNET.api_key_env)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    anthropic_client = setup_anthropic(anthropic_key)
    
    # Reset logger
    reset_logger()
    logger = get_logger()
    
    success_count = 0
    still_error_count = 0
    
    # Process in batches
    num_batches = (len(error_indices) + batch_size - 1) // batch_size
    
    for batch_num in range(num_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(error_indices))
        batch_indices = error_indices[batch_start:batch_end]
        
        print(f"\n[Batch {batch_num + 1}/{num_batches}] Processing {len(batch_indices)} records...")
        
        for idx in batch_indices:
            row = df.iloc[idx]
            title = str(row.get('title', ''))
            abstract = str(row.get('abstract', ''))
            record_id = str(row.get('record_id', idx))
            
            # Delay between calls
            time.sleep(delay_between_calls)
            
            # Retry Claude call
            result = screen_with_claude(anthropic_client, title, abstract, record_id)
            
            if result.get('error') is None:
                # Success - update the dataframe
                sonnet_flat = flatten_result(result, 'L2_sonnet')
                for key, value in sonnet_flat.items():
                    df.at[idx, key] = value
                
                # Add thinking if available
                if 'thinking' in result:
                    df.at[idx, 'L2_sonnet_thinking'] = result['thinking'][:500] if result['thinking'] else ''
                
                # Recalculate agreement
                pro_decision = df.at[idx, 'L2_pro_decision']
                df.at[idx, 'L2_models_agree'] = (pro_decision == result['decision'])
                
                success_count += 1
                print(f"  ✓ {record_id}: {result['decision']} ({result['confidence']})")
            else:
                still_error_count += 1
                print(f"  ✗ {record_id}: {result['error'][:50]}...")
        
        # Save after each batch
        df.to_csv('layer2_results.csv', index=False)
        print(f"  [Saved] Progress: {batch_end}/{len(error_indices)}")
        
        # Wait between batches (except for last batch)
        if batch_num < num_batches - 1:
            print(f"  Waiting {delay_between_batches}s before next batch...")
            time.sleep(delay_between_batches)
    
    print(f"\n{'='*50}")
    print(f"Retry complete!")
    print(f"  Success: {success_count}")
    print(f"  Still errors: {still_error_count}")
    print(f"{'='*50}")
    
    # Print token usage
    logger.print_summary()
    
    # Recalculate stats
    new_errors = df['L2_sonnet_error'].notna().sum()
    new_agree = df['L2_models_agree'].sum()
    print(f"\nUpdated stats:")
    print(f"  Remaining errors: {new_errors}")
    print(f"  Agreement: {new_agree}/{len(df[df['L2_pro_decision'].notna()])}")


if __name__ == "__main__":
    batch_size = 10
    delay_batches = 10.0
    delay_calls = 1.0
    
    if len(sys.argv) > 1:
        batch_size = int(sys.argv[1])
    if len(sys.argv) > 2:
        delay_batches = float(sys.argv[2])
    if len(sys.argv) > 3:
        delay_calls = float(sys.argv[3])
    
    retry_claude_errors(batch_size=batch_size, delay_between_batches=delay_batches, delay_between_calls=delay_calls)
