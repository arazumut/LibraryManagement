from django.db import models
from books.models import Book
from django.conf import settings
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files import File

class BookIdentifier(models.Model):
    """
    Kitaplar için barkod, QR kod ve diğer tanımlayıcıları yönetmek için model.
    """
    IDENTIFIER_TYPE_CHOICES = (
        ('barcode', 'Barkod'),
        ('qrcode', 'QR Kod'),
        ('rfid', 'RFID'),
        ('isbn', 'ISBN'),
        ('custom', 'Özel'),
    )
    
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='identifiers')
    identifier_type = models.CharField('Tanımlayıcı Tipi', max_length=20, choices=IDENTIFIER_TYPE_CHOICES)
    value = models.CharField('Değer', max_length=255, unique=True)
    qr_code_image = models.ImageField('QR Kod Resmi', upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Oluşturan', on_delete=models.SET_NULL, 
                                 blank=True, null=True, related_name='created_identifiers')
    is_active = models.BooleanField('Aktif', default=True)
    metadata = models.JSONField('Ek Bilgiler', blank=True, null=True, default=dict)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kitap Tanımlayıcı'
        verbose_name_plural = 'Kitap Tanımlayıcıları'
        
    def __str__(self):
        return f"{self.book.title} - {self.get_identifier_type_display()}: {self.value}"
    
    def generate_qr_code(self):
        """QR kod resmi oluştur."""
        if self.identifier_type == 'qrcode':
            qr_data = {
                'book_id': str(self.book.id),
                'identifier': self.value,
                'type': 'book',
                'library_id': str(self.book.library.id)
            }
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(str(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            filename = f'qr_code_{self.value}.png'
            self.qr_code_image.save(filename, File(buffer), save=False)
    
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
            elif self.identifier_type == 'isbn':
                # ISBN kullan eğer varsa
                if hasattr(self.book, 'isbn') and self.book.isbn:
                    self.value = self.book.isbn
                else:
                    self.value = f"ISBN-{uuid.uuid4().hex[:10].upper()}"
            else:
                # Özel tanımlayıcı
                self.value = f"C-{uuid.uuid4().hex[:12].upper()}"
        
        super().save(*args, **kwargs)
        
        # QR kod resmi oluştur
        if self.identifier_type == 'qrcode' and not self.qr_code_image:
            self.generate_qr_code()
            super().save(update_fields=['qr_code_image'])

class ScanRecord(models.Model):
    """
    Kitap tarama/okutma kayıtları için model.
    """
    SCAN_ACTION_CHOICES = (
        ('view', 'Görüntüleme'),
        ('borrow', 'Ödünç Alma'),
        ('return', 'İade'),
        ('inventory', 'Envanter'),
        ('location_check', 'Konum Kontrolü'),
    )
    
    identifier = models.ForeignKey(BookIdentifier, verbose_name='Tanımlayıcı', on_delete=models.CASCADE, 
                                 related_name='scan_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                           related_name='scan_records')
    scan_date = models.DateTimeField('Tarama Tarihi', default=timezone.now)
    location = models.CharField('Konum', max_length=255, blank=True, null=True)
    scan_action = models.CharField('Tarama Eylemi', max_length=50, choices=SCAN_ACTION_CHOICES, default='view')
    ip_address = models.GenericIPAddressField('IP Adresi', blank=True, null=True)
    user_agent = models.TextField('User Agent', blank=True, null=True)
    notes = models.TextField('Notlar', blank=True, null=True)
    
    class Meta:
        ordering = ['-scan_date']
        verbose_name = 'Tarama Kaydı'
        verbose_name_plural = 'Tarama Kayıtları'
        
    def __str__(self):
        return f"{self.identifier.value} - {self.user.username} - {self.scan_date.strftime('%Y-%m-%d %H:%M')}"


class BookLocation(models.Model):
    """
    Kitapların fiziksel konumunu takip etmek için model.
    """
    book = models.OneToOneField(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='location')
    shelf_code = models.CharField('Raf Kodu', max_length=50, blank=True, null=True)
    section = models.CharField('Bölüm', max_length=100, blank=True, null=True)
    floor = models.CharField('Kat', max_length=50, blank=True, null=True)
    coordinates = models.CharField('Koordinatlar', max_length=100, blank=True, null=True, 
                                  help_text='x,y formatında koordinat bilgisi')
    last_seen_date = models.DateTimeField('Son Görülme Tarihi', default=timezone.now)
    last_seen_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Son Gören', 
                                   on_delete=models.SET_NULL, blank=True, null=True)
    notes = models.TextField('Notlar', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Kitap Konumu'
        verbose_name_plural = 'Kitap Konumları'
        
    def __str__(self):
        location_parts = [self.shelf_code, self.section, self.floor]
        location_str = ' - '.join([part for part in location_parts if part])
        return f"{self.book.title}: {location_str}" if location_str else self.book.title
    
    def update_location(self, user, **kwargs):
        """Konum bilgilerini güncelle."""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.last_seen_date = timezone.now()
        self.last_seen_by = user
        self.save()
