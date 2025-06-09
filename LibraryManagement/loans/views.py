from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Loan
from books.models import Book
from .forms import LoanForm
from django.http import HttpResponseForbidden
from django.db.models import Q

# Create your views here.

@login_required
def loan_list(request):
    """Tüm ödünç işlemlerini listele (personel için)"""
    if not request.user.is_staff:
        return redirect('borrowed_books')
    
    loans = Loan.objects.all()
    
    # Filtreler
    status = request.GET.get('status')
    if status == 'active':
        loans = loans.filter(returned_date__isnull=True)
    elif status == 'returned':
        loans = loans.filter(returned_date__isnull=False)
    elif status == 'overdue':
        loans = loans.filter(returned_date__isnull=True, due_date__lt=timezone.now())
        
    return render(request, 'loans/loan_list.html', {'loans': loans})

@login_required
def create_loan(request):
    """Yeni bir ödünç işlemi oluştur (sadece personel)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.lender = request.user
            
            # Kitap uygun mu kontrol et
            if not loan.book.is_available:
                messages.error(request, "Bu kitap şu anda uygun değil.")
                return redirect('create_loan')
            
            loan.save()
            messages.success(request, f"{loan.book.title} başarıyla {loan.borrower.username} kullanıcısına ödünç verildi.")
            return redirect('loan_detail', pk=loan.pk)
    else:
        form = LoanForm()
    
    return render(request, 'loans/loan_form.html', {'form': form})

@login_required
def loan_detail(request, pk):
    """Ödünç detaylarını görüntüle"""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Sadece personel veya ödünç alan kişi görebilir
    if not request.user.is_staff and request.user != loan.borrower:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    return render(request, 'loans/loan_detail.html', {'loan': loan})

@login_required
def return_book(request, pk):
    """Kitap iade işlemi"""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Sadece personel veya ödünç alan kişi iade edebilir
    if not request.user.is_staff and request.user != loan.borrower:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    # Zaten iade edilmiş mi kontrol et
    if loan.is_returned:
        messages.warning(request, "Bu kitap zaten iade edilmiş.")
        return redirect('loan_detail', pk=loan.pk)
    
    if request.method == 'POST':
        loan.return_book()
        messages.success(request, f"{loan.book.title} başarıyla iade edildi.")
        
        if request.user.is_staff:
            return redirect('loan_list')
        else:
            return redirect('borrowed_books')
    
    return render(request, 'loans/return_book.html', {'loan': loan})

@login_required
def borrowed_books(request):
    """Kullanıcının ödünç aldığı kitapları listele"""
    loans = Loan.objects.filter(borrower=request.user)
    
    # Filtreler
    status = request.GET.get('status')
    if status == 'active':
        loans = loans.filter(returned_date__isnull=True)
    elif status == 'returned':
        loans = loans.filter(returned_date__isnull=False)
    elif status == 'overdue':
        loans = loans.filter(returned_date__isnull=True, due_date__lt=timezone.now())
    
    return render(request, 'loans/borrowed_books.html', {'loans': loans})

@login_required
def lent_books(request):
    """Kullanıcının ödünç verdiği kitapları listele (personel için)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    loans = Loan.objects.filter(lender=request.user)
    
    # Filtreler
    status = request.GET.get('status')
    if status == 'active':
        loans = loans.filter(returned_date__isnull=True)
    elif status == 'returned':
        loans = loans.filter(returned_date__isnull=False)
    elif status == 'overdue':
        loans = loans.filter(returned_date__isnull=True, due_date__lt=timezone.now())
    
    return render(request, 'loans/lent_books.html', {'loans': loans})

@login_required
def overdue_books(request):
    """Süresi geçmiş kitapları listele (personel için)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Bu işlem için yetkiniz bulunmamaktadır.")
    
    loans = Loan.objects.filter(
        returned_date__isnull=True,
        due_date__lt=timezone.now()
    )
    
    return render(request, 'loans/overdue_books.html', {'loans': loans})
