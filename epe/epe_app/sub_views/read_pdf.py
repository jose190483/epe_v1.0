import hashlib
import time
import traceback
import fitz  # PyMuPDF
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import fitz  # PyMuPDF
from django.views.decorators.http import require_POST
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from django.http import JsonResponse
import requests, json
from ..models import PDFChunks
from django.http import JsonResponse, request
from django.views.decorators.http import require_http_methods
from transformers import AutoModelForCausalLM,AutoTokenizer
import torch
from .rag_models import MODEL, TOKENIZER
# your embedding model already loaded somewhere above:
model = SentenceTransformer(r"C:\Users\waltjos01\PycharmProjects\epe_v2.0\epe\epe_app\models\all-MiniLM-L6-v2-main")
model = SentenceTransformer(r"C:\Users\BVM\PycharmProjects\epe_v_3.0\epe\epe_app\models\all_MiniLM_L6_v2_main")

EMBEDDER = SentenceTransformer(r"C:\Users\BVM\PycharmProjects\epe_v_3.0\epe\epe_app\models\all_MiniLM_L6_v2_main")

def get_embedding(text: str) -> list[float]:
    """Return L2-normalized embedding as a JSON-safe list[float]."""
    emb = EMBEDDER.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return emb.astype(np.float32).tolist()

def chunk_text_by_sentences(text, max_words=250):
    import re
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
    import re
    return re.sub(r'\s+', ' ', text).strip()

@login_required(login_url='login_page')
@require_POST
def upload_pdf(request):
    """
    Upload and process a PDF:
    - compute SHA-256 hash
    - skip if same content already processed
    - extract text -> chunk
    - embed chunks
    - store in PDFChunks
    """
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file uploaded.'}, status=400)

    pdf_file = request.FILES['pdf_file']
    file_name = pdf_file.name

    try:
        # read file once and compute hash
        stream_bytes = pdf_file.read()
        if not stream_bytes:
            return JsonResponse({'success': False, 'error': 'Empty file.'}, status=400)

        file_hash = hashlib.sha256(stream_bytes).hexdigest()

        # idempotency: skip if same hash already in DB
        existing = PDFChunks.objects.filter(file_hash=file_hash).first()
        if existing:
            return JsonResponse({'success': True, 'message': 'This PDF is already processed.', 'file_name': existing.file_name})

        # open PDF with PyMuPDF
        try:
            doc = fitz.open(stream=stream_bytes, filetype="pdf")
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Cannot open PDF: {e}'}, status=400)

        if doc.needs_pass:
            doc.close()
            return JsonResponse({'success': False, 'error': 'This PDF is password protected.'}, status=400)

        chunks = []
        for page in doc:
            text = page.get_text("text") or page.get_text() or ""
            text = clean_text(text)
            if text:
                chunks.extend(chunk_text_by_sentences(text, max_words=50))
        doc.close()

        # clean + filter short chunks
        chunks = [clean_text(c) for c in chunks if len(c.split()) >= 8]
        if not chunks:
            return JsonResponse({'success': False, 'error': 'No extractable text found. (Scanned PDF?)'}, status=400)

        # batch embed chunks and convert to JSON-safe lists
        emb_matrix = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
        embeddings = emb_matrix.astype('float32').tolist()

        # store in DB
        PDFChunks.objects.create(
            file_name=file_name,
            file_hash=file_hash,
            chunks=chunks,
            embeddings=embeddings,
            num_chunks=len(chunks),
            dim=len(embeddings[0]) if embeddings else 384
        )

        return JsonResponse({'success': True, 'message': 'PDF uploaded and processed successfully.'})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': f'Processing error: {e}'}, status=500)

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
            # ollama_url = "http://localhost:11434/api/generate"
            ollama_url = ""

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

            # try:
            #     answer = mistral_generate(
            #         f"Context:\n{context}\n\nQuestion: {prompt}",
            #         max_new_tokens=512,
            #         temperature=0.2
            #     )
            #     if not answer:
            #         answer = "Sorry, I couldn’t find that in the document."
            # except Exception as e:
            #     answer = f"Error running Mistral: {e}"

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
# @require_http_methods(["POST"])
# def ask_local_rag(request):
#     prompt = (request.POST.get("prompt") or request.body.decode("utf-8") or "").strip()
#     if not prompt:
#         return JsonResponse({"error": "Empty prompt"}, status=400)
#
#     try:
#         answer = ollama_generate(
#             model="llama3:8b",  # pick the exact tag you have (e.g., llama3, llama3.1, llama3:8b, etc.)
#             prompt=prompt,
#             stream=False,
#             temperature=0.3,
#             num_predict=256
#         )
#         if not answer:
#             answer = "Sorry, I couldn’t generate a response."
#         return JsonResponse({"answer": answer})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
#
#

def ollama_generate(model: str, prompt: str, *, stream: bool = False, **opts) -> str:
    """
    Call Ollama /api/generate. If stream=True, it stitches together all chunks.
    Example opts: temperature=0.2, num_predict=256
    """
    # url = "http://localhost:11434/api/generate"
    url = ""
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

