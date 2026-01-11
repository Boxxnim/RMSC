#!/usr/bin/env python3
"""
Export extracted data to R-compatible format (gemtc/netmeta)

Converts our wide-format Excel to long format:
  Wide:  Study_ID | EAD_Int_Events | EAD_Int_Total | EAD_Ctrl_Events | EAD_Ctrl_Total
  Long:  study | treatment | responders | sampleSize | design
"""

import pandas as pd
import openpyxl
from pathlib import Path
from typing import Literal, List, Dict
import argparse


# Outcome column mappings (wide format columns -> gemtc fields)
OUTCOME_MAPPINGS = {
    "EAD": {
        "int_events": "EAD_Int_Events",
        "int_total": "EAD_Int_Total",
        "ctrl_events": "EAD_Ctrl_Events",
        "ctrl_total": "EAD_Ctrl_Total",
    },
    "NAS": {
        "int_events": "NAS_Int_Events",
        "int_total": "NAS_Int_Total", 
        "ctrl_events": "NAS_Ctrl_Events",
        "ctrl_total": "NAS_Ctrl_Total",
    },
    "TBC": {
        "int_events": "TBC_Int_Events",
        "int_total": "TBC_Int_Total",
        "ctrl_events": "TBC_Ctrl_Events",
        "ctrl_total": "TBC_Ctrl_Total",
    },
    "PNF": {
        "int_events": "PNF_Int_Events",
        "int_total": "PNF_Int_Total",
        "ctrl_events": "PNF_Ctrl_Events",
        "ctrl_total": "PNF_Ctrl_Total",
    },
    "HAT": {
        "int_events": "HAT_Int_Events",
        "int_total": "HAT_Int_Total",
        "ctrl_events": "HAT_Ctrl_Events",
        "ctrl_total": "HAT_Ctrl_Total",
    },
    "MC": {
        "int_events": "MC_Int_Events",
        "int_total": "MC_Int_Total",
        "ctrl_events": "MC_Ctrl_Events",
        "ctrl_total": "MC_Ctrl_Total",
    },
    "ACR": {
        "int_events": "ACR_Int_Events",
        "int_total": "ACR_Int_Total",
        "ctrl_events": "ACR_Ctrl_Events",
        "ctrl_total": "ACR_Ctrl_Total",
    },
    "Retransplantation": {
        "int_events": "Retx_Int_Events",
        "int_total": "Retx_Int_Total",
        "ctrl_events": "Retx_Ctrl_Events",
        "ctrl_total": "Retx_Ctrl_Total",
    },
    # Survival outcomes
    "GS_1yr": {
        "int_events": "GS_1yr_Int_Events",
        "int_total": "GS_1yr_Int_Total",
        "ctrl_events": "GS_1yr_Ctrl_Events",
        "ctrl_total": "GS_1yr_Ctrl_Total",
    },
    "PS_1yr": {
        "int_events": "PS_1yr_Int_Events",
        "int_total": "PS_1yr_Int_Total",
        "ctrl_events": "PS_1yr_Ctrl_Events",
        "ctrl_total": "PS_1yr_Ctrl_Total",
    },
}


