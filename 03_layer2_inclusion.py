#!/usr/bin/env python3
"""
Layer 2: Inclusion Verification with Gemini 2.5 Pro + Claude Sonnet 4
=====================================================================

This script performs inclusion verification on records that passed Layer 1.
Uses two models (Gemini 2.5 Pro and Claude Sonnet 4) for cross-validation.
API calls are executed IN PARALLEL for faster processing.

Part of: Systematic Review Update - Machine Perfusion in Liver Transplantation

Usage:
    export GEMINI_API_KEY="your-key-here"
    export ANTHROPIC_API_KEY="your-key-here"
    python 03_layer2_inclusion.py layer1_results.csv layer2_results.csv

Dependencies:
    pip install google-generativeai anthropic pandas tqdm
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import local modules
from prompts import format_layer2_prompt
from config import GEMINI_PRO, CLAUDE_SONNET, get_api_key, INCLUSION_TAGS
from token_logger import get_logger

# Try to import SDKs
try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed")
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Error: anthropic not installed")
    print("Run: pip install anthropic")
    sys.exit(1)


def setup_gemini(api_key: str, model_name: str) -> Any:
    """Initialize Gemini client."""
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.5,
        "top_p": 0.95,
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "inclusion_check": {
                    "type": "object",
                    "properties": {
                        "INC-1": {"type": "object", "properties": {"status": {"type": "string", "enum": ["yes", "unclear", "no"]}, "evidence": {"type": "string"}}, "required": ["status", "evidence"]},
                        "INC-2": {"type": "object", "properties": {"status": {"type": "string", "enum": ["yes", "unclear", "no"]}, "evidence": {"type": "string"}}, "required": ["status", "evidence"]},
                        "INC-3": {"type": "object", "properties": {"status": {"type": "string", "enum": ["yes", "unclear", "no"]}, "evidence": {"type": "string"}}, "required": ["status", "evidence"]},
                        "INC-4": {"type": "object", "properties": {"status": {"type": "string", "enum": ["yes", "unclear", "no"]}, "evidence": {"type": "string"}}, "required": ["status", "evidence"]},
                        "INC-5": {"type": "object", "properties": {"status": {"type": "string", "enum": ["yes", "unclear", "no"]}, "evidence": {"type": "string"}}, "required": ["status", "evidence"]},
                    },
                    "required": ["INC-1", "INC-2", "INC-3", "INC-4", "INC-5"]
                },
                "decision": {"type": "string", "enum": ["include", "exclude"]},
                "confidence": {"type": "string", "enum": ["high", "low"]},
                "reasoning": {"type": "string"}
            },
            "required": ["inclusion_check", "decision", "confidence", "reasoning"]
        }
    }
    
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )
    
    return model


def setup_anthropic(api_key: str) -> anthropic.Anthropic:
    """Initialize Anthropic client."""
    return anthropic.Anthropic(api_key=api_key)


def parse_json_response(response_text: str) -> Optional[Dict]:
    """Parse JSON from model response, handling common issues."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        import re
        # Try markdown code block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try raw JSON object
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    
    return None


def extract_inclusion_result(parsed: Dict) -> Dict[str, Any]:
    """Extract standardized result from parsed JSON."""
    result = {
        "decision": parsed.get("decision", "include"),
        "confidence": parsed.get("confidence", "low"),
        "reasoning": parsed.get("reasoning"),
        "inclusion_check": {},
        "error": None
    }
    
    inc_check = parsed.get("inclusion_check", {})
    for tag in ["INC-1", "INC-2", "INC-3", "INC-4", "INC-5"]:
        tag_data = inc_check.get(tag, {})
        result["inclusion_check"][tag] = {
            "status": tag_data.get("status", "unclear"),
            "evidence": tag_data.get("evidence")
        }
    
    return result


