import os
import re
import fitz  # PyMuPDF
from collections import defaultdict, Counter
from django.conf import settings
from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from rapidfuzz import fuzz

PDF_FOLDER = os.path.join(settings.MEDIA_ROOT, 'pdfs')
PDF_FOLDER_MARKED = os.path.join(settings.MEDIA_ROOT, 'marked_pdf')
FUZZY_THRESHOLD = 80  # 80% match

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip().lower()

def search_keywords(request):
    highlighted_results = defaultdict(list)
    not_found_keywords = []
    message = ''
    keywords = []

    if request.method == 'POST':
        # ✅ Clear marked PDFs
        if request.POST.get('clear_pdfs') == 'true':
            deleted_count = 0
            for filename in os.listdir(PDF_FOLDER_MARKED):
                if filename.endswith('.pdf'):
                    os.remove(os.path.join(PDF_FOLDER_MARKED, filename))
                    deleted_count += 1
            return render(request, 'epe_app/search_page.html', {
                'found_summary': {},
                'not_found_keywords': [],
                'message': f"{deleted_count} PDF(s) deleted successfully.",
                'pdf_files': []
            })

        # ✅ Upload PDFs
        uploaded_files = request.FILES.getlist('pdf_files')
        if uploaded_files:
            for f in uploaded_files:
                with open(os.path.join(PDF_FOLDER, f.name), 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
            message = f"{len(uploaded_files)} file(s) uploaded successfully."

        # ✅ Auto-cleanup old marked PDFs
        for filename in os.listdir(PDF_FOLDER_MARKED):
            if filename.startswith("marked_") and filename.endswith(".pdf"):
                os.remove(os.path.join(PDF_FOLDER_MARKED, filename))

        # ✅ Keyword Search
        keywords = request.POST.get('keywords', '')
        keywords = [normalize(kw) for kw in keywords.split(',') if kw.strip()]
        print('keywords:', keywords)

        if keywords:
            pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
            for pdf_name in pdf_files:
                pdf_path = os.path.join(PDF_FOLDER, pdf_name)
                doc = fitz.open(pdf_path)
                marked = False

                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text("text")
                    lines = text.split('\n')

                    for kw in keywords:
                        for line in lines:
                            line_normalized = normalize(line)

                            # ✅ Hybrid Matching: exact OR fuzzy match
                            if kw in line_normalized or fuzz.ratio(kw, line_normalized) >= FUZZY_THRESHOLD:
                                pattern = re.compile(re.escape(kw), re.IGNORECASE)
                                highlighted_text = pattern.sub(r'<mark>\g<0></mark>', line)
                                highlighted_results[kw].append((pdf_name, page_num, highlighted_text))

                                # ✅ Highlight in PDF
                                matches = page.search_for(kw)
                                for rect in matches:
                                    extended_rect = fitz.Rect(rect.x0 - 2, rect.y0 - 2, rect.x1 + 2, rect.y1 + 2)
                                    highlight = page.add_highlight_annot(extended_rect)
                                    highlight.set_colors(stroke=(0, 1, 1))  # Cyan
                                    highlight.update()
                                    marked = True
                                break

                # ✅ Save marked PDF
                if marked:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    marked_filename = f"marked_{timestamp}_{pdf_name}"
                    marked_path = os.path.join(PDF_FOLDER_MARKED, marked_filename)
                    doc.save(marked_path, garbage=4, deflate=True)
                doc.close()

            not_found_keywords = [kw for kw in keywords if not highlighted_results[kw]]

    # ✅ Stats
    num_pdfs = len([f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')])
    num_keywords = len(keywords)
    num_matched = len([kw for kw in highlighted_results if highlighted_results[kw]])
    unique_keywords = len(set(keywords))
    duplicate_keywords_list = {k: v for k, v in Counter(keywords).items() if v > 1}
    duplicate_keywords = len(duplicate_keywords_list)
    num_not_found = len(not_found_keywords)

    # ✅ Session
    request.session['keywords'] = keywords
    request.session['found_summary'] = dict(highlighted_results)

    return render(request, 'epe_app/search_page.html', {
        'stats': {
            'pdfs_scanned': num_pdfs,
            'keywords_entered': num_keywords,
            'keywords_matched': num_matched,
            'keywords_not_found': num_not_found,
            'duplicate_keywords': duplicate_keywords,
        },
        'duplicate_keywords_list': duplicate_keywords_list,
        'found_summary': dict(highlighted_results),
        'not_found_keywords': not_found_keywords,
        'message': message,
        'pdf_files': [f for f in os.listdir(PDF_FOLDER_MARKED) if f.endswith('.pdf')]
    })

def download_marked_pdf(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'marked_pdf', filename)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
    return HttpResponse("File not found.", status=404)

