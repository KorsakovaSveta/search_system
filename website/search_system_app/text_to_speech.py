# from django.shortcuts import render
# from django.http import JsonResponse
# from gtts import gTTS
# import os
# from django.conf import settings
# import uuid

# def text_to_speech(request):
#     if request.method == 'POST':
#         text = request.POST.get('text', '')
        
#         speed = float(request.POST.get('speed'))
#         voice_gender = request.POST.get('voice_gender')
        
#         # Создаем уникальное имя файла
#         filename = f"audio_{uuid.uuid4()}.mp3"
#         filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
#         # Создаем аудио файл
#         tts = gTTS(text=text, lang='fr', slow=(speed < 1.0))
#         tts.save(filepath)
        
#         # Возвращаем URL файла
#         file_url = request.build_absolute_uri(settings.MEDIA_URL + filename)
#         return JsonResponse({'success': True, 'file_url': file_url})
        
#     return render(request, 'text_to_speech.html')

# tts_app/views.py

import os
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from gtts import gTTS
import uuid

def text_to_speech(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        speed = float(request.POST.get('speed', 1.0))
        
        if text:
            # Создаем уникальное имя файла
            filename = f"speech_{uuid.uuid4()}.mp3"
            
            # Создаем директорию для аудиофайлов, если её нет
            audio_path = os.path.join(settings.MEDIA_ROOT, 'audio')
            os.makedirs(audio_path, exist_ok=True)
            
            # Полный путь к файлу
            filepath = os.path.join(audio_path, filename)
            
            # Генерируем речь
            tts = gTTS(text=text, lang='fr', slow=(speed < 1.0))
            tts.save(filepath)
            
            return JsonResponse({
                'success': True,
                'audio_url': f'/media/audio/{filename}'
            })
            
        return JsonResponse({'success': False, 'error': 'No text provided'})
        
    return render(request, 'text_to_speech.html')