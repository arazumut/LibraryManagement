class DummyUser:
    """Dummy user for our templates."""
    def __init__(self):
        self.username = 'demo_user'
        self.first_name = 'Demo'
        self.last_name = 'User'
        self.email = 'demo@example.com'
        self.is_authenticated = True
        self.profile_picture = None
        self.pk = None  # Add pk attribute to prevent errors in admin
        self.id = None  # Add id attribute for good measure
        self.user_type = 'reader'  # Default user type
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_super_admin(self):
        return False
    
    @property
    def is_library_admin(self):
        return False
    
    @property
    def is_reader(self):
        return True

def user(request):
    """
    Add user context data for templates.
    Only use DummyUser for anonymous users or when debugging template contexts.
    """
    # Don't override the user in admin contexts
    if request.path.startswith('/admin/'):
        return {}
    
    # Use the real user when authenticated
    if hasattr(request, 'user') and request.user.is_authenticated:
        return {}  # Don't add anything, Django's auth context processor handles this
    
    # For anonymous users, provide a dummy user for template development
    return {'user': DummyUser()}
