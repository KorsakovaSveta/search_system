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
    #   # Запись текста в текстовый файл
    # with open(f'document_content_{doc_id}.txt', 'w', encoding='utf-8') as txt_file:
    #     txt_file.write(text)

    # Удаление временного PDF-файла
   
    os.remove('downloaded_pdf.pdf')
    return text

def search_results(request):
    query = request.GET.get('query')
    lemmatizer = WordNetLemmatizer()
    documents_links = []
    if query:
        search_words = query.split()
        documents = Documents.objects.all()
        for document in documents:
            text = process_link(document.doc_id)
            document_words = word_tokenize(text)
            lemmatized_words = [lemmatizer.lemmatize(word.lower()) for word in document_words]
            lemmatized_search_words = [lemmatizer.lemmatize(word.lower()) for word in search_words]
            if all(word in lemmatized_words for word in lemmatized_search_words):
                documents_links.append(document.link)
    
    return render(request, 'search_results.html', {'documents_links': documents_links})
