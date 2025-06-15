from django.db import models
from django.conf import settings
from libraries.models import Library

class Book(models.Model):
    """
    Kütüphane sistemindeki kitapları temsil eden model.
    """
    STATUS_CHOICES = (
        ('available', 'Mevcut'),
        ('borrowed', 'Ödünç Verilmiş'),
        ('reserved', 'Rezerve Edilmiş'),
        ('maintenance', 'Bakımda'),
    )
    
    title = models.CharField('Başlık', max_length=255)
    author = models.CharField('Yazar', max_length=255)
    isbn = models.CharField('ISBN', max_length=20, blank=True, null=True)
    description = models.TextField('Açıklama', blank=True, null=True)
    cover_image = models.ImageField('Kapak Resmi', upload_to='book_covers/', blank=True, null=True)
    library = models.ForeignKey(Library, verbose_name='Kütüphane', on_delete=models.CASCADE, related_name='books')
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='available')
    publication_year = models.PositiveIntegerField('Yayın Yılı', blank=True, null=True)
    publisher = models.CharField('Yayınevi', max_length=255, blank=True, null=True)
    language = models.CharField('Dil', max_length=50, blank=True, null=True)
    pages = models.PositiveIntegerField('Sayfa Sayısı', blank=True, null=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        ordering = ['title', 'author']
        verbose_name = 'Kitap'
        verbose_name_plural = 'Kitaplar'
        
    def __str__(self):
        return f"{self.title} - {self.author}"
        
    @property
    def status_color(self):
        """Return the appropriate color class for the status badge."""
        color_map = {
            'available': 'success',
            'borrowed': 'warning',
            'reserved': 'primary',
            'maintenance': 'danger'
        }
        return color_map.get(self.status, 'primary')
        
    @property
    def loan_count(self):
        """Return the number of times this book has been loaned."""
        return self.loans.count()

class BookRequest(models.Model):
    """
    Kullanıcılar arası kitap isteklerini yönetmek için model.
    """
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
        ('cancelled', 'İptal Edildi'),
    )
    
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='İstekte Bulunan', on_delete=models.CASCADE, related_name='book_requests')
    message = models.TextField('Mesaj', blank=True, null=True)
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField('İstek Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    response_message = models.TextField('Yanıt Mesajı', blank=True, null=True)
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Kitap İsteği'
        verbose_name_plural = 'Kitap İstekleri'
        
    def __str__(self):
        return f"{self.book.title} için {self.requester.username} tarafından istek - {self.get_status_display()}"

class BookNote(models.Model):
    """
    Kullanıcıların kitaplar hakkında kişisel notları için model.
    """
    VISIBILITY_CHOICES = (
        ('private', 'Özel'),
        ('public', 'Herkese Açık'),
    )
    
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, related_name='book_notes')
    note = models.TextField('Not')
    visibility = models.CharField('Görünürlük', max_length=10, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Kitap Notu'
        verbose_name_plural = 'Kitap Notları'
        
    def __str__(self):
        return f"{self.book.title} hakkında {self.user.username} tarafından not"
