from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class APIKey(models.Model):
    """
    API erişim anahtarları için model.
    """
    KEY_TYPE_CHOICES = (
        ('read', 'Sadece Okuma'),
        ('write', 'Okuma/Yazma'),
        ('full', 'Tam Erişim'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                           related_name='api_keys')
    name = models.CharField('Anahtar Adı', max_length=255)
    key = models.CharField('API Anahtarı', max_length=255, unique=True)
    key_type = models.CharField('Anahtar Tipi', max_length=20, choices=KEY_TYPE_CHOICES, default='read')
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    expires_at = models.DateTimeField('Geçerlilik Sonu', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Anahtarı'
        verbose_name_plural = 'API Anahtarları'
        
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.key:
            # Yeni API anahtarı oluştur
            self.key = uuid.uuid4().hex
        super().save(*args, **kwargs)
    
    def revoke(self):
        """API anahtarını iptal et."""
        self.is_active = False
        self.save()
    
    @property
    def is_expired(self):
        """API anahtarının süresi dolmuş mu?"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_valid(self):
        """API anahtarı geçerli mi?"""
        return self.is_active and not self.is_expired

class APIRequest(models.Model):
    """
    API isteklerini kaydetmek ve izlemek için model.
    """
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    )
    
    api_key = models.ForeignKey(APIKey, verbose_name='API Anahtarı', on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.SET_NULL, 
                           null=True, blank=True, related_name='api_requests')
    endpoint = models.CharField('Endpoint', max_length=255)
    method = models.CharField('HTTP Metodu', max_length=10, choices=METHOD_CHOICES)
    request_data = models.JSONField('İstek Verisi', blank=True, null=True)
    response_code = models.PositiveIntegerField('Yanıt Kodu')
    response_time_ms = models.PositiveIntegerField('Yanıt Süresi (ms)')
    ip_address = models.GenericIPAddressField('IP Adresi', blank=True, null=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    created_at = models.DateTimeField('İstek Tarihi', default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API İsteği'
        verbose_name_plural = 'API İstekleri'
        
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.response_code} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
