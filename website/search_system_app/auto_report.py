import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import re
from collections import defaultdict
import math
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse
import string
import yake
nltk.download('punkt')
nltk.download('stopwords')

class DocumentReport:
    def __init__(self):
        self.spanish_stemmer = SnowballStemmer('spanish')
        self.german_stemmer = SnowballStemmer('german')
        
        self.spanish_stops = set(stopwords.words('spanish'))
        self.german_stops = set(stopwords.words('german'))
        
    def detect_language(self, text):
        spanish_chars = len(re.findall(r'[áéíóúñ]', text.lower()))
        german_chars = len(re.findall(r'[äöüß]', text.lower()))
        return 'spanish' if spanish_chars > german_chars else 'german'
    
    def preprocess_text(self, text):
        language = self.detect_language(text)
        
        stemmer = self.spanish_stemmer if language == 'spanish' else self.german_stemmer
        stop_words = self.spanish_stops if language == 'spanish' else self.german_stops
        
        sentences = sent_tokenize(text)
        
        # Предобработка для каждого предложения
        processed_sentences = []
        for sentence in sentences:
            # Токенизация и приведение к нижнему регистру
            words = word_tokenize(sentence.lower())
            
            # Удаление стоп-слов и пунктуации, стемминг
            words = [stemmer.stem(word) for word in words 
                    if word.isalnum() and word not in stop_words]
            
            processed_sentences.append((sentence, words))
            
        return processed_sentences
    
    def calculate_tf_idf(self, processed_sentences):
        # Подсчет TF для каждого слова в каждом предложении
        term_freq = defaultdict(lambda: defaultdict(int))
        for _, words in processed_sentences:
            for word in words:
                term_freq[word][_] += 1
        
        # Подсчет IDF
        doc_freq = defaultdict(int)
        for _, words in processed_sentences:
            unique_words = set(words)
            for word in unique_words:
                doc_freq[word] += 1
        
        # Вычисление TF-IDF
        num_docs = len(processed_sentences)
        tf_idf = defaultdict(float)
        
        for sentence, words in processed_sentences:
            score = 0
            for word in words:
                tf = term_freq[word][sentence]
                idf = math.log(num_docs / doc_freq[word])
                score += tf * idf
            tf_idf[sentence] = score
            
        return tf_idf
    
    def calculate_position_weights(self, text, sentences):
        total_chars = len(text)
        current_pos = 0
        position_weights = {}
        
        for sentence in sentences:
            # Вес в зависимости от позиции в документе
            doc_position_weight = 1 - (current_pos / total_chars)
            position_weights[sentence] = doc_position_weight
            current_pos += len(sentence)
            
        return position_weights
    
    def generate_report(self, text, num_sentences=10):
        # Предобработка текста
   
        processed_sentences = self.preprocess_text(text)
        original_sentences = [s[0] for s in processed_sentences]

        tf_idf_weights = self.calculate_tf_idf(processed_sentences)
        position_weights = self.calculate_position_weights(text, [s[0] for s in processed_sentences])
        
        final_weights = {}
        for sentence in original_sentences:
            final_weights[sentence] = tf_idf_weights[sentence] * position_weights[sentence]
    
        sorted_sentences = sorted(final_weights.items(), key=lambda x: x[1], reverse=True)
        top_sentences = sorted_sentences[:num_sentences]
        
        summary_sentences = []
        for sentence in original_sentences:
            if sentence in dict(top_sentences):
                summary_sentences.append(sentence)
                if len(summary_sentences) == 10:
                    break
        
        return ' '.join(summary_sentences)
    

    def receiving_text(self, link):
        response = requests.get(link)
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        for footer in soup.find_all('footer'):
            footer.decompose()

        for list_tag in soup.find_all('head'):
            list_tag.decompose()

        for list_tag in soup.find_all('img'):
            list_tag.decompose()

        article_text = ''
        for paragraph in soup.find_all('p'):
            article_text += paragraph.get_text()

        cleaned_text = re.sub(r'\[\d+\]', ' ', article_text)
        
        return cleaned_text

    def auto_report(self, request):
        if request.method == 'POST':
            url = request.POST.get('url')
            text = self.receiving_text(url)
            report = self.generate_report(text)
            request.session['report_for_download'] = report
            return report, url
    
    #keyword report
        
    def generate_keywords_report(self, text, language, 
                            max_ngram_size: int = 2, 
                            deduplication_threshold: float = 0.3,
                            deduplication_algo: str = 'seqm'):
        
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
    
        cleaned_text = self.clean_text(text, language)
        num_of_keywords = self.determine_num_of_keywords(len(cleaned_text.split()))

        try:
            custom_kw_extractor = yake.KeywordExtractor(lan=language, 
                                                        n=max_ngram_size, 
                                                        dedupLim=deduplication_threshold, 
                                                        dedupFunc=deduplication_algo, 
                                                        
                                                        top=num_of_keywords, 
                                                        features=None)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("YAKE library not installed")

        keywords = custom_kw_extractor.extract_keywords(cleaned_text)

        top_keywords = [kw[0] for kw in keywords]

        return ', '.join(top_keywords)

    def clean_text(self, text: str, language: str) -> str:

        if language == 'german':
            stop_words = self.german_stops 
        else:
            stop_words = self.spanish_stops

        tokens = text.split()

        cleaned_tokens = [
            word for word in tokens 
            if word.lower() not in stop_words and word not in string.punctuation
        ]
        return ' '.join(cleaned_tokens)

    def determine_num_of_keywords(self, text_length: int) -> int:
        if text_length < 50:
            return 10
        elif text_length < 200:
            return 20
        elif text_length < 500:
            return 30
        else:
            return 50
    
    def auto_report_keywords(self, request):
        if request.method == 'POST':
            url = request.POST.get('url')
            text = self.receiving_text(url)
            language = self.detect_language(text)
            report = self.generate_keywords_report(text, language)
            request.session['report_for_download'] = report
            return report, url
    
def show_report(request):
    report = DocumentReport()
    try:
        ready_report, url = report.auto_report(request)
    except TypeError:
        ready_report, url = '', ''
    return render(request, 'auto_report.html', {'report': ready_report, 'url':url})

def show_keywords_report(request):
    report = DocumentReport()
    try:
        ready_keyword_report, url = report.auto_report_keywords(request)
    except TypeError:
        ready_keyword_report, url = '', ''
    return render(request, 'auto_keywords_report.html', {'report': ready_keyword_report, 'url':url})

def download_result_txt_file(request):
    report_for_download = request.session.get('report_for_download')
    report_for_download = sent_tokenize(report_for_download)
    report_for_download = '\n'.join(report_for_download)
    response = HttpResponse(report_for_download, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="result.txt"'
    return response