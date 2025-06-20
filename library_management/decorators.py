from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def login_required(view_func):
    """Simple login_required decorator for our example."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Bu sayfaya erişmek için giriş yapmalısınız.')
        return redirect('accounts:login')
    return wrapped_view

def user_is_library_admin(view_func):
    """Kullanıcının kütüphane yöneticisi olup olmadığını kontrol eden dekoratör."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_library_admin or request.user.is_super_admin):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Bu işlemi yapmak için kütüphane yöneticisi olmalısınız.')
        return redirect('dashboard')
    return wrapped_view

def user_is_super_admin(view_func):
    """Kullanıcının süper yönetici olup olmadığını kontrol eden dekoratör."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_super_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Bu işlemi yapmak için süper yönetici olmalısınız.')
        return redirect('dashboard')
    return wrapped_view

def check_account_activation(view_func):
    """Kullanıcı hesabının aktif olup olmadığını kontrol eden dekoratör."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_active:
                messages.warning(request, 'Hesabınız henüz aktif değil. Lütfen e-posta adresinizi kontrol edin veya yönetici ile iletişime geçin.')
                return redirect('accounts:inactive_account')
            return view_func(request, *args, **kwargs)
        return redirect('accounts:login')
    return wrapped_view
