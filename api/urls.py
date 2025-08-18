from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import (
    UserViewSet,
    BookViewSet,
    LibraryViewSet,
    LoanViewSet,
    CategoryViewSet,
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
    # OpenAPI 3 documentation with Swagger UI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
