from django.shortcuts import render
from collections import Counter
from bs4 import BeautifulSoup
import os
import requests
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import ngrams
from scipy.spatial.distance import cosine
from collections import Counter
import json
from django.http import HttpResponse

def generate_training_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read().lower().replace('\n', '')
    return text

german_text = generate_training_data(os.path.abspath('search_system_app/train_texts/german.txt'))
spanish_text = generate_training_data(os.path.abspath('search_system_app/train_texts/spanish.txt'))

def ngrams(text, n=5):
    return [text[i:i+n] for i in range(len(text)-n+1)]

def ngram_profile(text):
    n_gram_counts = Counter(ngrams(text))
    return n_gram_counts


def alphabetic_profile(text):
    return Counter(text)


german_profile_alph = alphabetic_profile(german_text)
spanish_profile_alph = alphabetic_profile(spanish_text)
german_profile_n_gramm = ngram_profile(german_text)
spanish_profile_n_gramm = ngram_profile(spanish_text)

def calculate_distance(doc_profile, german_profile, spanish_profile):
    distances = {}
    
    # Преобразуем профили в векторы
    all_n_grams = set(doc_profile.keys()).union(set(spanish_profile.keys()), set(german_profile.keys()))
    
    doc_vector = [doc_profile.get(n_gram, 0) for n_gram in all_n_grams]
    spanish_vector = [spanish_profile.get(n_gram, 0) for n_gram in all_n_grams]
    german_vector = [german_profile.get(n_gram, 0) for n_gram in all_n_grams]
    
    distances['Spanish'] = cosine(doc_vector, spanish_vector)
    distances['German'] = cosine(doc_vector, german_vector)
    
    return  distances['German'], distances['Spanish'],  min(distances, key=distances.get)


def prepare_training_data():
    
    texts = [german_text, spanish_text]
    labels = ['German', 'Spanish']
    
    return texts, labels

def train_model():
    texts, labels = prepare_training_data()
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    
    model = MLPClassifier(max_iter=1000)
    model.fit(X, labels)
    
    return model, vectorizer

def predict_language(text, model, vectorizer):
    text_vector = vectorizer.transform([text]).toarray().flatten()  # Ensure it's 1-D
    prediction = model.predict([text_vector])
    
    # Get language profiles as 1-D arrays
    german_vector = vectorizer.transform([german_text]).toarray().flatten()
    spanish_vector = vectorizer.transform([spanish_text]).toarray().flatten()
    
    # Calculate cosine distances
    distance_german = cosine(text_vector, german_vector)
    distance_spanish = cosine(text_vector, spanish_vector)
    
    return prediction[0], distance_german, distance_spanish


def language_recognition(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower().replace('\n', '')
        doc_n_gramm = ngram_profile(text)
        doc_profile = alphabetic_profile(text)
        model, vectorizer = train_model()

        alpha_german, alpha_spanish, lang = calculate_distance(doc_profile, german_profile_alph, spanish_profile_alph)
        n_gramm_german, n_gramm_spanish, lang = calculate_distance(doc_n_gramm, german_profile_n_gramm, spanish_profile_n_gramm)
        predicted_language, dist_german, dist_spanish = predict_language(text, model, vectorizer)

        results = {'N-gramm': [n_gramm_german, n_gramm_spanish, lang], 'Alphabetical method': [alpha_german, alpha_spanish, lang], 'Neural network method': [dist_german, dist_spanish, predicted_language]}

        results_for_download = {'N-gramm': {'German distance metric': n_gramm_german, 'Spanish distance metric': n_gramm_spanish, 'Language of the text':lang}, 'Alphabetical method': {'German distance metric': alpha_german, 'Spanish distance metric': alpha_spanish, 'Language of the text':lang}, 'Neural network method': {'German distance metric': dist_german, 'Spanish distance metric': dist_spanish, 'Language of the text':predicted_language}}
        
       
        request.session['results_for_download'] = results_for_download
        return render(request, 'lang_recognition.html', {'results': results})
    else:
        return render(request, 'lang_recognition.html')


def download_result_json_file(request):
    results_for_download = request.session.get('results_for_download', {})
    formatted_result = json.dumps(results_for_download, indent=4, separators=(',', ': '))
    response = HttpResponse(formatted_result, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="result.json"'
    
    return response