def screen_with_gemini_pro(
    model: Any,
    title: str,
    abstract: str,
    record_id: Optional[str] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Screen a record with Gemini Pro."""
    prompt = format_layer2_prompt(title, abstract)
    logger = get_logger()
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            # Extract token usage (including thinking tokens)
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(response.usage_metadata, 'total_token_count', input_tokens + output_tokens)
            
            # Log usage
            logger.log_usage(
                model=GEMINI_PRO.name,
                input_tokens=input_tokens,
                output_tokens=total_tokens - input_tokens,
                layer="L2",
                record_id=record_id
            )
            
            parsed = parse_json_response(response.text)
            
            if parsed and "decision" in parsed:
                result = extract_inclusion_result(parsed)
                result["raw_response"] = response.text[:500]
                result["input_tokens"] = input_tokens
                result["output_tokens"] = output_tokens
                result["total_tokens"] = total_tokens
                return result
            
            print(f"  [Gemini Retry] Invalid JSON (Attempt {attempt+1}/{max_retries})")
            print(f"  [Gemini Debug] Response: {response.text[:200]}...")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
                
        except Exception as e:
            print(f"  [Gemini Error] {e} (Attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {
                "decision": "include",
                "confidence": "low",
                "reasoning": None,
                "inclusion_check": {tag: {"status": "unclear", "evidence": None} 
                                   for tag in INCLUSION_TAGS},
                "error": str(e),
                "raw_response": None
            }
    
    return {
        "decision": "include",
        "confidence": "low",
        "reasoning": "Parsing failed",
        "inclusion_check": {tag: {"status": "unclear", "evidence": None} 
                           for tag in INCLUSION_TAGS},
        "error": "Max retries",
        "raw_response": None
    }


def screen_with_claude(
    client: anthropic.Anthropic,
    title: str,
    abstract: str,
    record_id: Optional[str] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Screen a record with Claude Sonnet 4.5."""
    prompt = format_layer2_prompt(title, abstract)
    logger = get_logger()
    
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=CLAUDE_SONNET.name,
                max_tokens=16000,  # Increased for thinking + output
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000  # Budget for thinking
                },
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract token usage (includes thinking tokens in output_tokens)
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            
            # Log usage
            logger.log_usage(
                model=CLAUDE_SONNET.name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                layer="L2",
                record_id=record_id
            )
            
            # Extract text response and thinking block
            response_text = ""
            thinking_text = ""
            for block in message.content:
                if hasattr(block, 'thinking'):
                    thinking_text = block.thinking
                elif hasattr(block, 'text'):
                    response_text = block.text
            
            parsed = parse_json_response(response_text)
            
            if parsed and "decision" in parsed:
                result = extract_inclusion_result(parsed)
                result["raw_response"] = response_text[:500]
                result["thinking"] = thinking_text[:1000] if thinking_text else ""
                result["input_tokens"] = input_tokens
                result["output_tokens"] = output_tokens
                result["total_tokens"] = input_tokens + output_tokens
                return result
            
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {
                "decision": "include",
                "confidence": "low",
                "reasoning": None,
                "inclusion_check": {tag: {"status": "unclear", "evidence": None} 
                                   for tag in INCLUSION_TAGS},
                "error": str(e),
                "raw_response": None
            }
    
    return {
        "decision": "include",
        "confidence": "low",
        "reasoning": "Parsing failed",
        "inclusion_check": {tag: {"status": "unclear", "evidence": None} 
                           for tag in INCLUSION_TAGS},
        "error": "Max retries",
        "raw_response": None
    }


def flatten_result(result: Dict, prefix: str) -> Dict[str, Any]:
    """Flatten nested result dict for CSV storage."""
    flat = {
        f"{prefix}_decision": result["decision"],
        f"{prefix}_confidence": result["confidence"],
        f"{prefix}_reasoning": result["reasoning"],
        f"{prefix}_error": result.get("error"),
        f"{prefix}_input_tokens": result.get("input_tokens", 0),
        f"{prefix}_output_tokens": result.get("output_tokens", 0),
        f"{prefix}_total_tokens": result.get("total_tokens", 0),
    }
    
    for tag in ["INC-1", "INC-2", "INC-3", "INC-4", "INC-5"]:
        tag_key = tag.lower().replace("-", "")
        inc_data = result["inclusion_check"].get(tag, {})
        flat[f"{prefix}_{tag_key}_status"] = inc_data.get("status", "unclear")
        flat[f"{prefix}_{tag_key}_evidence"] = inc_data.get("evidence")
    
    return flat


