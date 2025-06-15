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
    path('requests/create/', views.book_request_create, name='request_create'),
    path('requests/<int:request_id>/cancel/', views.book_request_cancel, name='request_cancel'),
    path('requests/<int:request_id>/approve/', views.book_request_approve, name='request_approve'),
    path('requests/<int:request_id>/reject/', views.book_request_reject, name='request_reject'),
]
