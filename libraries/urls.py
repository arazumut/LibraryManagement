from django.urls import path
from . import views

app_name = 'libraries'

urlpatterns = [
    path('', views.library_list, name='list'),
    path('<int:library_id>/', views.library_detail, name='detail'),
    path('create/', views.library_create, name='create'),
    path('<int:library_id>/edit/', views.library_edit, name='edit'),
    path('<int:library_id>/delete/', views.library_delete, name='delete'),
]
