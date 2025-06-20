from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

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
    if request.method == 'POST':
        # Form validasyonu ve kullanıcı kaydı
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        terms = request.POST.get('terms')
        
        # Temel validasyonlar
        error = False
        
        # Tüm gerekli alanların doldurulduğunu kontrol et
        if not (username and email and password and password_confirmation):
            messages.error(request, 'Lütfen tüm zorunlu alanları doldurun.')
            error = True
        
        # Kullanıcı adının benzersiz olduğunu kontrol et
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten kullanımda. Lütfen başka bir kullanıcı adı seçin.')
            error = True
            
        # E-posta adresinin benzersiz olduğunu kontrol et
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanımda. Lütfen başka bir e-posta adresi kullanın.')
            error = True
            
        # Şifrelerin eşleştiğini kontrol et
        if password != password_confirmation:
            messages.error(request, 'Şifreler eşleşmiyor. Lütfen tekrar deneyin.')
            error = True
            
        # Şifre uzunluğunu kontrol et
        if len(password) < 8:
            messages.error(request, 'Şifreniz en az 8 karakter uzunluğunda olmalıdır.')
            error = True
            
        # Şartlar ve koşulların kabul edildiğini kontrol et
        if not terms:
            messages.error(request, 'Kayıt olmak için şartlar ve koşulları kabul etmelisiniz.')
            error = True
            
        # Hata yoksa, kullanıcıyı oluştur
        if not error:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                messages.success(request, 'Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Kayıt sırasında bir hata oluştu: {str(e)}')
    
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

def notification_list(request):
    """
    Display all notifications for the current user
    """
    from .models_notification import Notification
    
    # Mark all as read if requested
    if request.GET.get('mark_all_read'):
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        for notification in unread_notifications:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        messages.success(request, 'All notifications marked as read.')
        return redirect('accounts:notification_list')
    
    # Mark single notification as read
    if notification_id := request.GET.get('mark_read'):
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            messages.success(request, 'Notification marked as read.')
            
            # Redirect to the notification's link if available
            if notification.link:
                return redirect(notification.link)
        except Notification.DoesNotExist:
            messages.error(request, 'Notification not found.')
    
    # Get all notifications for the current user
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'active_menu': 'notifications',
    }
    
    return render(request, 'accounts/notification_list.html', context)

@login_required
def social_feed(request):
    """
    Display social feed with user interactions, reviews, and activities
    """
    from books.models_review import BookReview
    from .models import User
    
    # Get recent book reviews from all users
    recent_reviews = BookReview.objects.select_related(
        'user', 'book'
    ).order_by('-created_at')[:20]
    
    # Get active users
    active_users = User.objects.filter(
        is_active=True
    ).order_by('-last_login')[:10]
    
    context = {
        'recent_reviews': recent_reviews,
        'active_users': active_users,
        'active_menu': 'social',
    }
    
    return render(request, 'accounts/social_feed.html', context)
