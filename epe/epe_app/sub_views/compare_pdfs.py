import fitz
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

import pymupdf as fitz  # PyMuPDF
import os
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def compare_pdfs_and_highlight(source_pdf_path, compare_pdf_path, threshold=0.75):
    # Load both PDFs
    source_doc = fitz.open(source_pdf_path)
    compare_doc = fitz.open(compare_pdf_path)

    # Extract and normalize lines from source PDF
    source_lines = []
    for page in source_doc:
        source_lines.extend(page.get_text("text").splitlines())
    source_lines = [line.strip().lower() for line in source_lines if line.strip()]

    # Highlight matching lines in compare PDF using fuzzy matching
    for page in compare_doc:
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            if 'lines' in b:
                for line in b['lines']:
                    line_text = " ".join([span['text'] for span in line['spans']]).strip().lower()
                    if any(similar(line_text, source_line) >= threshold for source_line in source_lines):
                        for span in line['spans']:
                            rect = fitz.Rect(span['bbox'])
                            highlight = page.add_highlight_annot(rect)
                            highlight.set_colors(stroke=(0, 1, 0))  # Green color for matched
                            highlight.update()

    # Save the highlighted PDF
    output_path = os.path.splitext(compare_pdf_path)[0] + "_highlighted.pdf"
    compare_doc.save(output_path)
    compare_doc.close()
    source_doc.close()

    return output_path

print("Function updated to use line-by-line comparison with 75% fuzzy matching threshold.")


def pdf_compare_view(request):
    if request.method == 'POST' and request.FILES.get('source_pdf') and request.FILES.get('compare_pdf'):
        source_pdf = request.FILES['source_pdf']
        compare_pdf = request.FILES['compare_pdf']

        fs = FileSystemStorage()
        source_path = fs.save(source_pdf.name, source_pdf)
        compare_path = fs.save(compare_pdf.name, compare_pdf)

        output_path = compare_pdfs_and_highlight(fs.path(source_path), fs.path(compare_path))

        with open(output_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="highlighted_comparison.pdf"'
            return response

    return render(request, 'epe_app/pdf_compare.html')





