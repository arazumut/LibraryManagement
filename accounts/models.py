from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Kütüphane Yönetim Sistemi için ek alanlar içeren Özel Kullanıcı modeli.
    """
    USER_TYPE_CHOICES = (
        ('super_admin', 'Süper Yönetici'),
        ('library_admin', 'Kütüphane Yöneticisi'),
        ('reader', 'Okuyucu'),
    )
    
    user_type = models.CharField(
        'Kullanıcı Tipi',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='reader',
        help_text='Kullanıcı hesabının tipini belirler.',
    )
    profile_picture = models.ImageField('Profil Resmi', upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField('Telefon Numarası', max_length=20, blank=True, null=True)
    address = models.TextField('Adres', blank=True, null=True)
    
    class Meta:
        verbose_name = 'kullanıcı'
        verbose_name_plural = 'kullanıcılar'
        
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
