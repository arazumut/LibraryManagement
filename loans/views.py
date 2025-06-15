from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Loan
from books.models import Book

@login_required
def loan_list(request):
    loans = Loan.objects.all()
    context = {
        'active_menu': 'loans',
        'loans': loans
    }
    return render(request, 'loans/loan_list.html', context)

@login_required
def my_loans(request):
    my_loans = Loan.objects.filter(borrower=request.user)
    context = {
        'active_menu': 'my_loans',
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
    # Kitabı bul veya 404 hatası döndür
    book = get_object_or_404(Book, id=book_id)
    
    # Kitap ödünç alınabilir durumda mı kontrol et
    if book.status != 'available':
        messages.error(request, "Bu kitap şu anda ödünç alınamaz.")
        return redirect('books:detail', book_id=book_id)
    
    if request.method == "POST":
        # Kitabı ödünç verecek kişi
        # Basit çözüm: İlk kütüphane görevlisi veya admin kullanıcıyı kullanma
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Önce kitabın kütüphanesinin sahibini kullan
        if hasattr(book.library, 'owner') and book.library.owner:
            loaned_by = book.library.owner
        else:
            # Yoksa admin yetkisi olan ilk kullanıcıyı bul
            try:
                loaned_by = User.objects.filter(is_staff=True).first()
            except User.DoesNotExist:
                # Yetkili bulunamadı
                loaned_by = request.user
        
        # Notları al
        notes = request.POST.get('notes', '')
        
        # Yeni ödünç verme kaydı oluştur
        loan = Loan(
            book=book,
            borrower=request.user,
            loaned_by=loaned_by,
            notes=notes
        )
        loan.save()
        
        messages.success(request, f"{book.title} kitabını başarıyla ödünç aldınız. Son iade tarihi: {loan.due_date.strftime('%d.%m.%Y')}")
        return redirect('loans:my_loans')
    
    # GET istekleri için book detail sayfasına yönlendir
    return redirect('books:detail', book_id=book_id)

@login_required
def return_book(request, loan_id):
    # Get the loan or return 404 if not found
    loan = get_object_or_404(Loan, id=loan_id)
    
    # Check if the current user is the borrower
    if loan.borrower != request.user:
        messages.error(request, "Bu işlem için yetkiniz bulunmuyor.")
        return redirect('loans:my_loans')
    
    # Check if loan is active
    if loan.status != 'active':
        messages.warning(request, "Bu ödünç zaten iade edilmiş.")
        return redirect('loans:my_loans')
    
    # Update loan status and return date
    loan.status = 'returned'
    loan.return_date = timezone.now()
    loan.save()
    
    # Update book status
    book = loan.book
    book.status = 'available'
    book.save()
    
    messages.success(request, f"{book.title} başarıyla iade edildi.")
    return redirect('loans:my_loans')
