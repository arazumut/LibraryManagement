from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model with additional fields for the Library Management System.
    """
    USER_TYPE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('library_admin', 'Library Admin'),
        ('reader', 'Reader'),
    )
    
    user_type = models.CharField(
        'User Type',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='reader',
        help_text='Designates the type of user account.',
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        
    def __str__(self):
        return self.username
    
    @property
    def is_super_admin(self):
        return self.user_type == 'super_admin'
    
    @property
    def is_library_admin(self):
        return self.user_type == 'library_admin'
    
    @property
    def is_reader(self):
        return self.user_type == 'reader'
