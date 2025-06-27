from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Ana analitik dashboard
    path('', views.analytics_dashboard, name='dashboard'),
    
    # Kütüphane analitikleri
    path('library/<int:library_id>/', views.library_analytics, name='library_analytics'),
    path('library/comparison/', views.library_comparison, name='library_comparison'),
    
    # Kullanıcı analitikleri
    path('user/reading-patterns/', views.user_reading_analytics, name='user_analytics'),
    
    # Popülerlik ve trend raporları
    path('popularity/', views.book_popularity_report, name='popularity_report'),
    
    # Dışa aktarım
    path('export/', views.export_analytics_data, name='export_csv'),
]
