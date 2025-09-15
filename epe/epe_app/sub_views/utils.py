import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

# Load the local model once
model = SentenceTransformer(
    r'C:\Users\waltjos01\PycharmProjects\epe_v2.0\epe\epe_app\models\all-MiniLM-L6-v2-main'
)

def extract_text_chunks(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    chunks = []
    for page in doc:
        text = page.get_text()
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        chunks.extend(paragraphs)
    return chunks

def semantic_search(chunks, prompt, top_k=3):
    # Encode all chunks and the prompt
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)

    # Compute cosine similarity
    scores = util.cos_sim(prompt_embedding, chunk_embeddings)[0]
    top_results = scores.topk(k=top_k)

    # Return top matching chunks
    matched_chunks = [chunks[idx] for idx in top_results.indices]
    return "\n\n".join(matched_chunks)
