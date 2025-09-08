import os
import re
import fitz  # PyMuPDF
from collections import defaultdict
from django.shortcuts import render
from collections import Counter

PDF_FOLDER = r"C:\Users\waltjos01\PycharmProjects\epe_v2.0\epe\epe_app\pdfs"

def search_keywords(request):
    highlighted_results = defaultdict(list)
    not_found_keywords = []
    message = ''
    keywords = []
    if request.method == 'POST':
        # ✅ Handle clear PDFs
        if request.POST.get('clear_pdfs') == 'true':
            deleted_count = 0
            for filename in os.listdir(PDF_FOLDER):
                if filename.endswith('.pdf'):
                    os.remove(os.path.join(PDF_FOLDER, filename))
                    deleted_count += 1
            return render(request, 'idp_app/search_page.html', {
                'found_summary': {},
                'not_found_keywords': [],
                'message': f"{deleted_count} PDF(s) deleted successfully.",
                'pdf_files': []
            })

        # ✅ Handle PDF upload
        uploaded_files = request.FILES.getlist('pdf_files')
        if uploaded_files:
            for f in uploaded_files:
                with open(os.path.join(PDF_FOLDER, f.name), 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
            message = f"{len(uploaded_files)} file(s) uploaded successfully."

        # ✅ Handle keyword search
        keywords = request.POST.get('keywords', '')
        keywords = [kw.strip().lower() for kw in keywords.split(',') if kw.strip()]
        print('keywords', keywords)
        if keywords:
            print("Searching PDFs...")
            pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
            print('pdf_files', pdf_files)
            for pdf_name in pdf_files:
                pdf_path = os.path.join(PDF_FOLDER, pdf_name)
                doc = fitz.open(pdf_path)
                print('Opened PDF:', pdf_name)
                for page_num, page in enumerate(doc, start=1):

                    # blocks = page.get_text('blocks') or []
                    # text = ' '.join(block[4] for block in blocks if isinstance(block[4], str))
                    # text_normalized = re.sub(r'\s+', ' ', text).lower()
                    #
                    # for kw in keywords:
                    #     if kw in text_normalized:
                    #         pattern = re.compile(re.escape(kw), re.IGNORECASE)
                    #         highlighted_text = pattern.sub(r'<mark>\g<0></mark>', text)
                    #         highlighted_results[kw].append((pdf_name, page_num, highlighted_text))

                    text = page.get_text("text")  # instead of 'blocks'
                    text_normalized = re.sub(r'\s+', ' ', text).lower()
                    print('text_normalized',text_normalized)
                    for kw in keywords:
                        if kw in text_normalized:
                            pattern = re.compile(re.escape(kw), re.IGNORECASE)
                            highlighted_text = pattern.sub(r'<mark>\g<0></mark>', text)
                            highlighted_results[kw].append((pdf_name, page_num, highlighted_text))

            not_found_keywords = [kw for kw in keywords if not highlighted_results[kw]]
    num_pdfs = len([f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')])
    num_keywords = len(keywords)
    num_matched = len([kw for kw in highlighted_results if highlighted_results[kw]])
    unique_keywords = len(set(keywords))
    duplicate_keywords = num_keywords - unique_keywords
    num_not_found = len(not_found_keywords)
    request.session['keywords'] = keywords
    request.session['found_summary'] = dict(highlighted_results)

    duplicate_keywords_list = {k: v for k, v in Counter(keywords).items() if v > 1}
    duplicate_keywords=len(duplicate_keywords_list)
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
        'pdf_files': [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    })


