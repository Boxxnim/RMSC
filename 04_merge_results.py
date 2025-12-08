#!/usr/bin/env python3
"""
Merge Results and Generate Summary
==================================

This script merges Layer 1 and Layer 2 results and generates:
1. Final screening decisions
2. Summary statistics
3. Records for human review export

Usage:
    python 04_merge_results.py layer2_results.csv final_screening.csv
"""

import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List


def determine_final_decision(row: pd.Series) -> Dict[str, str]:
    """
    Determine final decision based on Layer 1 and Layer 2 results.
    
    Logic:
    - L1 exclude → Exclude
    - L2 both exclude → Exclude
    - L2 both include → Include (needs human verification)
    - L2 disagree → Human review required
    """
    result = {
        "auto_decision": None,
        "review_priority": "none",
        "review_reason": None
    }
    
    # Layer 1 excluded
    if row.get('L1_decision') == 'exclude':
        result["auto_decision"] = "exclude"
        result["review_priority"] = "none"
        return result
    
    # Layer 2 results
    pro_decision = row.get('L2_pro_decision')
    opus_decision = row.get('L2_opus_decision')
    
    # Both models agree
    if pro_decision == opus_decision:
        if pro_decision == 'include':
            result["auto_decision"] = "include"
            result["review_priority"] = "high"
            result["review_reason"] = "Both models include - verify"
        else:
            result["auto_decision"] = "exclude"
            result["review_priority"] = "low"
            result["review_reason"] = "Both models exclude"
    else:
        # Disagreement
        result["auto_decision"] = "uncertain"
        result["review_priority"] = "high"
        result["review_reason"] = f"Disagreement: Pro={pro_decision}, Opus={opus_decision}"
    
    return result


def generate_summary(df: pd.DataFrame) -> str:
    """Generate text summary of screening results."""
    total = len(df)
    
    # Layer 1 stats
    l1_exclude = (df['L1_decision'] == 'exclude').sum()
    l1_pass = (df['L1_decision'] == 'pass').sum()
    
    # Layer 2 stats (only for L1 passed)
    l2_mask = df['L1_decision'] == 'pass'
    l2_records = l2_mask.sum()
    
    if l2_records > 0:
        l2_both_include = ((df['L2_pro_decision'] == 'include') & 
                          (df['L2_opus_decision'] == 'include') & l2_mask).sum()
        l2_both_exclude = ((df['L2_pro_decision'] == 'exclude') & 
                          (df['L2_opus_decision'] == 'exclude') & l2_mask).sum()
        l2_disagree = l2_records - l2_both_include - l2_both_exclude
        
        # Agreement rate
        agreement = (l2_both_include + l2_both_exclude) / l2_records * 100 if l2_records > 0 else 0
    else:
        l2_both_include = l2_both_exclude = l2_disagree = 0
        agreement = 0
    
    # Final counts
    final_include = (df['auto_decision'] == 'include').sum()
    final_exclude = (df['auto_decision'] == 'exclude').sum()
    final_uncertain = (df['auto_decision'] == 'uncertain').sum()
    
    # Exclusion breakdown
    exclusion_breakdown = {}
    if 'L1_exclusion_tags' in df.columns:
        for tags in df['L1_exclusion_tags'].dropna():
            for tag in str(tags).split(','):
                tag = tag.strip()
                if tag:
                    exclusion_breakdown[tag] = exclusion_breakdown.get(tag, 0) + 1
    
    summary = f"""
{'='*60}
SCREENING SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

OVERVIEW
--------
Total records screened: {total}

LAYER 1: EXCLUSION SCREENING
----------------------------
Excluded: {l1_exclude} ({100*l1_exclude/total:.1f}%)
Passed to Layer 2: {l1_pass} ({100*l1_pass/total:.1f}%)

Exclusion breakdown:
"""
    for tag, count in sorted(exclusion_breakdown.items()):
        summary += f"  {tag}: {count}\n"
    
    summary += f"""
LAYER 2: INCLUSION VERIFICATION
-------------------------------
Records evaluated: {l2_records}
Both models INCLUDE: {l2_both_include}
Both models EXCLUDE: {l2_both_exclude}
Disagreement: {l2_disagree}
Inter-model agreement: {agreement:.1f}%

FINAL DECISIONS (Auto)
----------------------
Include (pending human review): {final_include}
Exclude: {final_exclude}
Uncertain (needs review): {final_uncertain}

HUMAN REVIEW REQUIRED
---------------------
High priority (include/uncertain): {final_include + final_uncertain}
Low priority (spot-check excludes): ~{int(l2_both_exclude * 0.1)} (10% sample)

{'='*60}
"""
    return summary


def export_for_review(df: pd.DataFrame, output_prefix: str) -> None:
    """Export records needing human review."""
    
    # High priority: includes and uncertains
    high_priority = df[df['review_priority'] == 'high'].copy()
    if len(high_priority) > 0:
        cols_to_keep = [
            'record_id', 'pmid', 'title', 'abstract', 'year', 'journal',
            'L1_decision', 'L1_exclusion_tags',
            'L2_pro_decision', 'L2_pro_confidence', 'L2_pro_reasoning',
            'L2_opus_decision', 'L2_opus_confidence', 'L2_opus_reasoning',
            'auto_decision', 'review_reason'
        ]
        cols_to_keep = [c for c in cols_to_keep if c in high_priority.columns]
        high_priority[cols_to_keep].to_csv(
            f"{output_prefix}_human_review_high.csv", 
            index=False
        )
        print(f"Exported {len(high_priority)} high-priority records")
    
    # Low priority sample
    low_priority = df[df['review_priority'] == 'low']
    if len(low_priority) > 0:
        sample_size = min(len(low_priority), max(10, int(len(low_priority) * 0.1)))
        sample = low_priority.sample(n=sample_size, random_state=42)
        cols_to_keep = [
            'record_id', 'pmid', 'title', 'abstract',
            'L2_pro_decision', 'L2_pro_reasoning',
            'L2_opus_decision', 'L2_opus_reasoning',
            'auto_decision'
        ]
        cols_to_keep = [c for c in cols_to_keep if c in sample.columns]
        sample[cols_to_keep].to_csv(
            f"{output_prefix}_human_review_low_sample.csv",
            index=False
        )
        print(f"Exported {sample_size} low-priority sample records")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <layer2_results.csv> <output_prefix>")
        print(f"Example: {sys.argv[0]} layer2_results.csv final_screening")
        sys.exit(1)
    
    input_csv = sys.argv[1]
    output_prefix = sys.argv[2]
    
    # Load data
    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # Determine final decisions
    print("Determining final decisions...")
    decisions = df.apply(determine_final_decision, axis=1)
    decisions_df = pd.DataFrame(decisions.tolist())
    
    for col in decisions_df.columns:
        df[col] = decisions_df[col]
    
    # Add human review columns
    df['human_decision'] = None
    df['resolution_note'] = None
    df['final_decision'] = df['auto_decision']  # Will be updated by human
    
    # Save full results
    output_csv = f"{output_prefix}.csv"
    df.to_csv(output_csv, index=False)
    print(f"Saved full results to {output_csv}")
    
    # Generate summary
    summary = generate_summary(df)
    print(summary)
    
    # Save summary
    summary_file = f"{output_prefix}_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(summary)
    print(f"Saved summary to {summary_file}")
    
    # Export review files
    print("\nExporting files for human review...")
    export_for_review(df, output_prefix)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
