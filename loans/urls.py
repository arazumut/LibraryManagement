from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_list, name='list'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('manage/', views.manage_loans, name='manage'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow'),
    path('return/<int:loan_id>/', views.return_book, name='return'),
]
