from django.urls import path
from . import views, lang_recognition, auto_report, auto_translate, text_to_speech
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    
    path('', views.search_results, name='search_results'),
    path('add_links/', views.add_link, name='add_links'),
    path('calculate_metrics/', views.calculate_metrics, name='calculate_metrics'),
    path('translate/', views.translate_text, name='translate'),
    path('lang_recognition/', lang_recognition.language_recognition, name = 'lang_recognition'),
    path('download/', lang_recognition.download_result_json_file, name = 'download'),
    path('auto_report/', auto_report.show_report, name = 'auto_report'),
    path('auto_keywords_report/', auto_report.show_keywords_report, name = 'auto_keywords_report'),
    path('download_report/', auto_report.download_result_txt_file, name='download_report'),
    path('auto_translate/', auto_translate.translate_text, name='auto_translate'),
    path('create_tree/', auto_translate.generate_syntax_tree, name='create_tree'),
    path('get_words_freq/', auto_translate.count_word_frequency, name='get_words_freq'),
    path('get_pos_tags/', auto_translate.get_pos_tags, name='get_pos_tags'),
    path('text_to_speech/', text_to_speech.text_to_speech, name='text_to_speech'),
    #path('export-results/', auto_translate.export_results, name='export_results'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)