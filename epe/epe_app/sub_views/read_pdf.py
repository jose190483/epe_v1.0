import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from PyPDF2 import PdfReader
from ..models import PDFChunks
from .utils import semantic_search, model  # Reuse the globally loaded model

@login_required(login_url='login_page')
def upload_pdf(request):
    # Update embeddings for existing rows
    for pdf_chunk in PDFChunks.objects.all():
        if not pdf_chunk.embeddings:  # Only update if embeddings are empty
            embeddings = [model.encode(chunk, convert_to_tensor=False).tolist() for chunk in pdf_chunk.chunks]
            pdf_chunk.embeddings = embeddings
            pdf_chunk.save()

    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']
        file_name = pdf_file.name

        if PDFChunks.objects.filter(file_name=file_name).exists():
            return JsonResponse({'success': False, 'error': 'A PDF with this name already exists.'})

        try:
            reader = PdfReader(pdf_file)
            chunks = []
            embeddings = []
            max_chunk_size = 800  # Maximum words per chunk
            overlap = 100  # Overlap between chunks

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    # Split text into paragraphs
                    paragraphs = text.split('\n\n')
                    for paragraph in paragraphs:
                        words = paragraph.split()
                        current_chunk = []
                        current_chunk_size = 0

                        for word in words:
                            if current_chunk_size + 1 > max_chunk_size:
                                # Add the current chunk to the list
                                chunks.append(' '.join(current_chunk))
                                # Start a new chunk with overlap
                                current_chunk = current_chunk[-overlap:] if overlap else []
                                current_chunk_size = len(current_chunk)

                            current_chunk.append(word)
                            current_chunk_size += 1

                        # Add the last chunk if it exists
                        if current_chunk:
                            chunks.append(' '.join(current_chunk))

            # Precompute embeddings for all chunks
            embeddings = [model.encode(chunk, convert_to_tensor=False).tolist() for chunk in chunks]

            # Save chunks and embeddings to the database
            PDFChunks.objects.create(file_name=file_name, chunks=chunks, embeddings=embeddings)

            return JsonResponse({'success': True, 'message': 'PDF uploaded and processed successfully.'})
        except Exception as e:
            print("Error processing PDF:", e)
            return JsonResponse({'success': False, 'error': 'An error occurred while processing the PDF.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

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

            # Retrieve all stored chunks and embeddings from the database
            pdf_chunks = PDFChunks.objects.all()
            if not pdf_chunks.exists():
                return JsonResponse({'success': False, 'error': 'No PDF data found in the database.'})

            # Combine chunks and embeddings from all PDFs
            all_chunks = []
            all_embeddings = []
            for pdf_chunk in pdf_chunks:
                all_chunks.extend(pdf_chunk.chunks)
                all_embeddings.extend(pdf_chunk.embeddings)
            print("chunks:", all_chunks)
            # Perform semantic search
            response_text = semantic_search(all_embeddings, prompt, all_chunks)

            # Update chat history
            chat_entry = {
                'prompt': prompt,
                'response': response_text,
            }
            chat_history.append(chat_entry)
            request.session['chat_history'] = chat_history

            return JsonResponse({'success': True, 'prompt': prompt, 'response': response_text})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'})
        except Exception as e:
            import traceback
            print("Error during search:", e)
            print(traceback.format_exc())  # Print the full stack trace for debugging
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})

    # Handle GET requests
    return render(request, 'epe_app/read_pdf.html', {
        'response_text': response_text,
        'chat_history': chat_history
    })