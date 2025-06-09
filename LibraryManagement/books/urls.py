from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('create/', views.create_book, name='create_book'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('<int:pk>/delete/', views.delete_book, name='delete_book'),
    path('<int:pk>/request/', views.request_book, name='request_book'),
    path('requests/', views.book_request_list, name='book_request_list'),
    path('requests/<int:pk>/respond/', views.respond_to_request, name='respond_to_request'),
    path('<int:pk>/add-note/', views.add_book_note, name='add_book_note'),
    path('notes/<int:pk>/edit/', views.edit_book_note, name='edit_book_note'),
    path('notes/<int:pk>/delete/', views.delete_book_note, name='delete_book_note'),
] 