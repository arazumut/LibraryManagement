from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Loan
from books.models import Book

@login_required
def loan_list(request):
    # Loan list logic here
    loans = []
    context = {
        'active_menu': 'loans',
        'loans': loans
    }
    return render(request, 'loans/loan_list.html', context)

@login_required
def my_loans(request):
    # My loans logic here
    my_loans = []
    context = {
        'active_menu': 'loans',
        'loans': my_loans
    }
    return render(request, 'loans/my_loans.html', context)

@login_required
def manage_loans(request):
    # Manage loans logic here
    loans = []
    context = {
        'active_menu': 'manage_loans',
        'loans': loans
    }
    return render(request, 'loans/manage_loans.html', context)

@login_required
def borrow_book(request, book_id):
    # Borrow book logic here
    return redirect('books:detail', book_id=book_id)

@login_required
def return_book(request, loan_id):
    # Return book logic here
    return redirect('loans:my_loans')