def process_layer2(
    input_csv: str,
    output_csv: str,
    gemini_model: Any,
    anthropic_client: anthropic.Anthropic,
    save_interval: int = 10,
    batch_parallel_size: int = 100,
    delay_between_batches: float = 2.0,
    resume_from: Optional[int] = None
) -> None:
    """
    Process Layer 1 passed records through Layer 2 verification.
    
    Features:
    - Parallel batch processing (100 records at a time)
    - Both models called in parallel for each record
    - Automatic checkpoint saving
    
    Args:
        input_csv: Path to Layer 1 results
        output_csv: Output path
        save_interval: Save every N processed records
        batch_parallel_size: Number of records to process in parallel (default: 100)
        delay_between_batches: Delay between batches for rate limiting
        resume_from: Resume from specific index
    """
    # Load data
    df = pd.read_csv(input_csv)
    
    # Filter to only "pass" records from Layer 1
    if 'L1_decision' in df.columns:
        pass_mask = df['L1_decision'] == 'pass'
        pass_indices = df[pass_mask].index.tolist()
    else:
        print("Error: L1_decision column not found. Run Layer 1 first.")
        sys.exit(1)
    
    total_to_process = len(pass_indices)
    
    print(f"\n{'='*60}")
    print(f"LAYER 2: INCLUSION VERIFICATION (BATCH PARALLEL)")
    print(f"{'='*60}")
    print(f"Total records from Layer 1: {len(df)}")
    print(f"Passed to Layer 2: {total_to_process}")
    print(f"Models: {GEMINI_PRO.name} + {CLAUDE_SONNET.name}")
    print(f"Batch size: {batch_parallel_size} records (parallel)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize columns for both models
    for prefix in ['L2_pro', 'L2_sonnet']:
        cols = [
            f'{prefix}_decision',
            f'{prefix}_confidence',
            f'{prefix}_reasoning',
            f'{prefix}_error',
            f'{prefix}_inc1_status', f'{prefix}_inc1_evidence',
            f'{prefix}_inc2_status', f'{prefix}_inc2_evidence',
            f'{prefix}_inc3_status', f'{prefix}_inc3_evidence',
            f'{prefix}_inc4_status', f'{prefix}_inc4_evidence',
            f'{prefix}_inc5_status', f'{prefix}_inc5_evidence',
        ]
        for col in cols:
            if col not in df.columns:
                df[col] = None
    
    # Agreement columns
    for col in ['L2_models_agree', 'needs_human_review', 'L2_timestamp']:
        if col not in df.columns:
            df[col] = None
    
    # Determine starting point
    start_idx = 0
    if resume_from is not None:
        start_idx = resume_from
    
    # Counters
    include_count = 0
    exclude_count = 0
    disagree_count = 0
    
    def process_single_record(idx: int) -> Tuple[int, Dict, Dict]:
        """Process a single record with both models in parallel."""
        row = df.iloc[idx]
        title = str(row.get('title', ''))
        abstract = str(row.get('abstract', ''))
        record_id = str(row.get('record_id', idx))
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            pro_future = executor.submit(
                screen_with_gemini_pro, gemini_model, title, abstract, record_id
            )
            sonnet_future = executor.submit(
                screen_with_claude, anthropic_client, title, abstract, record_id
            )
            
            pro_result = pro_future.result()
            sonnet_result = sonnet_future.result()
        
        return idx, pro_result, sonnet_result
    
    try:
        # Process in batches
        indices_to_process = pass_indices[start_idx:]
        num_batches = (len(indices_to_process) + batch_parallel_size - 1) // batch_parallel_size
        
        for batch_num in range(num_batches):
            batch_start = batch_num * batch_parallel_size
            batch_end = min(batch_start + batch_parallel_size, len(indices_to_process))
            batch_indices = indices_to_process[batch_start:batch_end]
            
            print(f"\n[Batch {batch_num + 1}/{num_batches}] Processing {len(batch_indices)} records...")
            
            # Process entire batch in parallel
            with ThreadPoolExecutor(max_workers=batch_parallel_size) as batch_executor:
                futures = {
                    batch_executor.submit(process_single_record, idx): idx 
                    for idx in batch_indices
                }
                
                for future in tqdm(as_completed(futures), 
                                   total=len(futures),
                                   desc=f"Batch {batch_num + 1}"):
                    idx, pro_result, sonnet_result = future.result()
                    
                    # Flatten and store results
                    pro_flat = flatten_result(pro_result, 'L2_pro')
                    sonnet_flat = flatten_result(sonnet_result, 'L2_sonnet')
                    
                    for key, value in pro_flat.items():
                        df.at[idx, key] = value
                    for key, value in sonnet_flat.items():
                        df.at[idx, key] = value
                    
                    # Check agreement
                    models_agree = pro_result['decision'] == sonnet_result['decision']
                    df.at[idx, 'L2_models_agree'] = models_agree
                    
                    # Determine if human review needed
                    needs_review = (
                        not models_agree or 
                        pro_result['decision'] == 'include' or 
                        sonnet_result['decision'] == 'include'
                    )
                    df.at[idx, 'needs_human_review'] = needs_review
                    df.at[idx, 'L2_timestamp'] = datetime.now().isoformat()
                    
                    # Update counters
                    if models_agree:
                        if pro_result['decision'] == 'include':
                            include_count += 1
                        else:
                            exclude_count += 1
                    else:
                        disagree_count += 1
            
            # Save after each batch
            df.to_csv(output_csv, index=False)
            processed_so_far = start_idx + batch_end
            print(f"[Checkpoint] Saved {processed_so_far}/{total_to_process} records to {output_csv}")
            
            # Rate limiting between batches
            if batch_num < num_batches - 1:
                print(f"Waiting {delay_between_batches}s before next batch...")
                time.sleep(delay_between_batches)
    
    except KeyboardInterrupt:
        print(f"\n\nInterrupted! Saving progress...")
        df.to_csv(output_csv, index=False)
        print(f"Progress saved to {output_csv}")
        sys.exit(1)
    
    # Final save
    df.to_csv(output_csv, index=False)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"LAYER 2 COMPLETE")
    print(f"{'='*60}")
    print(f"Processed: {total_to_process}")
    print(f"\nAgreement:")
    print(f"  Both INCLUDE: {include_count}")
    print(f"  Both EXCLUDE: {exclude_count}")
    print(f"  Disagree: {disagree_count}")
    if total_to_process > 0:
        print(f"\nAgreement rate: {100*(include_count+exclude_count)/total_to_process:.1f}%")
    
    # Records needing review
    needs_review_count = df['needs_human_review'].sum()
    print(f"\nRecords needing human review: {needs_review_count}")
    
    # Token usage summary
    logger = get_logger()
    logger.print_summary()
    
    # Save cost report
    report_prefix = output_csv.replace('.csv', '')
    logger.save_report(f"{report_prefix}_cost_report.json")
    logger.save_summary_csv(f"{report_prefix}_cost_summary.csv")
    
    print(f"{'='*60}\n")
    
    print(f"\nResults saved to: {output_csv}")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <layer1_results.csv> <output.csv> [--resume N] [--batch N]")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_csv = sys.argv[2]
    
    resume_from = None
    batch_size = 100  # Default batch size
    
    if '--resume' in sys.argv:
        resume_idx = sys.argv.index('--resume')
        if resume_idx + 1 < len(sys.argv):
            resume_from = int(sys.argv[resume_idx + 1])
    
    if '--batch' in sys.argv:
        batch_idx = sys.argv.index('--batch')
        if batch_idx + 1 < len(sys.argv):
            batch_size = int(sys.argv[batch_idx + 1])
    
    if not os.path.exists(input_csv):
        print(f"Error: Input file not found: {input_csv}")
        sys.exit(1)
    
    # Setup APIs
    try:
        gemini_key = get_api_key(GEMINI_PRO.api_key_env)
        anthropic_key = get_api_key(CLAUDE_SONNET.api_key_env)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    gemini_model = setup_gemini(gemini_key, GEMINI_PRO.name)
    anthropic_client = setup_anthropic(anthropic_key)
    
    # Run processing
    process_layer2(
        input_csv=input_csv,
        output_csv=output_csv,
        gemini_model=gemini_model,
        anthropic_client=anthropic_client,
        batch_parallel_size=batch_size,
        delay_between_batches=2.0,
        resume_from=resume_from
    )


if __name__ == '__main__':
    main()
