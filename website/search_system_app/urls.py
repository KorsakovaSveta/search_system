from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    
    path('', views.search_results, name='search_results'),
    path('add_links/', views.add_link, name='add_links'),
    path('calculate_metrics/', views.calculate_metrics, name='calculate_metrics'),
    path('translate/', views.translate_text, name='translate')
]