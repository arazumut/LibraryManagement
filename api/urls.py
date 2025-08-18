from django.urls import path, include
from rest_framework import routers
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
]
