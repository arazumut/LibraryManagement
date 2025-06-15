from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def register(request):
    # Registration logic here
    return render(request, 'accounts/register.html')

def profile(request):
    # Profile logic here
    return render(request, 'accounts/profile.html')

def my_books(request):
    from loans.models import Loan
    
    # Get all books borrowed by the current user
    active_loans = Loan.objects.filter(
        borrower=request.user, 
        status__in=['active', 'overdue']
    ).select_related('book', 'book__library')
    
    past_loans = Loan.objects.filter(
        borrower=request.user,
        status='returned'
    ).select_related('book', 'book__library')
    
    context = {
        'active_loans': active_loans,
        'past_loans': past_loans
    }
    
    return render(request, 'accounts/my_books.html', context)

def user_list(request):
    # User list logic here
    return render(request, 'accounts/user_list.html')
