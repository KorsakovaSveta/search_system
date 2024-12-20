import speech_recognition as sr
from gtts import gTTS
import os
from datetime import datetime
from playsound import playsound
import google.generativeai as genai
from django.http import JsonResponse
import threading
from django.shortcuts import render

class SpeechRecognitionSystem:
    def __init__(self):
        # Инициализация распознавателя речи
        self.recognizer = sr.Recognizer()
        self.is_active = False
        self.conversation_history = []
        # Словарь команд и соответствующих действий
        self.commands = {
            "bonjour": self.say_hello,
            "quelle heure est-il": self.tell_time,
            # "au revoir": self.say_goodbye,
            "merci": self.say_welcome,
            "qu'est-ce que la littérature": self.say_about_literature,
            "écrire": self.generate_essay
        }
        
        # Настройка Generative AI
        genai.configure(api_key='AIzaSyAHcj6-yuym_aFmj10WVIZdNH9VTYWBCAY')
        self.model = genai.GenerativeModel('gemini-pro')

    def speak(self, text):
        """Произнести текст"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.conversation_history.append({
            'speaker': 'System',
            'message': text,
            'timestamp': timestamp
        })
        tts = gTTS(text=text, lang='fr')
        audio_file = "temp_audio.mp3"
        tts.save(audio_file)
        playsound(audio_file)
        os.remove(audio_file)  # Удаление временного файла

    def listen(self):
        """Прослушивание и распознавание речи"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.conversation_history.append({
                'speaker': 'User',
                'message': text,
                'timestamp': timestamp
            })
            return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            self.speak("Désolé, il y a un problème avec le service.")  # Извините, возникла проблема с сервисом.
            return None

    # Команды
    def say_hello(self):
        self.speak("Bonjour! Comment puis-je vous aider?")  # Здравствуйте! Могу я чем-нибудь помочь?

    def tell_time(self):
        current_time = datetime.now().strftime("%H:%M")
        self.speak(f"Il est {current_time}")  # Текущее время

    # def say_goodbye(self):
    #     self.speak("Au revoir!")  # До свидания
    #     return "exit"

    def say_welcome(self):
        self.speak("Je vous en prie!")  # Пожалуйста!

    def say_about_literature(self):
        self.speak("La littérature est l'ensemble des oeuvres écrites auxquelles on reconnaît une finalité esthétique.")
        # Литература – это совокупность письменных произведений, в которых мы видим эстетическую цель.

    # Асинхронная генерация эссе
    def generate_essay_async(self, topic):
        """Фоновая генерация эссе"""
        try:
            prompt = f"""Écrivez un essai bien structuré en français sur le sujet: {topic}
            L'essai doit contenir:
            - Une introduction
            - 2-3 arguments principaux
            - Une conclusion
            Longueur: environ 250-300 mots"""
            
            # Вызов API для генерации текста
            response = self.model.generate_content(prompt)
            essay = response.text

            # Сохранение результата и уведомление
            self.conversation_history.append({
                'speaker': 'System',
                'message': essay,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
           
            print(essay)  # Для отладки
        except Exception as e:
            self.speak("Désolé, une erreur est survenue lors de la génération de l'essai.")  # Сообщение об ошибке
            print(f"Erreur: {e}")

    def generate_essay(self):
        """Запуск фоновой задачи для генерации эссе"""
        self.speak("Sur quel sujet voulez-vous que j'écrive une rédaction?")  # На какую тему вы хотите, чтобы я написал эссе?
        topic = self.listen()
        if topic:
            self.speak(f"Un instant, je prépare une rédaction sur {topic}...")  # Уведомление о начале генерации
            # Запуск отдельного потока
            thread = threading.Thread(target=self.generate_essay_async, args=(topic,))
            thread.start()
        else:
            self.speak("Je n'ai pas entendu le sujet. Veuillez répéter, s'il vous plaît.")  # Я не расслышал тему, повторите.

    def run(self):
        """Основной цикл работы системы"""
        self.speak("Système de reconnaissance vocale activé")  # Система распознавания голоса активирована
        self.is_active = True
        while self.is_active:
            text = self.listen()
            
            if text:
                for command, action in self.commands.items():
                    if command in text:
                        result = action()
                        if result == "exit":
                            return

# Объект распознавания речи
speech_system = SpeechRecognitionSystem()

# Django Views
def speech_recognizer(request):
    return render(request, 'speech_recognizer.html')

def start_recognition(request):
    if not speech_system.is_active:
        thread = threading.Thread(target=speech_system.run)
        thread.start()
        return JsonResponse({'status': 'started'})
    return JsonResponse({'status': 'already running'})

def stop_recognition(request):
    speech_system.is_active = False
    return JsonResponse({'status': 'stopped'})

def get_conversations(request):
    return JsonResponse({'conversations': speech_system.conversation_history})
