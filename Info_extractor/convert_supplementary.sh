#!/bin/bash
# Batch convert DOCX to PDF and TIF to PNG for Gemini API compatibility

PAPERS_DIR="/Users/boxx/Desktop/Dev/RMSC/Papers"

echo "=== DOCX to PDF Conversion ==="
find "$PAPERS_DIR" -name "*.docx" -type f | while read docx_file; do
    pdf_file="${docx_file%.docx}.pdf"
    if [ ! -f "$pdf_file" ]; then
        echo "Converting: $(basename "$docx_file")"
        soffice --headless --convert-to pdf --outdir "$(dirname "$docx_file")" "$docx_file"
    else
        echo "Skipping (already exists): $(basename "$pdf_file")"
    fi
done

echo ""
echo "=== TIF to PNG Conversion ==="
find "$PAPERS_DIR" -name "*.tif" -o -name "*.tiff" -type f | while read tif_file; do
    png_file="${tif_file%.*}.png"
    if [ ! -f "$png_file" ]; then
        echo "Converting: $(basename "$tif_file")"
        sips -s format png "$tif_file" --out "$png_file"
    else
        echo "Skipping (already exists): $(basename "$png_file")"
    fi
done

echo ""
echo "=== Conversion Complete ==="
