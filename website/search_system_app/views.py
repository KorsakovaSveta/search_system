from django.shortcuts import render
from .models import Documents
from .forms import LinkForm
import requests
import PyPDF2
import nltk
nltk.download('punkt_tab')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import math
from nltk.probability import FreqDist
from io import BytesIO
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import io
from google.cloud import translate_v2 as translate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googletrans import Translator
from django.contrib import messages
keyword_cache = {}

def add_link(request):
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            form.save()
            doc = Documents.objects.get(link=form.cleaned_data['link'])
            text = process_link(doc.doc_id)
            doc.text = text
            doc.save()
            messages.success(request, 'The link has been added')
            
    else:
        form = LinkForm()
    return render(request, 'add_links.html', {'form': form})

def calculate_inverse_term_frequency(Pi, N):
    return math.log(N / Pi)

def calculate_term_weight(Q, B):
    return Q * B

def extract_keywords(text, len_processed_documents):
    if text in keyword_cache:
        return keyword_cache[text]
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
 
    lemmatized_words = [lemmatizer.lemmatize(word.lower()) for word in words]
    fdist = FreqDist(lemmatized_words)

    keywords = {}
    
    for word, freq in fdist.items():
        B = calculate_inverse_term_frequency(freq, len_processed_documents)  # Предполагаем, что processed_documents содержит данные о документах
        Q = fdist[word]
        weight = calculate_term_weight(Q, B)
        keywords[word] = weight
        #sorted_keywords = dict(sorted(keywords.items(), key=lambda value: value[1]))

    keyword_cache[text] = keywords
    return keywords

def process_link(doc_id):
    
    pdf_doc = Documents.objects.get(pk=doc_id)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(pdf_doc.link, headers=headers)
    response.raise_for_status()
    pdf_file = BytesIO(response.content)

    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    
    for page in reader.pages:
        text += page.extract_text() 
 
    return text

def search_results(request):
    lemmatizer = WordNetLemmatizer()
    query = request.GET.get('query')
    documents = []
    texts ={}
    a = 0
    if query:
        search_words = query.split()
        new_search_words = [word.lower() for word in search_words]
        processed_documents = {}
       
            
        for doc in Documents.objects.all(): 
            processed_documents[doc.doc_id] = doc.text
            keywords = extract_keywords(doc.text, Documents.objects.count())
            found_all_words = all([lemmatizer.lemmatize(word) in keywords.keys() for word in new_search_words])
            if found_all_words:
                documents.append(Documents.objects.get(doc_id=doc.doc_id))
                texts[doc.doc_id] = doc.text

        request.session['documents_ids'] = [document.doc_id for document in documents]
        request.session['texts'] = texts
        request.session['processed_documents'] = processed_documents
        request.session['search_words'] = search_words
    else:
        return render(request, 'search_results.html', {'documents': documents})
 
    return render(request, 'search_results.html', {'documents': documents, 'search_words': search_words})

def calculate_precision_recall(relevant_docs, retrieved_docs):
    n_relevant = len(relevant_docs)
    n_retrieved = len(retrieved_docs)
    

    # Initialize lists to store precision and recall values
    precision = []
    recall = []
    found_relevant = 0
    
    for i in range(n_retrieved):
        if retrieved_docs[i] in relevant_docs:
            found_relevant += 1
        
        # Calculate precision and recall
        
        current_precision = found_relevant / (i + 1)  # TP / (TP + FP)
        if n_relevant == 0:
            current_recall = 0
        else:
            current_recall = found_relevant / n_relevant   # TP / (TP + FN)
        
        precision.append(current_precision)
        recall.append(current_recall)

    return precision, recall

