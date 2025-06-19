from django.db import models
from books.models import Book
from django.conf import settings
from django.utils import timezone
import uuid

class BookIdentifier(models.Model):
    """
    Kitaplar için barkod, QR kod ve diğer tanımlayıcıları yönetmek için model.
    """
    IDENTIFIER_TYPE_CHOICES = (
        ('barcode', 'Barkod'),
        ('qrcode', 'QR Kod'),
        ('rfid', 'RFID'),
        ('custom', 'Özel'),
    )
    
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='identifiers')
    identifier_type = models.CharField('Tanımlayıcı Tipi', max_length=20, choices=IDENTIFIER_TYPE_CHOICES)
    value = models.CharField('Değer', max_length=255, unique=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Oluşturan', on_delete=models.SET_NULL, 
                                 blank=True, null=True, related_name='created_identifiers')
    is_active = models.BooleanField('Aktif', default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kitap Tanımlayıcı'
        verbose_name_plural = 'Kitap Tanımlayıcıları'
        
    def __str__(self):
        return f"{self.book.title} - {self.get_identifier_type_display()}: {self.value}"
    
    def save(self, *args, **kwargs):
        # Eğer değer belirtilmemişse, otomatik oluştur
        if not self.value:
            if self.identifier_type == 'barcode':
                # Basit bir barkod oluşturma
                self.value = f"B-{uuid.uuid4().hex[:12].upper()}"
            elif self.identifier_type == 'qrcode':
                # QR kod değeri oluşturma
                self.value = f"QR-{uuid.uuid4().hex[:12].upper()}"
            elif self.identifier_type == 'rfid':
                # RFID değeri oluşturma
                self.value = f"RF-{uuid.uuid4().hex[:12].upper()}"
            else:
                # Özel tanımlayıcı
                self.value = f"C-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

class ScanRecord(models.Model):
    """
    Kitap tarama/okutma kayıtları için model.
    """
    identifier = models.ForeignKey(BookIdentifier, verbose_name='Tanımlayıcı', on_delete=models.CASCADE, 
                                 related_name='scan_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                           related_name='scan_records')
    scan_date = models.DateTimeField('Tarama Tarihi', default=timezone.now)
    location = models.CharField('Konum', max_length=255, blank=True, null=True)
    scan_type = models.CharField('Tarama Tipi', max_length=50, blank=True, null=True)
    notes = models.TextField('Notlar', blank=True, null=True)
    
    class Meta:
        ordering = ['-scan_date']
        verbose_name = 'Tarama Kaydı'
        verbose_name_plural = 'Tarama Kayıtları'
        
    def __str__(self):
        return f"{self.identifier.value} - {self.user.username} - {self.scan_date.strftime('%Y-%m-%d %H:%M')}"
