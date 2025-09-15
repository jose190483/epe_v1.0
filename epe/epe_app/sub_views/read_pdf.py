import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from PyPDF2 import PdfReader
from ..models import PDFChunks
from .utils import semantic_search

@login_required(login_url='login_page')
def upload_pdf(request):
    if request.method == 'POST' and 'pdf_file' in request.FILES:
        pdf_file = request.FILES['pdf_file']
        file_name = pdf_file.name

        # Check for duplicate file name
        if PDFChunks.objects.filter(file_name=file_name).exists():
            return JsonResponse({'success': False, 'error': 'A PDF with this name already exists.'})

        try:
            # Read and chunk the PDF content
            reader = PdfReader(pdf_file)
            chunks = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    chunks.append(text)

            # Save chunks to the database
            PDFChunks.objects.create(file_name=file_name, chunks=chunks)

            return JsonResponse({'success': True, 'message': 'PDF uploaded and processed successfully.'})
        except Exception as e:
            print("Error processing PDF:", e)
            return JsonResponse({'success': False, 'error': 'An error occurred while processing the PDF.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required(login_url='login_page')
def read_pdf(request):
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

            # Flatten all chunks from the database
            pdf_chunks_qs = PDFChunks.objects.all().values_list('chunks', flat=True)
            all_chunks = []
            for chunk_list in pdf_chunks_qs:
                if isinstance(chunk_list, list):
                    all_chunks.extend(chunk_list)

            # Perform semantic search
            response_text = semantic_search(all_chunks, prompt)

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
            print("Error during search:", e)
            return JsonResponse({'success': False, 'error': 'An error occurred during processing.'})

    # Handle GET requests
    return render(request, 'epe_app/read_pdf.html', {
        'response_text': response_text,
        'chat_history': chat_history
    })