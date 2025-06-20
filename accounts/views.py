from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Lütfen kullanıcı adı ve şifre giriniz.')
            return render(request, 'accounts/login.html')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Kullanıcı hesabı aktif mi kontrol et
            if not user.is_active:
                messages.warning(request, 'Hesabınız henüz aktif değil. Lütfen yönetici onayını bekleyin.')
                return redirect('accounts:inactive_account')
                
            login(request, user)
            
            # Giriş başarılı olduğunda, son giriş tarihini güncelle
            user.last_login = timezone.now()
            user.save()
            
            # Başarılı giriş bildirimi
            messages.success(request, f'Hoş geldiniz, {user.first_name if user.first_name else user.username}!')
            
            # Kullanıcıyı yönlendir
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre')
    
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
                # Yeni kullanıcıları varsayılan olarak devre dışı bırak (onay gerekli)
                user.is_active = False
                user.save()
                
                # Bildirim oluştur
                from .models_notification import Notification
                # Tüm süper yöneticilere bildirim gönder
                for admin in User.objects.filter(user_type='super_admin'):
                    Notification.objects.create(
                        recipient=admin,
                        title='Yeni Kullanıcı Kaydı',
                        message=f'{username} adlı yeni bir kullanıcı kaydoldu ve onay bekliyor.',
                        notification_type='user_registration',
                        link='/admin/accounts/user/'
                    )
                
                messages.success(request, 'Hesabınız başarıyla oluşturuldu! Hesabınız yönetici onayı bekliyor. Onaylandıktan sonra giriş yapabileceksiniz.')
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Kayıt sırasında bir hata oluştu: {str(e)}')
    
    return render(request, 'accounts/register.html')

@login_required
def profile(request):
    """
    Display the profile page for the logged-in user
    """
    # Get additional stats
    from loans.models import Loan
    active_loans = Loan.objects.filter(
        borrower=request.user, 
        status__in=['active', 'overdue']
    ).count()
    
    try:
        # Try to get review count if the model exists
        from books.models_review import Review
        review_count = Review.objects.filter(user=request.user).count()
    except ImportError:
        review_count = 0
    
    context = {
        'active_loans': active_loans,
        'review_count': review_count,
        'active_menu': 'profile',
    }
    
    return render(request, 'accounts/profile.html', context)

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

def inactive_account(request):
    """
    Hesabı henüz aktif olmayan kullanıcılar için bilgilendirme sayfası
    """
    return render(request, 'accounts/inactive_account.html')

@login_required
def admin_user_management(request):
    """
    Kullanıcı yönetim sayfası - Yalnızca süper yöneticiler erişebilir
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Kullanıcıları listele
    users = User.objects.all().order_by('-date_joined')
    
    # Kullanıcı aktivasyon işlemi
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if user_id and action:
            try:
                user = User.objects.get(id=user_id)
                
                if action == 'activate':
                    user.is_active = True
                    user.save()
                    messages.success(request, f"{user.username} kullanıcısı başarıyla aktifleştirildi.")
                    
                    # Bildirim gönder
                    from accounts.models_notification import Notification
                    Notification.objects.create(
                        recipient=user,
                        title='Hesabınız Aktifleştirildi',
                        message='Hesabınız yönetici tarafından onaylandı. Artık tüm özelliklere erişebilirsiniz.',
                        notification_type='account_activated'
                    )
                    
                elif action == 'deactivate':
                    user.is_active = False
                    user.save()
                    messages.success(request, f"{user.username} kullanıcısı başarıyla devre dışı bırakıldı.")
                
                elif action == 'promote_to_admin':
                    user.user_type = 'library_admin'
                    user.save()
                    messages.success(request, f"{user.username} kullanıcısı kütüphane yöneticisi olarak atandı.")
                
                elif action == 'demote_to_reader':
                    user.user_type = 'reader'
                    user.save()
                    messages.success(request, f"{user.username} kullanıcısı okuyucu olarak atandı.")
                    
            except User.DoesNotExist:
                messages.error(request, "Belirtilen kullanıcı bulunamadı.")
    
    context = {
        'active_menu': 'admin_users',
        'users': users
    }
    
    return render(request, 'accounts/admin_user_management.html', context)

@login_required
def edit_profile(request):
    """
    Allow users to edit their profile information
    """
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        
        # Update user profile
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.address = address
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
        return redirect('accounts:profile')
    
    context = {
        'active_menu': 'profile',
    }
    
    return render(request, 'accounts/edit_profile.html', context)