MISTRAL_PATH = r"C:\Users\BVM\PycharmProjects\epe_v_3.0\epe\epe_app\models\Mistral_7B_Instruct_v0.3"  # your local dir
MISTRAL_TOKENIZER = AutoTokenizer.from_pretrained(MISTRAL_PATH)

# Use fp16 only if you have a GPU that supports it; otherwise use float32
MISTRAL_MODEL = AutoModelForCausalLM.from_pretrained(
    MISTRAL_PATH,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)

def mistral_generate(prompt: str, *, max_new_tokens=64, temperature=0.2) -> str:
    """
    Fast path for local inference.
    - If no CUDA, use Ollama (quantized) for speed.
    - Keeps tokens small and greedy to return quickly.
    """
    if not torch.cuda.is_available():
        # fallback so you aren't waiting minutes on CPU
        return ollama_generate(
            model="mistral:7b-instruct",   # or your local Ollama tag
            prompt=prompt,
            stream=False,
            temperature=temperature,
            num_predict=max_new_tokens,
        )

    inputs = TOKENIZER(prompt, return_tensors="pt", padding=True).to(MODEL.device)
    with torch.inference_mode():
        out_ids = MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=False,              # greedy is faster/stable
            pad_token_id=TOKENIZER.eos_token_id,
        )
    return TOKENIZER.decode(out_ids[0], skip_special_tokens=True)



# In `read_pdf.py`
@require_http_methods(["POST"])
def clear_chat_history(request):
    request.session['chat_history'] = []
    return JsonResponse({'success': True, 'message': 'Chat history cleared.'})


def compare_prompt_with_pdf(request):
    """
    Compare a chunked prompt with chunked PDF content stored in the database.
    """
    if request.method == 'POST':
        try:
            # Extract the prompt and optional parameters from the request
            prompt = request.POST.get('prompt', '').strip()
            max_words = int(request.POST.get('max_words', 250))  # Default max words per chunk
            top_n = int(request.POST.get('top_n', 3))  # Default number of top matches to return
            print("Received prompt for comparison:", prompt)

            # Validate the prompt
            if not prompt:
                return render(request, 'epe_app/read_pdf.html', {
                    'response_text': 'Empty prompt provided.',
                    'chat_history': []
                })

            if max_words <= 0 or top_n <= 0:
                return render(request, 'epe_app/read_pdf.html', {
                    'response_text': 'Invalid parameters: max_words and top_n must be positive integers.',
                    'chat_history': []
                })

            # Step 1: Chunk the prompt into smaller pieces
            prompt_chunks = chunk_text_by_sentences(prompt, max_words=max_words)

            # Step 2: Retrieve PDF chunks and embeddings from the database
            pdf_chunks = PDFChunks.objects.all()
            if not pdf_chunks.exists():
                return render(request, 'epe_app/read_pdf.html', {
                    'response_text': 'No PDF content found in the database.',
                    'chat_history': []
                })

            all_chunks = []
            all_embeddings = []
            chunk_to_file_map = []  # Map chunks to their file names
            for pdf_chunk in pdf_chunks:
                all_chunks.extend(pdf_chunk.chunks)
                chunk_to_file_map.extend([pdf_chunk.file_name] * len(pdf_chunk.chunks))
                for emb in pdf_chunk.embeddings:
                    all_embeddings.append(np.array(emb, dtype=np.float32))

            # Step 3: Generate embeddings for the prompt chunks
            prompt_embeddings = np.array([get_embedding(chunk) for chunk in prompt_chunks], dtype=np.float32)

            # Step 4: Compute cosine similarity between prompt embeddings and PDF embeddings
            similarities = cosine_similarity(prompt_embeddings, np.vstack(all_embeddings))
            print("Computed similarities shape:", similarities.shape)

            # Step 5: Aggregate results and find top matches for each prompt chunk
            top_matches = []
            for i, chunk in enumerate(prompt_chunks):
                chunk_similarities = similarities[i]
                top_indices = chunk_similarities.argsort()[-top_n:][::-1]  # Get indices of top N matches
                top_matches.append({
                    'prompt_chunk': chunk,
                    'matches': [
                        {
                            'pdf_chunk': all_chunks[idx],
                            'similarity': float(chunk_similarities[idx]),
                            'file_name': chunk_to_file_map[idx]
                        }
                        for idx in top_indices
                    ]
                })
            print("Top matches found:", top_matches)

            # Render the results in the template
            return render(request, 'epe_app/read_pdf_new.html', {
                'response_text': 'Comparison completed successfully.',
                'chat_history': top_matches
            })

        except Exception as e:
            # Log the error for debugging
            import traceback
            traceback.print_exc()
            return render(request, 'epe_app/read_pdf_new.html', {
                'response_text': f'An unexpected error occurred: {str(e)}',
                'chat_history': []
            })

    # Handle GET requests or other methods
    return render(request, 'epe_app/read_pdf_new.html', {
        'response_text': '',
        'chat_history': []
    })
