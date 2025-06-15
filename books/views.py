from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, BookRequest
from libraries.models import Library

@login_required
def book_list(request):
    books = Book.objects.all()
    context = {
        'active_menu': 'books',
        'books': books
    }
    return render(request, 'books/book_list.html', context)

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    context = {
        'active_menu': 'books',
        'book': book
    }
    return render(request, 'books/book_detail.html', context)

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
    book_requests = BookRequest.objects.filter(user=request.user)
    libraries = Library.objects.all()
    
    context = {
        'active_menu': 'book_requests',
        'book_requests': book_requests,
        'libraries': libraries
    }
    return render(request, 'books/book_requests.html', context)
