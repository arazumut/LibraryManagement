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
    from .models import Book
    
    libraries = Library.objects.all()
    status_choices = Book.STATUS_CHOICES
    
    if request.method == 'POST':
        # Extract data from the form
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        description = request.POST.get('description')
        library_id = request.POST.get('library')
        publication_year = request.POST.get('publication_year')
        publisher = request.POST.get('publisher')
        language = request.POST.get('language')
        pages = request.POST.get('pages')
        status = request.POST.get('status', 'available')
        
        # Create the book object
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            description=description,
            library_id=library_id,
            publication_year=publication_year if publication_year else None,
            publisher=publisher,
            language=language,
            pages=pages if pages else None,
            status=status
        )
        
        # Handle cover image upload
        if request.FILES.get('cover_image'):
            book.cover_image = request.FILES.get('cover_image')
            
        book.save()
        return redirect('books:detail', book_id=book.id)
    
    context = {
        'active_menu': 'books',
        'libraries': libraries,
        'status_choices': status_choices
    }
    return render(request, 'books/book_form.html', context)

@login_required
def book_edit(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    libraries = Library.objects.all()
    status_choices = Book.STATUS_CHOICES
    
    if request.method == 'POST':
        # Extract data from the form
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.description = request.POST.get('description')
        book.library_id = request.POST.get('library')
        
        publication_year = request.POST.get('publication_year')
        book.publication_year = publication_year if publication_year else None
        
        book.publisher = request.POST.get('publisher')
        book.language = request.POST.get('language')
        
        pages = request.POST.get('pages')
        book.pages = pages if pages else None
        
        book.status = request.POST.get('status', 'available')
        
        # Handle cover image upload
        if request.FILES.get('cover_image'):
            book.cover_image = request.FILES.get('cover_image')
            
        book.save()
        return redirect('books:detail', book_id=book.id)
    
    context = {
        'active_menu': 'books',
        'book': book,
        'libraries': libraries,
        'status_choices': status_choices
    }
    return render(request, 'books/book_form.html', context)

@login_required
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book.delete()
        return redirect('books:list')
    
    context = {
        'active_menu': 'books',
        'book': book
    }
    return render(request, 'books/book_confirm_delete.html', context)

@login_required
def book_requests(request):
    book_requests = BookRequest.objects.filter(requester=request.user)
    libraries = Library.objects.all()
    
    # Hata ayıklama amaçlı context bilgisini zenginleştirelim
    import json
    from django.forms.models import model_to_dict
    
    # Veri yapısını JSON serileştirmesi için hazırlama
    debug_requests = []
    for req in book_requests:
        debug_data = {
            'id': req.id,
            'book_title': req.book.title if req.book else 'Unknown',
            'requester': req.requester.username,
            'status': req.status,
            'requested_at': req.requested_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': req.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        debug_requests.append(debug_data)
    
    context = {
        'active_menu': 'book_requests',
        'book_requests': book_requests,
        'libraries': libraries,
        'debug_data': json.dumps(debug_requests)
    }
    return render(request, 'books/book_requests.html', context)
