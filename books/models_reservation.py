from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone

class BookReservation(models.Model):
    """
    Kitap rezervasyon sistemi için model.
    """
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('notified', 'Bildirim Gönderildi'),
        ('fulfilled', 'Tamamlandı'),
        ('expired', 'Süresi Doldu'),
        ('cancelled', 'İptal Edildi'),
    )
    
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Rezerve Eden', on_delete=models.CASCADE, related_name='book_reservations')
    reservation_date = models.DateTimeField('Rezervasyon Tarihi', default=timezone.now)
    notification_date = models.DateTimeField('Bildirim Tarihi', blank=True, null=True)
    expiry_date = models.DateTimeField('Son Geçerlilik Tarihi', blank=True, null=True)
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField('Notlar', blank=True, null=True)
    
    class Meta:
        ordering = ['reservation_date']
        verbose_name = 'Kitap Rezervasyonu'
        verbose_name_plural = 'Kitap Rezervasyonları'
        
    def __str__(self):
        return f"{self.book.title} kitabı {self.user.username} tarafından rezerve edildi"
    
    def notify_available(self):
        """Kitap müsait olduğunda kullanıcıya bildirim gönder."""
        self.status = 'notified'
        self.notification_date = timezone.now()
        # Bildirim gönderildikten sonra 48 saat içinde alınmazsa rezervasyon sona erer
        self.expiry_date = self.notification_date + timezone.timedelta(days=2)
        self.save()
        
    def cancel(self):
        """Rezervasyonu iptal et."""
        self.status = 'cancelled'
        self.save()
        
    def fulfill(self):
        """Rezervasyon tamamlandı (kitap ödünç alındı)."""
        self.status = 'fulfilled'
        self.save()
        
    def expire(self):
        """Rezervasyon süresi doldu."""
        self.status = 'expired'
        self.save()
        
    @property
    def is_active(self):
        """Rezervasyon hala aktif mi?"""
        return self.status in ['pending', 'notified']
        
    @property
    def status_color(self):
        """Return the appropriate color class for the status badge."""
        color_map = {
            'pending': 'primary',
            'notified': 'warning',
            'fulfilled': 'success',
            'expired': 'danger',
            'cancelled': 'secondary'
        }
        return color_map.get(self.status, 'primary')