def calculate_metrics(request):
    relevant_docs, relevant_docs_for_recall ={}, {}
    documents_ids = request.session.get('documents_ids', [])
    documents = [Documents.objects.get(doc_id=document_id) for document_id in documents_ids]
    processed_documents = request.session.get('processed_documents', {})
    texts = request.session.get('texts', {})
    search_words = request.session.get('search_words', [])
    for doc_id, text in processed_documents.items(): 
        if text in texts.values():
            relevant_docs[doc_id] = calculate_relevant(search_words, text)

        else:
            relevant_docs_for_recall[doc_id] = calculate_relevant(search_words, text)
        
    sorted_relevant_docs = dict(sorted(relevant_docs.items(), key=lambda item: min(item[1].values())))

    a = sum(1 for nested_dict in relevant_docs.values() if not any(val < 20 for val in nested_dict.values()))
    pos_rel_docs = [list(relevant_docs.keys()).index(doc_id) + 1 for doc_id, nested_dict in relevant_docs.items() if not any(val < 20 for val in nested_dict.values())]
    c = sum(1 for nested_dict in relevant_docs_for_recall.values() if not any(val < 20 for val in nested_dict.values()))
    if c != 0:
        pos_rel_docs = pos_rel_docs + [list(relevant_docs_for_recall.keys()).index(doc_id) + 1 for doc_id, nested_dict in relevant_docs_for_recall.items() if not any(val < 20 for val in nested_dict.values())]

    d = sum(1 for nested_dict in relevant_docs_for_recall.values() if any(val == 0 for val in nested_dict.values()))
    b = len(sorted_relevant_docs) - a
    if a == 0:
        precision = 0
    else:
        precision = round(a / (a + b), 2)
    if a == 0 and c == 0:  
        recall = 0 
    else:
        recall = round(a / (a + c), 2)
    accuracy = round((a + d) / (a + c + b + d), 2)
    error = round((b + c) / (a+b+c+d), 2)
    if precision == 0 or recall == 0:
        f_measure = 0
    elif precision == recall:
        f_measure = precision
    else:
        f_measure = round(2 / (1 / precision + 1 / recall), 2) 

    
    if a == 0:
        avg_Prec = precision_n = 0 
    else:
        precision_n =  round(a / len(sorted_relevant_docs), 2)
        avg_Prec = round(1 / (a + c) * sum(i / pos_rel_docs[i-1] for i in range(1, len(pos_rel_docs)+1)), 2)

    # Вычисление точности и полноты
    precision_for_chart, recall_for_chart = calculate_precision_recall(pos_rel_docs, list(relevant_docs.keys()))

    # Интерполяция значений точности
    recall_levels = np.arange(0.0, 1.1, 0.1)
    interpolated_precision = []

    for r in recall_levels:
        max_precision = max([p for p, r_val in zip(precision_for_chart, recall_for_chart) if r_val >= r], default=0)
        interpolated_precision.append(max_precision)

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(recall_levels, interpolated_precision, marker='o')
    plt.title('График полноты/точности')
    plt.xlabel('Полнота')
    plt.ylabel('Точность')
    plt.grid()
    plt.xticks(np.arange(0.0, 1.1, 0.1))
    plt.yticks(np.arange(0.0, 1.1, 0.1))
    plt.axhline(0, color='black', lw=0.5)
    plt.axvline(0, color='black', lw=0.5)
     # Сохранение графика в буфер
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Конвертация графика в base64
    import base64
    graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'calculate_metrics.html', {'documents': documents, 'search_words': search_words, 'relevant_docs': sorted_relevant_docs,
        'precision': precision, 'recall': recall, 'accuracy': accuracy, 'error': error, 'f_measure': f_measure, 'precision_n': precision_n, 'avg_Prec': avg_Prec, 'graphic': graphic})
 

def calculate_relevant(search_words, text):
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(text)
    lemmatized_words = [lemmatizer.lemmatize(word.lower()) for word in words]
    lemmatized_word_counts = Counter(lemmatized_words[:50000])

    relevant_search_word = {word: (lemmatized_word_counts.get(lemmatizer.lemmatize(word.lower()), 0)) for word in search_words}
    
    return relevant_search_word


@csrf_exempt
def translate_text(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        target_lang = request.POST.get('target_lang')

        if text:
            translator = Translator()
            translated_text = translator.translate(text, dest=target_lang).text

            return JsonResponse({'translated_text': translated_text})
        else:
            return JsonResponse({'error': 'Missing text or target language'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)