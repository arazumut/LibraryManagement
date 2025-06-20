from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, BookRequest
from libraries.models import Library
from library_management.decorators import check_account_activation, user_is_library_admin

@login_required
@check_account_activation
def book_list(request):
    books = Book.objects.all()
    context = {
        'active_menu': 'books',
        'books': books
    }
    return render(request, 'books/book_list.html', context)

@login_required
@check_account_activation
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    context = {
        'active_menu': 'books',
        'book': book
    }
    return render(request, 'books/book_detail.html', context)

@login_required
@check_account_activation
@user_is_library_admin
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
@login_required
@check_account_activation
@user_is_library_admin
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
@login_required
@check_account_activation
@user_is_library_admin
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

@login_required
def book_request_create(request):
    """Yeni bir kitap isteği oluştur"""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        library_id = request.POST.get('library')
        description = request.POST.get('description')
        
        # Önce kitabı bulmaya çalış
        try:
            # get yerine filter.first() kullanarak birden fazla sonuç durumunda hata oluşmasını engelle
            matching_books = Book.objects.filter(title=title, author=author, library_id=library_id)
            
            if matching_books.count() == 0:
                raise Book.DoesNotExist
            
            # Eğer birden fazla kitap bulunduysa, ilkini al
            book = matching_books.first()
            
            # İsteğe bağlı olarak birden fazla kitap bulunduğunda bildirim eklenebilir
            if matching_books.count() > 1:
                from django.contrib import messages
                messages.warning(request, f"Aynı başlık ve yazara sahip birden fazla kitap bulundu. İlk bulunan kitap için istek oluşturulacak: {book.title}")
                
        except Book.DoesNotExist:
            # Kitap bulunamadı, mesaj gösterip yönlendir
            from django.contrib import messages
            messages.error(request, "Belirtilen kitap bulunamadı. Lütfen bilgileri kontrol ediniz.")
            return redirect('books:requests')
            
        # Daha önce bu kitap için bekleyen bir istek var mı kontrol et
        existing_request = BookRequest.objects.filter(
            book=book, 
            requester=request.user, 
            status='pending'
        ).exists()
        
        if existing_request:
            from django.contrib import messages
            messages.warning(request, "Bu kitap için zaten bekleyen bir isteğiniz bulunmaktadır.")
            return redirect('books:requests')
        
        # Yeni istek oluştur
        book_request = BookRequest.objects.create(
            book=book,
            requester=request.user,
            message=description,
            status='pending'
        )
        
        from django.contrib import messages
        messages.success(request, "Kitap isteği başarıyla oluşturuldu.")
        
    return redirect('books:requests')

@login_required
def book_request_cancel(request, request_id):
    """Kullanıcının kendi isteğini iptal etmesi"""
    book_request = get_object_or_404(BookRequest, id=request_id)
    
    # İsteğin sahibi olup olmadığını kontrol et
    if book_request.requester != request.user:
        from django.contrib import messages
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('books:requests')
    
    if book_request.cancel():
        from django.contrib import messages
        messages.success(request, "Kitap isteği başarıyla iptal edildi.")
    else:
        from django.contrib import messages
        messages.error(request, "İstek iptal edilemedi. Sadece bekleyen istekler iptal edilebilir.")
    
    return redirect('books:requests')

@login_required
def book_request_approve(request, request_id):
    """Yetkili kişinin isteği onaylaması"""
    if not request.user.is_staff:
        from django.contrib import messages
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('books:requests')
    
    book_request = get_object_or_404(BookRequest, id=request_id)
    response_message = request.POST.get('response_message', '')
    
    if book_request.approve(response_message):
        from django.contrib import messages
        messages.success(request, f"{book_request.book.title} kitabı için istek onaylandı.")
    else:
        from django.contrib import messages
        messages.error(request, "İstek onaylanamadı. Sadece bekleyen istekler onaylanabilir.")
    
    # Yönetici paneline yönlendir
    return redirect('admin:books_bookrequest_changelist')

@login_required
def book_request_reject(request, request_id):
    """Yetkili kişinin isteği reddetmesi"""
    if not request.user.is_staff:
        from django.contrib import messages
        messages.error(request, "Bu işlem için yetkiniz bulunmamaktadır.")
        return redirect('books:requests')
    
    book_request = get_object_or_404(BookRequest, id=request_id)
    response_message = request.POST.get('response_message', '')
    
    if book_request.reject(response_message):
        from django.contrib import messages
        messages.success(request, f"{book_request.book.title} kitabı için istek reddedildi.")
    else:
        from django.contrib import messages
        messages.error(request, "İstek reddedilemedi. Sadece bekleyen istekler reddedilebilir.")
    
    # Yönetici paneline yönlendir
    return redirect('admin:books_bookrequest_changelist')
