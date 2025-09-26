
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer


# Load the local model once
model = SentenceTransformer(
    r'C:\Users\waltjos01\PycharmProjects\epe_v2.0\epe\epe_app\models\all-MiniLM-L6-v2-main'
)
def extract_text_chunks(pdf_file, max_chunk_size=800):
    import re
    from nltk.tokenize import sent_tokenize

    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    chunks = []

    for page in doc:
        # Extract text from the page
        text = page.get_text()

        # Remove unnecessary whitespace and special characters
        text = re.sub(r'\s+', ' ', text).strip()

        # Split text into sentences
        sentences = sent_tokenize(text)

        # Group sentences into chunks of a maximum size
        current_chunk = []
        current_chunk_size = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_chunk_size + sentence_length > max_chunk_size:
                # Add the current chunk to the list and start a new chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_chunk_size = 0

            current_chunk.append(sentence)
            current_chunk_size += sentence_length

        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(' '.join(current_chunk))

    return chunks


def semantic_search(embeddings, prompt, chunks, top_k=3, similarity_threshold=0.1):
    from sentence_transformers import util
    import torch

    # Encode the prompt
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    print("Prompt Embedding:", prompt_embedding)
    # Convert stored embeddings to tensor
    chunk_embeddings = torch.tensor(embeddings)
    print("Chunk Embeddings Shape:", chunk_embeddings.shape)
    # Compute cosine similarity
    scores = util.cos_sim(prompt_embedding, chunk_embeddings)[0]
    print("Similarity Scores:", scores)
    # Filter results by similarity threshold
    filtered_results = [(idx, score.item()) for idx, score in enumerate(scores) if score >= similarity_threshold]
    print("Filtered Results (Index, Score):", filtered_results)
    # Sort results by score in descending order
    filtered_results = sorted(filtered_results, key=lambda x: x[1], reverse=True)

    # Limit to top-k results
    top_results = filtered_results[:top_k]
    print("Top Results (Index, Score):", top_results)
    # Retrieve the top-matched chunks
    matched_chunks = [chunks[idx] for idx, _ in top_results]
    print("Matched Chunks:", matched_chunks)
    if not matched_chunks:
        matched_chunks = ["No relevant data found."]

    return matched_chunks
