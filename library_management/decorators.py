from functools import wraps
from django.shortcuts import redirect

def login_required(view_func):
    """Simple login_required decorator for our example."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect('accounts:login')
    return wrapped_view
