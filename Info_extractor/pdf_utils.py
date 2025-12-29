"""
PDF Text Extraction Utilities
For systematic review data extraction pipeline
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re
import io


def extract_text_from_pdf(pdf_path: str, max_pages: Optional[int] = None, use_ocr: bool = False) -> str:
    """
    Extract text from PDF file
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to extract (None = all)
        use_ocr: Force OCR even if text is available
    
    Returns:
        Extracted text as string
    """
    doc = fitz.open(pdf_path)
    text_parts = []
    
    pages_to_read = min(len(doc), max_pages) if max_pages else len(doc)
    
    for page_num in range(pages_to_read):
        page = doc[page_num]
        text = page.get_text()
        
        # If no text found, try OCR
        if (not text.strip() or use_ocr) and _has_ocr_support():
            ocr_text = _ocr_page(page)
            if ocr_text:
                text = ocr_text
        
        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
    
    doc.close()
    return "\n\n".join(text_parts)


def _has_ocr_support() -> bool:
    """Check if OCR is available"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except:
        return False


def _ocr_page(page) -> str:
    """Perform OCR on a single PDF page"""
    try:
        import pytesseract
        from PIL import Image
        
        # Render page to image at higher resolution for better OCR
        mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"[OCR Error: {str(e)}]"


def extract_text_with_ocr_fallback(pdf_path: str, max_pages: Optional[int] = None) -> str:
    """
    Extract text with automatic OCR fallback
    
    First tries normal text extraction, falls back to OCR if no text found.
    """
    doc = fitz.open(pdf_path)
    text_parts = []
    needs_ocr = False
    
    pages_to_read = min(len(doc), max_pages) if max_pages else len(doc)
    
    # First pass: try normal extraction
    for page_num in range(pages_to_read):
        page = doc[page_num]
        text = page.get_text().strip()
        
        if not text:
            needs_ocr = True
            break
        
        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
    
    # If any page lacks text, use OCR for all pages
    if needs_ocr and _has_ocr_support():
        print(f"  → Using OCR for image-based PDF...")
        text_parts = []
        for page_num in range(pages_to_read):
            page = doc[page_num]
            text = _ocr_page(page)
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
    
    doc.close()
    return "\n\n".join(text_parts)


def extract_structured_sections(pdf_path: str) -> Dict[str, str]:
    """
    Extract text with section detection
    
    Attempts to identify common paper sections:
    - Abstract
    - Introduction
    - Methods
    - Results
    - Discussion
    - References
    
    Returns:
        Dictionary mapping section names to content
    """
    # Use OCR fallback for text extraction
    full_text = extract_text_with_ocr_fallback(pdf_path)
    
    # Common section headers in medical papers
    section_patterns = [
        (r'(?i)\b(abstract)\b', 'abstract'),
        (r'(?i)\b(introduction|background)\b', 'introduction'),
        (r'(?i)\b(methods?|materials?\s+and\s+methods?|patients?\s+and\s+methods?)\b', 'methods'),
        (r'(?i)\b(results?)\b', 'results'),
        (r'(?i)\b(discussion)\b', 'discussion'),
        (r'(?i)\b(conclusion)\b', 'conclusion'),
        (r'(?i)\b(references?|bibliography)\b', 'references'),
    ]
    
    # Find all section positions
    section_positions: List[Tuple[int, str]] = []
    
    for pattern, section_name in section_patterns:
        for match in re.finditer(pattern, full_text):
            section_positions.append((match.start(), section_name))
    
    # Sort by position
    section_positions.sort(key=lambda x: x[0])
    
    # Extract content between sections
    sections = {}
    for i, (pos, name) in enumerate(section_positions):
        # Get end position (start of next section or end of text)
        if i + 1 < len(section_positions):
            end_pos = section_positions[i + 1][0]
        else:
            end_pos = len(full_text)
        
        content = full_text[pos:end_pos].strip()
        
        # Only keep first occurrence of each section
        if name not in sections:
            sections[name] = content
    
    # Always include full text as fallback
    sections['full_text'] = full_text
    
    return sections


