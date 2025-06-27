from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone
import uuid

class BookCollection(models.Model):
    """
    Kullanıcıların kendi kitap koleksiyonlarını oluşturması için model.
    """
    VISIBILITY_CHOICES = (
        ('public', 'Herkese Açık'),
        ('private', 'Özel'),
        ('friends', 'Sadece Arkadaşlar'),
    )
    
    COLLECTION_TYPES = (
        ('reading_list', 'Okunacaklar Listesi'),
        ('favorites', 'Favoriler'),
        ('completed', 'Okunanlar'),
        ('custom', 'Özel Koleksiyon'),
        ('wishlist', 'İstek Listesi'),
        ('recommendations', 'Öneriler'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Koleksiyon Adı', max_length=255)
    description = models.TextField('Açıklama', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Oluşturan', on_delete=models.CASCADE, related_name='book_collections')
    books = models.ManyToManyField(Book, verbose_name='Kitaplar', related_name='collections', through='BookCollectionItem')
    collection_type = models.CharField('Koleksiyon Türü', max_length=20, choices=COLLECTION_TYPES, default='custom')
    visibility = models.CharField('Görünürlük', max_length=20, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField('Oluşturulma Tarihi', default=timezone.now)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    is_featured = models.BooleanField('Öne Çıkan', default=False)
    cover_image = models.ImageField('Kapak Resmi', upload_to='collection_covers/', blank=True, null=True)
    tags = models.JSONField('Etiketler', blank=True, null=True, default=list)
    color_theme = models.CharField('Renk Teması', max_length=7, default='#007bff')  # Hex color
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kitap Koleksiyonu'
        verbose_name_plural = 'Kitap Koleksiyonları'
        
    def __str__(self):
        return f"{self.name} - {self.owner.username}"
    
    @property
    def book_count(self):
        """Koleksiyondaki kitap sayısını döndürür."""
        return self.books.count()
    
    @property
    def is_public(self):
        """Koleksiyon herkese açık mı?"""
        return self.visibility == 'public'
        
    @property
    def is_private(self):
        """Koleksiyon özel mi?"""
        return self.visibility == 'private'
        
    @property
    def visibility_icon(self):
        """Return the appropriate icon for visibility status."""
        icon_map = {
            'public': 'globe',
            'private': 'lock',
            'friends': 'users'
        }
        return icon_map.get(self.visibility, 'question')
    
    @property
    def total_pages(self):
        """Koleksiyondaki toplam sayfa sayısı."""
        return sum([book.pages for book in self.books.all() if book.pages])
    
    @property
    def completed_books_count(self):
        """Tamamlanan kitap sayısı."""
        return self.bookcollectionitem_set.filter(reading_status='completed').count()
    
    @property
    def reading_progress(self):
        """Genel okuma ilerlemesi yüzdesi."""
        total_books = self.book_count
        if total_books == 0:
            return 0
        completed = self.completed_books_count
        return int((completed / total_books) * 100)
    
    def can_view(self, user):
        """Kullanıcı bu koleksiyonu görüntüleyebilir mi?"""
        if self.owner == user:
            return True
        if self.visibility == 'public':
            return True
        if self.visibility == 'friends':
            # TODO: Arkadaşlık sistemi eklendiğinde burayı güncelleyeceğiz
            return True
        return False
        
class BookCollectionItem(models.Model):
    """
    Koleksiyonlardaki kitap öğeleri için ara model.
    """
    collection = models.ForeignKey(BookCollection, verbose_name='Koleksiyon', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE)
    added_at = models.DateTimeField('Eklenme Tarihi', default=timezone.now)
    notes = models.TextField('Notlar', blank=True, null=True)
    order = models.PositiveIntegerField('Sıra', default=0)
    rating = models.PositiveIntegerField('Değerlendirme', choices=[(i, i) for i in range(1, 6)], 
                                        blank=True, null=True)
    reading_status = models.CharField('Okuma Durumu', max_length=20, choices=[
        ('not_started', 'Başlanmadı'),
        ('reading', 'Okunuyor'),
        ('completed', 'Tamamlandı'),
        ('paused', 'Duraklatıldı'),
        ('abandoned', 'Bırakıldı'),
    ], default='not_started')
    progress_percentage = models.PositiveIntegerField('İlerleme Yüzdesi', default=0)
    start_date = models.DateField('Başlangıç Tarihi', blank=True, null=True)
    finish_date = models.DateField('Bitiş Tarihi', blank=True, null=True)
    
    class Meta:
        ordering = ['order', 'added_at']
        verbose_name = 'Koleksiyon Kitabı'
        verbose_name_plural = 'Koleksiyon Kitapları'
        # Bir kitap bir koleksiyonda sadece bir kez olabilir
        unique_together = ['collection', 'book']
        
    def __str__(self):
        return f"{self.book.title} - {self.collection.name}"
    
    def start_reading(self):
        """Kitabı okumaya başla."""
        self.reading_status = 'reading'
        self.start_date = timezone.now().date()
        self.save()
    
    def complete_reading(self):
        """Kitabı tamamlandı olarak işaretle."""
        self.reading_status = 'completed'
        self.finish_date = timezone.now().date()
        self.progress_percentage = 100
        self.save()


class CollectionFollow(models.Model):
    """
    Kullanıcıların diğer kullanıcıların koleksiyonlarını takip etmesi.
    """
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Takip Eden', 
                                on_delete=models.CASCADE, related_name='following_collections')
    collection = models.ForeignKey(BookCollection, verbose_name='Takip Edilen Koleksiyon', 
                                  on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField('Takip Başlangıcı', auto_now_add=True)
    notifications_enabled = models.BooleanField('Bildirimler Aktif', default=True)
    
    class Meta:
        unique_together = ['follower', 'collection']
        verbose_name = 'Koleksiyon Takibi'
        verbose_name_plural = 'Koleksiyon Takipleri'
        
    def __str__(self):
        return f"{self.follower.username} follows {self.collection.name}"
