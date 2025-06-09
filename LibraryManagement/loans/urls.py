from django.urls import path
from . import views

urlpatterns = [
    path('', views.loan_list, name='loan_list'),
    path('create/', views.create_loan, name='create_loan'),
    path('<int:pk>/', views.loan_detail, name='loan_detail'),
    path('<int:pk>/return/', views.return_book, name='return_book'),
    path('borrowed/', views.borrowed_books, name='borrowed_books'),
    path('lent/', views.lent_books, name='lent_books'),
    path('overdue/', views.overdue_books, name='overdue_books'),
] 