def extract_tables_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Attempt to extract table data from PDF
    
    Note: PDF table extraction is inherently imperfect.
    Returns best-effort extraction for review.
    
    Returns:
        List of table dictionaries with page and content
    """
    doc = fitz.open(pdf_path)
    tables = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get tables using PyMuPDF's table finder
        try:
            page_tables = page.find_tables()
            for table in page_tables:
                table_data = {
                    'page': page_num + 1,
                    'bbox': table.bbox,
                    'rows': [],
                    'raw_text': ''
                }
                
                # Extract cells
                for row in table.extract():
                    table_data['rows'].append(row)
                
                # Also get raw text in table area
                rect = fitz.Rect(table.bbox)
                table_data['raw_text'] = page.get_text(clip=rect)
                
                tables.append(table_data)
        except Exception as e:
            # Table extraction can fail on some PDFs
            pass
    
    doc.close()
    return tables


def get_pdf_metadata(pdf_path: str) -> Dict:
    """
    Extract PDF metadata
    
    Returns:
        Dictionary with title, author, creation date, etc.
    """
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    
    result = {
        'title': metadata.get('title', ''),
        'author': metadata.get('author', ''),
        'subject': metadata.get('subject', ''),
        'keywords': metadata.get('keywords', ''),
        'creator': metadata.get('creator', ''),
        'producer': metadata.get('producer', ''),
        'creation_date': metadata.get('creationDate', ''),
        'modification_date': metadata.get('modDate', ''),
        'page_count': len(doc),
    }
    
    doc.close()
    return result


def prepare_paper_for_extraction(pdf_path: str, include_tables: bool = False) -> str:
    """
    Prepare paper content for LLM extraction
    
    Creates a formatted string with:
    - Metadata
    - Structured sections (if detected)
    - Full text
    - Table summaries (optional)
    
    Args:
        pdf_path: Path to PDF
        include_tables: Whether to include table extraction (slower)
    
    Returns:
        Formatted string ready for LLM processing
    """
    path = Path(pdf_path)
    
    # Get metadata
    metadata = get_pdf_metadata(pdf_path)
    
    # Get structured sections
    sections = extract_structured_sections(pdf_path)
    
    # Build output
    output_parts = [
        f"=== PDF METADATA ===",
        f"Filename: {path.name}",
        f"Title: {metadata.get('title', 'Not specified')}",
        f"Author: {metadata.get('author', 'Not specified')}",
        f"Pages: {metadata.get('page_count', 'Unknown')}",
        f"",
        f"=== PAPER CONTENT ===",
    ]
    
    # Add structured sections if detected
    priority_sections = ['abstract', 'methods', 'results', 'discussion']
    for section_name in priority_sections:
        if section_name in sections:
            output_parts.append(f"\n--- {section_name.upper()} ---")
            # Truncate very long sections
            content = sections[section_name]
            if len(content) > 15000:
                content = content[:15000] + "\n[... truncated ...]"
            output_parts.append(content)
    
    # If no sections detected, use full text
    if not any(s in sections for s in priority_sections):
        output_parts.append("\n--- FULL TEXT ---")
        full_text = sections.get('full_text', '')
        if len(full_text) > 50000:
            full_text = full_text[:50000] + "\n[... truncated ...]"
        output_parts.append(full_text)
    
    # Optionally add tables
    if include_tables:
        tables = extract_tables_from_pdf(pdf_path)
        if tables:
            output_parts.append("\n=== TABLES (best-effort extraction) ===")
            for i, table in enumerate(tables[:5]):  # Limit to first 5 tables
                output_parts.append(f"\nTable {i+1} (Page {table['page']}):")
                for row in table['rows'][:20]:  # Limit rows
                    output_parts.append(str(row))
    
    return "\n".join(output_parts)


# Convenience function for batch processing
def process_pdf_folder(folder_path: str) -> Dict[str, str]:
    """
    Process all PDFs in a folder
    
    Returns:
        Dictionary mapping filename to extracted content
    """
    folder = Path(folder_path)
    results = {}
    
    for pdf_file in folder.glob("*.pdf"):
        try:
            content = prepare_paper_for_extraction(str(pdf_file))
            results[pdf_file.name] = content
        except Exception as e:
            results[pdf_file.name] = f"ERROR: {str(e)}"
    
    return results


if __name__ == "__main__":
    # Test with a sample PDF
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"Processing: {pdf_path}")
        
        metadata = get_pdf_metadata(pdf_path)
        print(f"\nMetadata: {metadata}")
        
        content = prepare_paper_for_extraction(pdf_path)
        print(f"\nExtracted content ({len(content)} chars):")
        print(content[:2000] + "..." if len(content) > 2000 else content)
    else:
        print("Usage: python pdf_utils.py <pdf_path>")
