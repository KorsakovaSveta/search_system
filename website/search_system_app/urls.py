from django.urls import path
from . import views, lang_recognition, auto_report
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
    path('download_report/', auto_report.download_result_txt_file, name='download_report')
]