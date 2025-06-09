from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Book, BookRequest, BookNote
from .forms import BookForm, BookRequestForm, BookNoteForm
from django.http import HttpResponseForbidden

# Create your views here.

def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

@login_required
def create_book(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"{book.title} başarıyla eklendi.")
            return redirect('book_list')
    else:
        form = BookForm()
    
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Yeni Kitap Ekle'})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    notes = book.notes.filter(is_private=False)
    
    if request.user.is_authenticated:
        private_notes = book.notes.filter(user=request.user, is_private=True)
        notes = notes | private_notes
    
    context = {
        'book': book,
        'notes': notes,
    }
    return render(request, 'books/book_detail.html', context)

@login_required
def edit_book(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"{book.title} başarıyla güncellendi.")
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'books/book_form.html', {'form': form, 'title': 'Kitap Düzenle', 'book': book})

@login_required
def delete_book(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f"{book_title} başarıyla silindi.")
        return redirect('book_list')
    
    return render(request, 'books/book_confirm_delete.html', {'book': book})

@login_required
def request_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if not book.is_available:
        messages.error(request, "Bu kitap şu anda uygun değil.")
        return redirect('book_detail', pk=book.pk)
    
    if request.method == 'POST':
        form = BookRequestForm(request.POST)
        if form.is_valid():
            book_request = form.save(commit=False)
            book_request.book = book
            book_request.requester = request.user
            book_request.save()
            messages.success(request, f"{book.title} için talebiniz alındı.")
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookRequestForm()
    
    return render(request, 'books/book_request_form.html', {'form': form, 'book': book})

@login_required
def book_request_list(request):
    if request.user.is_staff:
        requests = BookRequest.objects.all()
    else:
        requests = BookRequest.objects.filter(requester=request.user)
    
    return render(request, 'books/book_request_list.html', {'requests': requests})

@login_required
def respond_to_request(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    book_request = get_object_or_404(BookRequest, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        message = request.POST.get('message', '')
        
        if status in [BookRequest.STATUS_APPROVED, BookRequest.STATUS_REJECTED]:
            book_request.status = status
            book_request.message = message
            book_request.response_at = timezone.now()
            book_request.save()
            
            if status == BookRequest.STATUS_APPROVED:
                book_request.book.is_available = False
                book_request.book.save()
                messages.success(request, f"Kitap talebi onaylandı: {book_request.book.title}")
            else:
                messages.info(request, f"Kitap talebi reddedildi: {book_request.book.title}")
            
            return redirect('book_request_list')
    
    return render(request, 'books/book_request_respond.html', {'book_request': book_request})

@login_required
def add_book_note(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.book = book
            note.user = request.user
            note.save()
            messages.success(request, "Not başarıyla eklendi.")
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookNoteForm()
    
    return render(request, 'books/book_note_form.html', {'form': form, 'book': book})

@login_required
def edit_book_note(request, pk):
    note = get_object_or_404(BookNote, pk=pk)
    
    if note.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    if request.method == 'POST':
        form = BookNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Not başarıyla güncellendi.")
            return redirect('book_detail', pk=note.book.pk)
    else:
        form = BookNoteForm(instance=note)
    
    return render(request, 'books/book_note_form.html', {'form': form, 'book': note.book, 'note': note})

@login_required
def delete_book_note(request, pk):
    note = get_object_or_404(BookNote, pk=pk)
    
    if note.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    book_pk = note.book.pk
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Not başarıyla silindi.")
        return redirect('book_detail', pk=book_pk)
    
    return render(request, 'books/book_note_confirm_delete.html', {'note': note})
