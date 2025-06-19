from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    """
    Kullanıcı bildirimleri için genel model.
    """
    NOTIFICATION_TYPES = (
        ('loan_due', 'Ödünç Alma Süresi Yaklaşıyor'),
        ('loan_overdue', 'Ödünç Alma Süresi Geçti'),
        ('book_available', 'Kitap Müsait'),
        ('book_reserved', 'Kitap Rezerve Edildi'),
        ('request_approved', 'İstek Onaylandı'),
        ('request_rejected', 'İstek Reddedildi'),
        ('new_book', 'Yeni Kitap Eklendi'),
        ('review_liked', 'Değerlendirmeniz Beğenildi'),
        ('comment_received', 'Yorumunuza Yanıt Geldi'),
        ('system', 'Sistem Bildirimi'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Alıcı',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField('Bildirim Tipi', max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField('Başlık', max_length=255)
    message = models.TextField('Mesaj')
    created_at = models.DateTimeField('Oluşturulma Tarihi', default=timezone.now)
    is_read = models.BooleanField('Okundu', default=False)
    read_at = models.DateTimeField('Okunma Tarihi', blank=True, null=True)
    
    # İlişkili içerik için generic ilişki
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # İsteğe bağlı bağlantı
    link = models.CharField('Bağlantı', max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'
        
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Bildirimi okundu olarak işaretle."""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
        
    @property
    def notification_icon(self):
        """Return the appropriate icon for notification type."""
        icon_map = {
            'loan_due': 'clock',
            'loan_overdue': 'exclamation-triangle',
            'book_available': 'check-circle',
            'book_reserved': 'bookmark',
            'request_approved': 'thumbs-up',
            'request_rejected': 'thumbs-down',
            'new_book': 'book',
            'review_liked': 'heart',
            'comment_received': 'comment',
            'system': 'bell'
        }
        return icon_map.get(self.notification_type, 'bell')
        
    @property
    def notification_color(self):
        """Return the appropriate color class for notification type."""
        color_map = {
            'loan_due': 'warning',
            'loan_overdue': 'danger',
            'book_available': 'success',
            'book_reserved': 'info',
            'request_approved': 'success',
            'request_rejected': 'secondary',
            'new_book': 'primary',
            'review_liked': 'pink',
            'comment_received': 'info',
            'system': 'dark'
        }
        return color_map.get(self.notification_type, 'primary')
