#!/usr/bin/env python3
"""
RIS Parser for Systematic Review Screening
===========================================

This script parses EndNote RIS export files and generates a structured CSV 
for LLM-assisted title/abstract screening.

Part of: Systematic Review Update - Machine Perfusion in Liver Transplantation
Original study: Kang et al. (2025) International Journal of Surgery

Author: [Your Name]
Date: 2024-12-06
Version: 1.0.0

Usage:
    python 01_parse_ris.py input.ris output.csv

Output CSV Schema:
    - record_id: EndNote Record Number (for cross-referencing)
    - pmid: PubMed ID (if available)
    - doi: Digital Object Identifier
    - title: Article title
    - abstract: Full abstract text
    - authors: Semicolon-separated author list
    - year: Publication year
    - journal: Journal name
    - source: Database source (PubMed/EMBASE/Other)
    - llm_decision: [blank - to be filled by LLM]
    - llm_confidence: [blank - to be filled by LLM]
    - llm_reasoning: [blank - to be filled by LLM]
    - evidence_quote: [blank - to be filled by LLM]
    - human_decision: [blank - to be filled by reviewer]
    - discrepancy: [blank - TRUE/FALSE]
    - resolution_note: [blank - if discrepancy exists]
    - final_decision: [blank - final include/exclude]
    - timestamp: [blank - processing timestamp]

License: CC BY 4.0
Repository: [Zenodo DOI to be added]
"""

import re
import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def parse_ris_file(filepath: str) -> List[Dict[str, str]]:
    """
    Parse RIS file and extract relevant fields.
    
    RIS Format Reference:
    - TY: Type of reference
    - TI: Title
    - AB: Abstract
    - AU: Author (multiple allowed)
    - PY: Publication year
    - T2: Secondary title (journal name)
    - DO: DOI
    - AN: Accession number (often PMID)
    - ID: EndNote Record Number
    - DB: Database
    - ER: End of record
    
    Args:
        filepath: Path to RIS file
        
    Returns:
        List of dictionaries, one per record
    """
    records = []
    current_record = {}
    current_field = None
    authors = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n\r')
            
            # Check for field tag (e.g., "TY  - ")
            match = re.match(r'^([A-Z][A-Z0-9])  - (.*)$', line)
            
            if match:
                tag, value = match.groups()
                current_field = tag
                
                if tag == 'TY':
                    # Start of new record
                    current_record = {'type': value}
                    authors = []
                elif tag == 'ER':
                    # End of record - save it
                    if authors:
                        current_record['authors'] = '; '.join(authors)
                    records.append(current_record)
                    current_record = {}
                    current_field = None
                elif tag == 'TI':
                    current_record['title'] = value
                elif tag == 'AB':
                    current_record['abstract'] = value
                elif tag == 'AU':
                    authors.append(value)
                elif tag == 'PY':
                    current_record['year'] = value
                elif tag == 'T2':
                    current_record['journal'] = value
                elif tag == 'DO':
                    current_record['doi'] = value
                elif tag == 'AN':
                    current_record['accession'] = value
                elif tag == 'ID':
                    current_record['record_id'] = value
                elif tag == 'DB':
                    current_record['database'] = value
            else:
                # Continuation of previous field (multi-line content)
                if current_field == 'AB' and 'abstract' in current_record:
                    current_record['abstract'] += ' ' + line.strip()
                elif current_field == 'TI' and 'title' in current_record:
                    current_record['title'] += ' ' + line.strip()
    
    return records


def determine_source(record: Dict[str, str]) -> str:
    """
    Determine database source from record metadata.
    
    Args:
        record: Parsed record dictionary
        
    Returns:
        Source identifier (PubMed/EMBASE/Other)
    """
    db = record.get('database', '').lower()
    
    if 'pubmed' in db or 'nlm' in db or 'medline' in db:
        return 'PubMed'
    elif 'embase' in db or 'ovid' in db:
        return 'EMBASE'
    else:
        return 'Other'


def extract_pmid(record: Dict[str, str]) -> str:
    """
    Extract PMID from accession number if available.
    
    Args:
        record: Parsed record dictionary
        
    Returns:
        PMID string or empty string
    """
    accession = record.get('accession', '')
    # PMID is typically 8 digits
    if accession and accession.isdigit() and len(accession) >= 7:
        return accession
    return ''


def create_screening_csv(records: List[Dict[str, str]], output_path: str) -> None:
    """
    Create CSV file for screening with all required fields.
    
    Args:
        records: List of parsed records
        output_path: Path for output CSV
    """
    fieldnames = [
        # Identifiers
        'record_id',
        'pmid', 
        'doi',
        # Content
        'title',
        'abstract',
        'authors',
        'year',
        'journal',
        'source',
        # LLM Screening
        'llm_decision',
        'llm_confidence',
        'llm_reasoning',
        'evidence_quote',
        # Human Review
        'human_decision',
        'discrepancy',
        'resolution_note',
        # Final
        'final_decision',
        'timestamp'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            row = {
                'record_id': record.get('record_id', ''),
                'pmid': extract_pmid(record),
                'doi': record.get('doi', ''),
                'title': record.get('title', ''),
                'abstract': record.get('abstract', ''),
                'authors': record.get('authors', ''),
                'year': record.get('year', ''),
                'journal': record.get('journal', ''),
                'source': determine_source(record),
                # Leave screening fields blank
                'llm_decision': '',
                'llm_confidence': '',
                'llm_reasoning': '',
                'evidence_quote': '',
                'human_decision': '',
                'discrepancy': '',
                'resolution_note': '',
                'final_decision': '',
                'timestamp': ''
            }
            writer.writerow(row)


def print_summary(records: List[Dict[str, str]]) -> None:
    """Print parsing summary statistics."""
    total = len(records)
    with_abstract = sum(1 for r in records if r.get('abstract'))
    with_pmid = sum(1 for r in records if extract_pmid(r))
    
    sources = {}
    for r in records:
        src = determine_source(r)
        sources[src] = sources.get(src, 0) + 1
    
    years = {}
    for r in records:
        yr = r.get('year', 'Unknown')
        years[yr] = years.get(yr, 0) + 1
    
    print("\n" + "="*50)
    print("RIS PARSING SUMMARY")
    print("="*50)
    print(f"Total records:        {total}")
    print(f"With abstract:        {with_abstract} ({100*with_abstract/total:.1f}%)")
    print(f"With PMID:            {with_pmid} ({100*with_pmid/total:.1f}%)")
    print(f"\nBy source:")
    for src, count in sorted(sources.items()):
        print(f"  {src}: {count}")
    print(f"\nBy year:")
    for yr, count in sorted(years.items(), reverse=True):
        print(f"  {yr}: {count}")
    print("="*50 + "\n")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.ris> <output.csv>")
        print(f"Example: {sys.argv[0]} MP_Liver_Update.ris screening_records.csv")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not Path(input_path).exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"Parsing RIS file: {input_path}")
    records = parse_ris_file(input_path)
    
    print_summary(records)
    
    print(f"Creating screening CSV: {output_path}")
    create_screening_csv(records, output_path)
    
    print(f"Done! {len(records)} records ready for screening.")


if __name__ == '__main__':
    main()
