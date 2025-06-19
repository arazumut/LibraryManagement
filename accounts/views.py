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
