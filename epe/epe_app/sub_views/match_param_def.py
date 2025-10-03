from django.shortcuts import render
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from ..models import prameter_info

def parameter_similarity_view(request):
    # Fetch all records with related definitions
    records = prameter_info.objects.select_related('p_definition').all()

    # Prepare docs
    data = {
        "parameter_definition": [record.p_definition.pd_name for record in records],
        "parameter": [record.p_name for record in records]
    }

    df = pd.DataFrame(data)

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer().fit(df["parameter_definition"] + df["parameter"])
    definition_vectors = vectorizer.transform(df["parameter_definition"])
    parameter_vectors = vectorizer.transform(df["parameter"])

    # Cosine similarity
    similarity_scores = cosine_similarity(definition_vectors, parameter_vectors).diagonal()
    df["matching_score"] = similarity_scores

    # Convert to list of dictionaries for template rendering
    records_with_scores = df.to_dict(orient='records')

    return render(request, 'epe_app/parameter_similarity_list.html', {'records': records_with_scores})
