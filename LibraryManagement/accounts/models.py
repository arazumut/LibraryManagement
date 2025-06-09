from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Kullanıcı tipleri için sabitler
    SUPER_ADMIN = 'SUPER_ADMIN'
    LIBRARY_ADMIN = 'LIBRARY_ADMIN'
    READER = 'READER'
    
    USER_TYPE_CHOICES = [
        (SUPER_ADMIN, 'Süper Admin'),
        (LIBRARY_ADMIN, 'Kütüphane Yöneticisi'),
        (READER, 'Okuyucu'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=READER,
    )
    
    def is_super_admin(self):
        return self.user_type == self.SUPER_ADMIN
    
    def is_library_admin(self):
        return self.user_type == self.LIBRARY_ADMIN
    
    def is_reader(self):
        return self.user_type == self.READER
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
