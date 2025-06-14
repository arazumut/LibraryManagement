from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, BookRequest

@login_required
def book_list(request):
    # Book list logic here
    return render(request, 'books/book_list.html')

@login_required
def book_detail(request, book_id):
    # Book detail logic here
    return render(request, 'books/book_detail.html')

@login_required
def book_create(request):
    # Book create logic here
    return render(request, 'books/book_form.html')

@login_required
def book_edit(request, book_id):
    # Book edit logic here
    return render(request, 'books/book_form.html')

@login_required
def book_delete(request, book_id):
    # Book delete logic here
    return redirect('books:list')

@login_required
def book_requests(request):
    # Book requests logic here
    return render(request, 'books/book_requests.html')
