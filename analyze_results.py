#!/usr/bin/env python3
"""Analyze Layer 2 results and cost."""

import pandas as pd

def analyze_results():
    df = pd.read_csv('layer2_results.csv')

    print('='*60)
    print('LAYER 2 FINAL RESULTS')
    print('='*60)

    # Basic stats
    total = len(df[df['L2_pro_decision'].notna()])
    print(f'Total processed: {total}')

    # Errors
    gemini_errors = df['L2_pro_error'].notna().sum()
    claude_errors = df['L2_sonnet_error'].notna().sum()
    print(f'Remaining Gemini errors: {gemini_errors}')
    print(f'Remaining Claude errors: {claude_errors}')

    # Decisions
    both_inc = len(df[(df['L2_pro_decision']=='include') & (df['L2_sonnet_decision']=='include')])
    both_exc = len(df[(df['L2_pro_decision']=='exclude') & (df['L2_sonnet_decision']=='exclude')])
    disagree = total - both_inc - both_exc

    print()
    print('AGREEMENT:')
    print(f'  Both INCLUDE: {both_inc}')
    print(f'  Both EXCLUDE: {both_exc}')
    print(f'  Disagree: {disagree}')
    print(f'  Agreement rate: {100*(both_inc+both_exc)/total:.1f}%')

    # INC-1 analysis
    print()
    print('INC-1 (Study Design):')
    print(f"  Gemini yes: {len(df[df['L2_pro_inc1_status']=='yes'])}")
    print(f"  Gemini no: {len(df[df['L2_pro_inc1_status']=='no'])}")
    print(f"  Gemini unclear: {len(df[df['L2_pro_inc1_status']=='unclear'])}")
    print(f"  Claude yes: {len(df[df['L2_sonnet_inc1_status']=='yes'])}")
    print(f"  Claude no: {len(df[df['L2_sonnet_inc1_status']=='no'])}")
    print(f"  Claude unclear: {len(df[df['L2_sonnet_inc1_status']=='unclear'])}")
    
    # Cost analysis
    print()
    print('='*60)
    print('COST ANALYSIS')
    print('='*60)
    
    try:
        cost_df = pd.read_csv('layer2_results_cost_summary.csv')
        print(cost_df.to_string(index=False))
    except:
        print('Cost summary file not found')
    
    # Regenerate human review list
    print()
    print('='*60)
    print('HUMAN REVIEW LIST')
    print('='*60)
    
    # Both INCLUDE
    both_inc_df = df[(df['L2_pro_decision']=='include') & (df['L2_sonnet_decision']=='include')].copy()
    both_inc_df['review_category'] = 'both_include'
    
    # Disagreement
    disagree_df = df[(df['L2_pro_decision'] != df['L2_sonnet_decision'])].copy()
    disagree_df['review_category'] = 'disagreement'
    
    # Combine
    review = pd.concat([both_inc_df, disagree_df])
    
    cols = ['record_id', 'title', 'review_category',
            'L2_pro_decision', 'L2_pro_confidence', 'L2_pro_inc1_status',
            'L2_sonnet_decision', 'L2_sonnet_confidence', 'L2_sonnet_inc1_status']
    
    review_df = review[cols].copy()
    review_df.to_csv('human_review_list.csv', index=False)
    
    print(f'Total for human review: {len(review_df)}')
    print(f'  Both INCLUDE: {len(both_inc_df)}')
    print(f'  Disagreement: {len(disagree_df)}')
    print(f'Saved to: human_review_list.csv')


if __name__ == '__main__':
    analyze_results()
