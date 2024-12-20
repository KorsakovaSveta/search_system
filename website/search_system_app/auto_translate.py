# translator/utils/translation.py
from transformers import MarianMTModel, MarianTokenizer
import requests
from transformers import MarianMTModel, MarianTokenizer
from collections import Counter
import spacy
from django.shortcuts import render
from bs4 import BeautifulSoup
from .models import Word
from spacy import displacy
import re
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Get the list of dependency labels from the parser
parser_lst = nlp.pipe_labels['parser']

# Print the number of dependency labels and the labels themselves
print(len(parser_lst))
print(parser_lst)

# Print explanations for each dependency label
for label in parser_lst:
    print(f"{label}: {spacy.explain(label)}")


model_name = 'Helsinki-NLP/opus-mt-en-ru'
model = MarianMTModel.from_pretrained(model_name)
tokenizer = MarianTokenizer.from_pretrained(model_name)

# Загружаем модель для анализа частей речи
nlp = spacy.load("en_core_web_sm")

def process_link(url):
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Удаление ненужных тегов
    for tag in soup(['footer', 'head', 'img', 'script', 'style']):
        tag.decompose()
    
    article_text = ''
    for paragraph in soup.find_all('p'):
        article_text += paragraph.get_text()

    cleaned_text = re.sub(r'\[\d+\]', ' ', article_text)
    
    return cleaned_text

def translate_text(request):
    if request.method == 'POST':
        # Получаем текст для перевода
        doc_url = request.POST.get('url')

        input_text = process_link(doc_url)
        sentences_of_input_text = sent_tokenize(input_text)[:20]
        #input_text = input_text[:512]
        # Перевод текста
        translated = translate(' '.join(sentences_of_input_text))
        
        # Сохранение переведенных слов в базу данных
        save_translation_to_db(' '.join(sentences_of_input_text).lower())
        
       
        request.session['sentences_of_input_text'] = sent_tokenize(translated) 
        request.session['text'] = ' '.join(sentences_of_input_text).lower()
        # Отображаем данные на странице
        return render(request, 'auto_translate.html', {
            'url': doc_url,
            'input_text': ' '.join(sentences_of_input_text),
            'translated_text': translated,
        })
    return render(request, 'auto_translate.html')

def split_long_text(input_text, max_length=512):
    words = input_text.split()
    chunks = [" ".join(words[i:i + max_length]) for i in range(0, len(words), max_length)]
    return chunks

def translate(input_text):
    max_length = tokenizer.model_max_length
    chunks = split_long_text(input_text, max_length)
    
    translated_chunks = []
    for chunk in chunks:
        # Tokenize all sentences at once
        sentences = sent_tokenize(chunk)
        inputs = tokenizer(sentences, return_tensors="pt", padding=True)
        
        # Translate in one go
        translated_tokens = model.generate(**inputs, num_beams=4, max_length=128, early_stopping=True)
        translated_sentences = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
        
        translated_chunks.append(" ".join(translated_sentences))
    
    return " ".join(translated_chunks)

def save_translation_to_db(input_text):
    # Сохраняем переведенные слова в базу данных
    doc = nlp(' '.join(set(input_text.split())))
    for token in doc:
        if not Word.objects.filter(english_word=token.text).exists():
            # Получаем перевод
            translation = translate(token.text)
            # Сохраняем в базу данных
            Word.objects.create(english_word=token.text, russian_translation=translation, pos_tag=token.pos_)

def count_word_frequency(request):
    # Анализируем частоты слов в тексте
    text = request.session.get('text')
    cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
    # Разбиваем текст на слова
    words = cleaned_text.split()
    # Используем Counter для подсчёта частот
    words_freq = Counter(words)
    return render(request, 'words_freq.html', {'words_freq': dict(words_freq)})

def get_pos_tags(request):
    # Используем spacy для извлечения грамматических тегов
    text = request.session.get('text')
    doc = nlp(text)
    pos_tags = [(token.text, token.pos_) for token in doc]
    return render(request, 'pos_tags.html', {'pos_tags': pos_tags})

def generate_syntax_tree(request):
    """
    Генерирует синтаксическое дерево для входного текста.
    Возвращает HTML, который можно вставить в шаблон.
    """
    html_trees = {}
    sentences = request.session.get('sentences_of_input_text')
    for sentence in sentences:
        doc = nlp(sentence)  # Используем spacy для анализа текста
        # Генерация синтаксического дерева в HTML
        html_trees[sentence] = displacy.render(doc, style='dep', page=True)

    return render(request, 'tree.html', {'syntax_trees_html': html_trees})