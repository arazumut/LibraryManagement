from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='list'),
    path('<int:book_id>/', views.book_detail, name='detail'),
    path('create/', views.book_create, name='create'),
    path('<int:book_id>/edit/', views.book_edit, name='edit'),
    path('<int:book_id>/delete/', views.book_delete, name='delete'),
    path('requests/', views.book_requests, name='requests'),
]
