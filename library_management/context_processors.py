class DummyUser:
    """Dummy user for our templates."""
    def __init__(self):
        self.username = 'demo_user'
        self.first_name = 'Demo'
        self.last_name = 'User'
        self.email = 'demo@example.com'
        self.is_authenticated = True
        self.profile_picture = None
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

def user(request):
    """Add a dummy user to all template contexts."""
    return {'user': DummyUser()}
