from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet,
    BookViewSet,
    LibraryViewSet,
    LoanViewSet,
    CategoryViewSet,
    UserRegisterView,
    CurrentUserView,
)

# DRF router setup
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'books', BookViewSet)
router.register(r'libraries', LibraryViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'categories', CategoryViewSet)

# API URL patterns
urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication endpoints for Flutter
    path('auth/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('auth/register/', UserRegisterView.as_view(), name='api_register'),
    path('auth/me/', CurrentUserView.as_view(), name='api_current_user'),
    
    # OpenAPI 3 documentation with Swagger UI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