def wide_to_long(excel_path: str, outcome: str, sheet_name: str = "Outcome_Data") -> pd.DataFrame:
    """Convert our wide format to gemtc-compatible long format.
    
    Args:
        excel_path: Path to our extraction Excel file
        outcome: Outcome name (EAD, NAS, TBC, etc.)
        sheet_name: Sheet containing outcome data
        
    Returns:
        DataFrame with columns: study, treatment, responders, sampleSize, design
    """
    if outcome not in OUTCOME_MAPPINGS:
        raise ValueError(f"Unknown outcome: {outcome}. Available: {list(OUTCOME_MAPPINGS.keys())}")
    
    mapping = OUTCOME_MAPPINGS[outcome]
    
    # Read data
    df = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')
    
    # Also read study characteristics for design info
    chars_df = pd.read_excel(excel_path, sheet_name='Study_Characteristics', engine='openpyxl')
    design_map = dict(zip(chars_df['Study_ID'], chars_df['Study_Design']))
    intervention_map = dict(zip(chars_df['Study_ID'], chars_df['Intervention_Type']))
    
    rows = []
    
    for _, row in df.iterrows():
        study_id = row.get('Study_ID')
        if not study_id or pd.isna(study_id):
            continue
            
        # Check if outcome is reported
        reported_col = f"{outcome}_Reported"
        if reported_col in df.columns and not row.get(reported_col, True):
            continue
        
        # Get values
        int_events = row.get(mapping['int_events'])
        int_total = row.get(mapping['int_total'])
        ctrl_events = row.get(mapping['ctrl_events'])
        ctrl_total = row.get(mapping['ctrl_total'])
        
        # Skip if no data
        if pd.isna(int_total) or pd.isna(ctrl_total):
            continue
        
        # Determine design
        design = design_map.get(study_id, 'non-RCT')
        if 'RCT' in str(design).upper() or 'RANDOM' in str(design).upper():
            design = 'RCT'
        else:
            design = 'non-RCT'
        
        # Determine treatment names
        intervention_type = intervention_map.get(study_id, 'MP')  # HOPE, NMP, etc.
        
        # Add intervention row
        rows.append({
            'study': study_id,
            'treatment': intervention_type,
            'responders': int(int_events) if not pd.isna(int_events) else 0,
            'sampleSize': int(int_total),
            'design': design
        })
        
        # Add control row
        rows.append({
            'study': study_id,
            'treatment': 'SCS',  # Control is always SCS
            'responders': int(ctrl_events) if not pd.isna(ctrl_events) else 0,
            'sampleSize': int(ctrl_total),
            'design': design
        })
    
    return pd.DataFrame(rows)


def export_all_outcomes(excel_path: str, output_path: str):
    """Export all outcomes to a single Excel file with multiple sheets (R-compatible).
    
    Output format matches legacy ECD_RoB.xlsx structure.
    """
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for outcome in OUTCOME_MAPPINGS.keys():
            try:
                df = wide_to_long(excel_path, outcome)
                if len(df) > 0:
                    df.to_excel(writer, sheet_name=outcome, index=False)
                    print(f"  ✅ {outcome}: {len(df)} rows")
                else:
                    print(f"  ⚠️ {outcome}: no data")
            except Exception as e:
                print(f"  ❌ {outcome}: {e}")
    
    print(f"\n📊 Exported to: {output_path}")


def export_meta_regression_data(excel_path: str, output_path: str):
    """Export time metrics for meta-regression analysis."""
    
    # Read time metrics
    time_df = pd.read_excel(excel_path, sheet_name='Time_Metrics', engine='openpyxl')
    chars_df = pd.read_excel(excel_path, sheet_name='Study_Characteristics', engine='openpyxl')
    
    # Merge with study info
    merged = time_df.merge(chars_df[['Study_ID', 'Study_Design', 'Donor_Type', 'Intervention_Type']], 
                           on='Study_ID', how='left')
    
    # Export
    merged.to_excel(output_path, index=False)
    print(f"📊 Meta-regression data exported to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export extraction data to R-compatible format")
    parser.add_argument("-i", "--input", required=True, help="Input Excel file (our extraction)")
    parser.add_argument("-o", "--output", default="r_export.xlsx", help="Output Excel file for R")
    parser.add_argument("--outcome", help="Single outcome to export (default: all)")
    parser.add_argument("--meta-regression", action="store_true", help="Export meta-regression data")
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("EXPORT FOR R (gemtc/netmeta)")
    print(f"{'='*60}")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}\n")
    
    if args.meta_regression:
        export_meta_regression_data(args.input, args.output)
    elif args.outcome:
        df = wide_to_long(args.input, args.outcome)
        df.to_excel(args.output, index=False)
        print(f"✅ {args.outcome}: {len(df)} rows exported to {args.output}")
    else:
        export_all_outcomes(args.input, args.output)
