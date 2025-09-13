from django.shortcuts import render
from django.http import HttpResponse
from ..models import prameter_info, system_Info, equipmentInfo,system_short_Info
import os
import fitz  # PyMuPDF
import re
from datetime import datetime
from rapidfuzz import fuzz
import pandas as pd
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PDF_FOLDER = os.path.join(settings.MEDIA_ROOT, 'pdfs')
PDF_FOLDER_MARKED = os.path.join(settings.MEDIA_ROOT, 'marked_pdf')
FUZZY_THRESHOLD = 80

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip().lower()

def search_and_highlight(pdf_path, keywords, prefix, timestamp, system_short_name, equipment_name):
    doc = fitz.open(pdf_path)
    highlighted_results = {}
    not_found = []

    for kw in keywords:
        found = False
        for page in doc:
            text = page.get_text("text")
            normalized_text = normalize(text)

            if kw in normalized_text or fuzz.ratio(kw, normalized_text) >= FUZZY_THRESHOLD:
                matches = page.search_for(kw)
                for rect in matches:
                    # Define dot size
                    dot_size = 5  # Adjust for visibility

                    # Calculate position for the dot (slightly to the right of the match)
                    dot_x = rect.x1 + 2
                    dot_y = rect.y0 + (rect.y1 - rect.y0) / 2  # Vertically centered

                    dot_rect = fitz.Rect(dot_x, dot_y, dot_x + dot_size, dot_y + dot_size)

                    # Add a red filled circle annotation
                    dot_annot = page.add_circle_annot(dot_rect)
                    dot_annot.set_colors(stroke=(1, 0, 0), fill=(1, 0, 0))  # Red color
                    dot_annot.set_border(width=0.5)
                    dot_annot.update()

                found = True
                highlighted_results.setdefault(kw, []).append(text)

        if not found:
            not_found.append(kw)

    marked_filename = f"{system_short_name}_{equipment_name}_{prefix}_marked_{timestamp}.pdf"
    marked_path = os.path.join(PDF_FOLDER_MARKED, marked_filename)
    doc.save(marked_path)
    doc.close()

    return {
        'pdfs_scanned': 1,
        'keywords_entered': len(keywords),
        'keywords_matched': len(highlighted_results),
        'keywords_not_found': len(not_found),
        'duplicate_keywords': len([kw for kw in keywords if keywords.count(kw) > 1]),
        'found_summary': highlighted_results,
        'not_found_keywords': not_found,
        'marked_pdf': marked_filename
    }


def parameter_analysis_view(request):
    systems = system_Info.objects.all()
    equipments = equipmentInfo.objects.all()
    context = {'systems': systems, 'equipments': equipments}

    if request.method == 'POST' and 'analyze' in request.POST:
        system_id = request.POST.get('system')
        equipment_id = request.POST.get('equipment')

        parameters = prameter_info.objects.select_related('p_definition').filter(
            p_system_id=system_id,
            p_equipment_name_id=equipment_id
        )

        # Get the system object
        system_obj = system_Info.objects.get(id=system_id)

        # Get the short name from system_short_Info
        system_short_obj = system_short_Info.objects.filter(ss_system_name=system_obj).first()
        system_short_name = system_short_obj.ss_system_short_name if system_short_obj else 'N/A'

        # Get the equipment object
        equipment_obj = equipmentInfo.objects.get(id=equipment_id)
        equipment_name = equipment_obj.equipment_name

        # Clean up old files for this system + equipment
        delete_old_files(system_short_name, equipment_name)

        as_is_pdf = request.FILES.get('as_is_pdf')
        to_be_pdf = request.FILES.get('to_be_pdf')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if as_is_pdf:
            as_is_path = os.path.join(PDF_FOLDER, f"{system_short_name}_{equipment_name}_as_is_{timestamp}.pdf")
            with open(as_is_path, 'wb+') as f:
                for chunk in as_is_pdf.chunks():
                    f.write(chunk)

        if to_be_pdf:
            to_be_path = os.path.join(PDF_FOLDER, f"{system_short_name}_{equipment_name}_to_be_{timestamp}.pdf")
            with open(to_be_path, 'wb+') as f:
                for chunk in to_be_pdf.chunks():
                    f.write(chunk)

        # Normalize keywords
        as_is_keywords = [normalize(p.p_name_as_is) for p in parameters if p.p_name_as_is]
        to_be_keywords = [normalize(p.p_parameter_name_combo) for p in parameters if p.p_parameter_name_combo]

        # Identify duplicates
        def get_duplicates(keyword_list):
            return list(set([kw for kw in keyword_list if keyword_list.count(kw) > 1]))

        as_is_duplicates = get_duplicates(as_is_keywords)
        to_be_duplicates = get_duplicates(to_be_keywords)

        # Run analysis
        if as_is_pdf:
            as_is_result = search_and_highlight(as_is_path, as_is_keywords, 'as_is', timestamp,system_short_name,equipment_name)
            as_is_result['duplicate_keywords_list'] = as_is_duplicates
            context['as_is_results'] = as_is_result

        if to_be_pdf:
            to_be_result = search_and_highlight(to_be_path, to_be_keywords, 'to_be', timestamp,system_short_name,equipment_name)
            to_be_result['duplicate_keywords_list'] = to_be_duplicates
            context['to_be_results'] = to_be_result

        # TF-IDF Similarity Calculation
        param_texts = [p.p_name for p in parameters]
        def_texts = [p.p_definition.pd_name for p in parameters]

        df = pd.DataFrame({
            'parameter': param_texts,
            'parameter_definition': def_texts
        })

        vectorizer = TfidfVectorizer().fit(df['parameter'] + df['parameter_definition'])
        param_vectors = vectorizer.transform(df['parameter'])
        def_vectors = vectorizer.transform(df['parameter_definition'])

        similarity_scores = cosine_similarity(param_vectors, def_vectors).diagonal()
        df['matching_score'] = similarity_scores

        context['similarity_scores'] = df.to_dict(orient='records')

        context['as_is_pdf_files'] = [
            f for f in os.listdir(PDF_FOLDER_MARKED)
            if f.endswith('.pdf') and 'as_is' in f.lower()
        ]
        context['to_be_pdf_files'] = [
            f for f in os.listdir(PDF_FOLDER_MARKED)
            if f.endswith('.pdf') and 'to_be' in f.lower()
        ]

    return render(request, 'epe_app/parameter_analysis.html', context)


def delete_old_files(system_short_name, equipment_name):
    prefix = f"{system_short_name}_{equipment_name}_"

    # Delete old uploaded PDFs
    for f in os.listdir(PDF_FOLDER):
        if f.startswith(prefix) and f.endswith('.pdf'):
            try:
                os.remove(os.path.join(PDF_FOLDER, f))
            except Exception as e:
                print(f"Error deleting {f}: {e}")

    # Delete old marked PDFs
    for f in os.listdir(PDF_FOLDER_MARKED):
        if f.startswith(prefix) and f.endswith('.pdf'):
            try:
                os.remove(os.path.join(PDF_FOLDER_MARKED, f))
            except Exception as e:
                print(f"Error deleting {f}: {e}")


