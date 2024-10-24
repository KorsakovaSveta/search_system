from google.cloud import translate_v2 as translate
import os

# Установите переменную окружения для ключа API
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/service-account-file.json'

class GoogleTranslate:
    def __init__(self):
        self.client = translate.Client()

    def translate_text(self, text, target_language):
        result = self.client.translate(text, target_language=target_language)
        return result['translatedText']