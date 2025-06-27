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
    path('user/<int:user_id>/', views.user_analytics, name='user_analytics'),
    path('user/reading-patterns/', views.user_reading_patterns, name='user_reading_patterns'),
    
    # Popülerlik ve trend raporları
    path('popularity/', views.popularity_report, name='popularity_report'),
    path('trends/', views.trend_analysis, name='trend_analysis'),
    
    # Dışa aktarım
    path('export/csv/', views.export_analytics_csv, name='export_csv'),
    path('export/pdf/', views.export_analytics_pdf, name='export_pdf'),
    
    # API endpoints
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/real-time-stats/', views.get_real_time_stats, name='real_time_stats'),
]
