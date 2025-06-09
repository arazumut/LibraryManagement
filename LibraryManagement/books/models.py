from django.db import models
from libraries.models import Library
from django.conf import settings

class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Kitap Adı")
    author = models.CharField(max_length=255, verbose_name="Yazar")
    isbn = models.CharField(max_length=13, blank=True, null=True, verbose_name="ISBN")
    library = models.ForeignKey(
        Library, 
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Kütüphane"
    )
    is_available = models.BooleanField(default=True, verbose_name="Uygunluk Durumu")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name="Kapak Resmi")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Kitap"
        verbose_name_plural = "Kitaplar"
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} - {self.author} ({self.library.name})"


class BookRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Beklemede'),
        (STATUS_APPROVED, 'Onaylandı'),
        (STATUS_REJECTED, 'Reddedildi'),
        (STATUS_CANCELLED, 'İptal Edildi'),
    ]
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name="Kitap"
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_requests',
        verbose_name="İsteyen"
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="İstek Tarihi")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Durum"
    )
    response_at = models.DateTimeField(blank=True, null=True, verbose_name="Yanıt Tarihi")
    message = models.TextField(blank=True, null=True, verbose_name="Mesaj")
    
    class Meta:
        verbose_name = "Kitap İsteği"
        verbose_name_plural = "Kitap İstekleri"
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.requester.username} - {self.book.title} ({self.get_status_display()})"


class BookNote(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="Kitap"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_notes',
        verbose_name="Kullanıcı"
    )
    content = models.TextField(verbose_name="Not İçeriği")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    is_private = models.BooleanField(default=False, verbose_name="Özel Not")
    
    class Meta:
        verbose_name = "Kitap Notu"
        verbose_name_plural = "Kitap Notları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.book.title} - Not ({self.user.username})"
