from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from books.models import Book, BookRequest
from loans.models import Loan
from libraries.models import Library
from .forms import UserRegisterForm, UserUpdateForm
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username} hesabı başarıyla oluşturuldu! Giriş yapabilirsiniz.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    # Kullanıcının kütüphaneleri
    user_libraries = Library.objects.filter(owner=request.user)
    
    # Kullanıcının ödünç aldığı kitaplar
    borrowed_books = Loan.objects.filter(borrower=request.user, returned_date__isnull=True)
    
    # Kullanıcının ödünç verdiği kitaplar
    lent_books = Loan.objects.filter(lender=request.user, returned_date__isnull=True)
    
    # Kullanıcının kitap istekleri
    book_requests = BookRequest.objects.filter(requester=request.user)
    
    # Kullanıcının kütüphanesindeki kitaplara gelen istekler (sadece kütüphane yöneticileri için)
    if request.user.is_library_admin() or request.user.is_super_admin():
        incoming_requests = BookRequest.objects.filter(
            book__library__owner=request.user,
            status=BookRequest.STATUS_PENDING
        )
    else:
        incoming_requests = None
    
    # Gecikmiş kitaplar
    overdue_books = Loan.objects.filter(borrower=request.user, returned_date__isnull=True).filter(due_date__lt=timezone.now())
    
    context = {
        'user_libraries': user_libraries,
        'borrowed_books': borrowed_books,
        'lent_books': lent_books,
        'book_requests': book_requests,
        'incoming_requests': incoming_requests,
        'overdue_books': overdue_books,
    }
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    # Kullanıcının istatistiklerini hesapla
    borrowed_count = Loan.objects.filter(borrower=request.user).count()
    lent_count = Loan.objects.filter(lender=request.user).count()
    book_requests_count = BookRequest.objects.filter(requester=request.user).count()
    
    if request.user.is_library_admin() or request.user.is_super_admin():
        libraries_count = Library.objects.filter(owner=request.user).count()
    else:
        libraries_count = 0
    
    context = {
        'borrowed_count': borrowed_count,
        'lent_count': lent_count,
        'book_requests_count': book_requests_count,
        'libraries_count': libraries_count,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})
