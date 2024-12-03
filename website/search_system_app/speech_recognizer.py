# import speech_recognition as sr
# from gtts import gTTS
# from playsound import playsound
# import os

# # Список команд
# COMMANDS = {
#     "ouvrir la porte": "La porte est ouverte.",
#     "allumer la lumière": "La lumière est allumée.",
#     "éteindre la lumière": "La lumière est éteinte.",
#     "fermer la porte": "La porte est fermée."
# }

# # Функция распознавания речи
# def recognize_speech():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Parlez maintenant :")
#         try:
#             audio = recognizer.listen(source, timeout=5)  # Ждём 5 секунд для захвата
#             # Использование Google API для французского языка
#             text = recognizer.recognize_google(audio, language="fr-FR")
#             print(f"Vous avez dit : {text}")
#             return text.lower()
#         except sr.UnknownValueError:
#             print("Je n'ai pas compris.")
#             notify_user("Je n'ai pas compris.")
#             return None
#         except sr.RequestError as e:
#             print(f"Erreur du service : {e}")
#             notify_user("Erreur du service.")
#             return None
#         except sr.WaitTimeoutError:
#             print("Temps d'attente écoulé, veuillez réessayer.")
#             notify_user("Temps d'attente écoulé.")
#             return None

# # Функция выполнения команды
# def execute_command(command):
#     if command in COMMANDS:
#         response = COMMANDS[command]
#         print(response)
#         notify_user(response)
#     else:
#         print("Commande non reconnue.")
#         notify_user("Commande non reconnue.")

# # Функция уведомления пользователя с помощью TTS
# def notify_user(message):
#     try:
#         tts = gTTS(message, lang='fr')
#         file_path = "notification.mp3"
#         tts.save(file_path)
#         playsound(file_path)
#         os.remove(file_path)
#     except Exception as e:
#         print(f"Erreur lors de la notification : {e}")

# # Основная функция
# def main():
#     print("Système de reconnaissance vocale activé.")
#     notify_user("Système activé. Parlez pour donner une commande.")
#     while True:
#         text = recognize_speech()
#         if text:
#             execute_command(text)

# # Запуск программы
# if __name__ == "__main__":
#     main()
import speech_recognition as sr
from gtts import gTTS
import os
from datetime import datetime
from playsound import playsound
from transformers import pipeline

class SpeechRecognitionSystem:
    def __init__(self):
        # Инициализация распознавателя речи
        self.recognizer = sr.Recognizer()
        
        # Словарь команд и соответствующих действий
        self.commands = {
            "bonjour": self.say_hello,
            "quelle heure est-il": self.tell_time,
            "au revoir": self.say_goodbye,
            "merci": self.say_welcome,
            "qu'est-ce que la littérature": self.say_about_literature,
            "écrire un essai": self.generate_essay
        }
        
        self.text_generator = pipeline("text-generation", model="gpt2", tokenizer="gpt2")

    def speak(self, text):
        """Произнести текст"""
        print(f"Système: {text}")
        tts = gTTS(text=text, lang='fr')
        audio_file = "temp_audio.mp3"
        tts.save(audio_file)
        playsound(audio_file)
        os.remove(audio_file)  # Удаление временного файла

    def listen(self):
        """Прослушивание и распознавание речи"""
        with sr.Microphone() as source:
            print("En écoute...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            print(f"Vous avez dit: {text}")
            return text.lower()
        except sr.UnknownValueError:
            self.speak("Désolé, je n'ai pas compris")
            return None
        except sr.RequestError:
            self.speak("Désolé, il y a un problème avec le service")
            return None

    # Команды
    def say_hello(self):
        self.speak("Bonjour! Comment puis-je vous aider?")

    def tell_time(self):
        current_time = datetime.now().strftime("%H:%M")
        self.speak(f"Il est {current_time}")

    def say_goodbye(self):
        self.speak("Au revoir! Bonne journée!")
        return "exit"

    def say_welcome(self):
        self.speak("Je vous en prie!")

    def say_about_literature(self):
        self.speak("La littérature est l'ensemble des oeuvres écrites auxquelles on reconnaît une finalité esthétique.")

    def generate_essay(self):
        self.speak("Sur quel sujet voulez-vous que j'écrive une rédaction?")
        topic = self.listen()
        if topic:
            self.speak(f"Un instant, je prépare une rédaction sur {topic}...")
            essay = self.text_generator(f"Rédaction sur {topic}:", max_length=150, num_return_sequences=1, truncation=True, pad_token_id=self.text_generator.tokenizer.eos_token_id)[0]['generated_text']
            print(f"Rédaction générée: {essay}")
            self.speak("Voici votre rédaction:")
            self.speak(essay)

    def run(self):
        """Основной цикл работы системы"""
        self.speak("Système de reconnaissance vocale activé")
        
        while True:
            text = self.listen()
            if text:
                for command, action in self.commands.items():
                    if command in text:
                        result = action()
                        if result == "exit":
                            return

if __name__ == "__main__":
    system = SpeechRecognitionSystem()
    system.run()