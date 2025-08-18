"""
URL configuration for library_management project.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import views
from accounts import views as account_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', account_views.login_view, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls')),
    path('libraries/', include('libraries.urls')),
    path('loans/', include('loans.urls')),
    path('search/', views.search, name='search'),
    
    # API endpoints
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # JWT Token endpoints for Flutter
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
