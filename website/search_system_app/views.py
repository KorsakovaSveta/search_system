from django.shortcuts import render, redirect
from .models import Documents, Keywords
from .forms import LinkForm
import requests
import PyPDF2
from django.db.models import Q
import nltk
nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
# Create your views here.
import os
from django.core.cache import cache
def add_link(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            form.save()
            doc_id = Documents.objects.get(link=form.cleaned_data['link'])
            process_link(doc_id.doc_id)
            return render(request, 'add_links.html', {'form': form})
    else:
        form = LinkForm()
    return render(request, 'add_links.html', {'form': form})

def process_link(doc_id):
    pdf_doc = Documents.objects.get(pk=doc_id)

     # Проверить наличие текста в кэше
    cached_text = cache.get(f'document_text_{doc_id}')
    if cached_text:
        return cached_text

    response = requests.get(pdf_doc.link)

    with open("downloaded_pdf.pdf", "wb") as pdf_file:
        pdf_file.write(response.content)

    text = ""
    with open("downloaded_pdf.pdf", "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    cache.set(f'document_text_{doc_id}', text)

    # Удаление временного PDF-файла
    os.remove('downloaded_pdf.pdf')

    return text

def search_results(request):
    query = request.GET.get('query')
    lemmatizer = WordNetLemmatizer()
    documents_links = []
    if query:
        search_words = query.split()
        processed_documents = {}
        for document in Documents.objects.all():
            processed_documents[document.doc_id] = process_link(document.doc_id)
        
        for doc_id, text in processed_documents.items():
            document_words = word_tokenize(text)
            lemmatized_words = [lemmatizer.lemmatize(word.lower()) for word in document_words]
            lemmatized_search_words = [lemmatizer.lemmatize(word.lower()) for word in search_words]
            if all(word in lemmatized_words for word in lemmatized_search_words):
                documents_links.append(Documents.objects.get(doc_id=doc_id).link)
    
    return render(request, 'search_results.html', {'documents_links': documents_links})
