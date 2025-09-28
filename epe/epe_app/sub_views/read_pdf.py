import json
import re
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ..models import PDFChunks
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def chunk_text_by_sentences(text, max_words=250):
    # Split text into sentences and group into chunks
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, chunk = [], []
    word_count = 0
    for sentence in sentences:
        words = sentence.split()
        if word_count + len(words) > max_words and chunk:
            chunks.append(' '.join(chunk))
            chunk, word_count = [], 0
        chunk.append(sentence)
        word_count += len(words)
    if chunk:
        chunks.append(' '.join(chunk))
    return chunks

def clean_text(text):
    # Remove extra whitespace and non-printable characters
    return re.sub(r'\s+', ' ', text).strip()


# Load the model from your local path
model = SentenceTransformer('C:/Users/BVM/PycharmProjects/epe_v_3.0/epe/epe_app/models/all-MiniLM-L6-v2-main')

# good: returns a plain list
def get_embedding(text: str):
    return model.encode(text, convert_to_numpy=True, normalize_embeddings=True).tolist()


@login_required(login_url='login_page')
def upload_pdf(request):
    if request.method != 'POST' or 'pdf_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

    pdf_file = request.FILES['pdf_file']
    file_name = pdf_file.name

    if PDFChunks.objects.filter(file_name=file_name).exists():
        return JsonResponse({'success': False, 'error': 'A PDF with this name already exists.'})

    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        chunks = []
        for page in doc:
            text = page.get_text()
            if text:
                chunks.extend(chunk_text_by_sentences(text, max_words=500))

        chunks = [clean_text(c) for c in chunks if len(c.split()) >= 8]
        if not chunks:
            return JsonResponse({'success': False, 'error': 'No extractable text found.'})

        # Generate embeddings for each chunk
        embeddings = [get_embedding(chunk) for chunk in chunks]

        PDFChunks.objects.create(
            file_name=file_name,
            chunks=chunks,
            embeddings=embeddings,
            num_chunks=len(chunks),
            dim=len(embeddings[0]) if embeddings else 384
        )
        return JsonResponse({'success': True, 'message': 'PDF uploaded and processed successfully.'})

    except Exception as e:
        print("Error processing PDF:", e)
        return JsonResponse({'success': False, 'error': 'An error occurred while processing the PDF.'})

@login_required(login_url='login_page')
def read_pdf(request):
    print("Accessing read_pdf view")
    response_text = ""
    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        if request.content_type != 'application/json':
            return JsonResponse({'success': False, 'error': 'Invalid content type. Expected JSON.'})

        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()
            if not prompt:
                return JsonResponse({'success': False, 'error': 'Prompt is missing.'})

            pdf_chunks = PDFChunks.objects.all()
            if not pdf_chunks.exists():
                return JsonResponse({'success': False, 'error': 'No PDF docs found in the database.'})

            all_chunks = []
            all_embeddings = []
            for pdf_chunk in pdf_chunks:
                all_chunks.extend(pdf_chunk.chunks)
                # ensure each embedding is a numpy array of same length
                for emb in pdf_chunk.embeddings:
                    all_embeddings.append(np.array(emb, dtype=np.float32))

            # Now stack them properly
            all_embeddings = np.vstack(all_embeddings)  # shape: (N, D)

            # Generate embedding for the prompt (normalize if you like)
            prompt_embedding = np.array(get_embedding(prompt), dtype=np.float32).reshape(1, -1)

            # Compute cosine similarity
            # similarities = cosine_similarity(prompt_embedding, all_embeddings).flatten()

            similarities = (all_embeddings @ prompt_embedding.T).ravel()

            # Get top 3 most similar chunks
            top_indices = similarities.argsort()[-3:][::-1]
            response_chunks = [all_chunks[i] for i in top_indices]

            context = "\n".join(response_chunks)
            ollama_url = "http://localhost:11434/api/generate"

            payload = {
                "model": "gemma3:4b",
                "prompt": f"Context:\n{context}\n\nQuestion: {prompt}"
            }
            try:
                answer = ollama_generate(
                    model="gemma3:4b",  # ensure this tag exists locally
                    prompt=f"Context:\n{context}\n\nQuestion: {prompt}",
                    stream=False,  # <—— key change
                    temperature=0.2,
                    num_predict=512
                )
                if not answer:
                    answer = "Sorry, I couldn’t find that in the document."

                chat_entry = {'prompt': prompt, 'response': answer}
                chat_history.append(chat_entry)
                request.session['chat_history'] = chat_history
                return JsonResponse({'success': True, 'prompt': prompt, 'response': answer})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON docs.'})
        except Exception as e:
            import traceback
            print("Error during search:", e)
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    # GET
    return render(request, 'epe_app/read_pdf.html', {
        'response_text': response_text,
        'chat_history': chat_history
    })
@require_http_methods(["POST"])
def ask_local_rag(request):
    prompt = (request.POST.get("prompt") or request.body.decode("utf-8") or "").strip()
    if not prompt:
        return JsonResponse({"error": "Empty prompt"}, status=400)

    try:
        answer = ollama_generate(
            model="llama3:8b",  # pick the exact tag you have (e.g., llama3, llama3.1, llama3:8b, etc.)
            prompt=prompt,
            stream=False,
            temperature=0.3,
            num_predict=256
        )
        if not answer:
            answer = "Sorry, I couldn’t generate a response."
        return JsonResponse({"answer": answer})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


import requests, json

def ollama_generate(model: str, prompt: str, *, stream: bool = False, **opts) -> str:
    """
    Call Ollama /api/generate. If stream=True, it stitches together all chunks.
    Example opts: temperature=0.2, num_predict=256
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": stream}
    if opts:
        payload.update(opts)

    if not stream:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "").strip()

    # stream=True: concatenate all 'response' chunks
    r = requests.post(url, json=payload, stream=True, timeout=120)
    r.raise_for_status()
    out = []
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        try:
            piece = json.loads(line)
            out.append(piece.get("response", ""))
        except json.JSONDecodeError:
            # ignore partial lines
            continue
    return "".join(out).strip()
