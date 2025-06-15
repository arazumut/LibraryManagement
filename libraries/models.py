from django.db import models
from django.conf import settings

class Library(models.Model):
    """
    Sistemdeki kütüphaneleri yönetmek için model.
    """
    name = models.CharField('Adı', max_length=255)
    description = models.TextField('Açıklama', blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Sahibi',
        on_delete=models.CASCADE,
        related_name='owned_libraries'
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Yöneticiler',
        related_name='administered_libraries',
        blank=True
    )
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    address = models.TextField('Adres', blank=True, null=True)
    phone = models.CharField('Telefon', max_length=20, blank=True, null=True)
    email = models.EmailField('E-posta', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Kütüphane'
        verbose_name_plural = 'Kütüphaneler'
        ordering = ['name']
    
    def __str__(self):
        return self.name
