from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_list, name='library_list'),
    path('create/', views.create_library, name='create_library'),
    path('<int:pk>/', views.library_detail, name='library_detail'),
    path('<int:pk>/edit/', views.edit_library, name='edit_library'),
    path('<int:pk>/delete/', views.delete_library, name='delete_library'),
] 