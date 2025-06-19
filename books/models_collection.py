from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone

class BookCollection(models.Model):
    """
    Kullanıcıların kendi kitap koleksiyonlarını oluşturması için model.
    """
    VISIBILITY_CHOICES = (
        ('public', 'Herkese Açık'),
        ('private', 'Özel'),
        ('friends', 'Sadece Arkadaşlar'),
    )
    
    name = models.CharField('Koleksiyon Adı', max_length=255)
    description = models.TextField('Açıklama', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Oluşturan', on_delete=models.CASCADE, related_name='book_collections')
    books = models.ManyToManyField(Book, verbose_name='Kitaplar', related_name='collections', through='BookCollectionItem')
    visibility = models.CharField('Görünürlük', max_length=20, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField('Oluşturulma Tarihi', default=timezone.now)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    is_featured = models.BooleanField('Öne Çıkan', default=False)
    cover_image = models.ImageField('Kapak Resmi', upload_to='collection_covers/', blank=True, null=True)
    
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
        
class BookCollectionItem(models.Model):
    """
    Koleksiyonlardaki kitap öğeleri için ara model.
    """
    collection = models.ForeignKey(BookCollection, verbose_name='Koleksiyon', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE)
    added_at = models.DateTimeField('Eklenme Tarihi', default=timezone.now)
    notes = models.TextField('Notlar', blank=True, null=True)
    order = models.PositiveIntegerField('Sıra', default=0)
    
    class Meta:
        ordering = ['order', 'added_at']
        verbose_name = 'Koleksiyon Kitabı'
        verbose_name_plural = 'Koleksiyon Kitapları'
        # Bir kitap bir koleksiyonda sadece bir kez olabilir
        unique_together = ['collection', 'book']
        
    def __str__(self):
        return f"{self.book.title} - {self.collection.name}"
