from django.db import models
from django.conf import settings
from books.models import Book
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class BookReview(models.Model):
    """
    Kitap değerlendirme ve yorum sistemi için model.
    """
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, related_name='book_reviews')
    rating = models.PositiveSmallIntegerField(
        'Değerlendirme', 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1-5 arası değerlendirme puanı'
    )
    review_text = models.TextField('Yorum', blank=True, null=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', default=timezone.now)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    is_public = models.BooleanField('Herkese Açık', default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kitap Değerlendirmesi'
        verbose_name_plural = 'Kitap Değerlendirmeleri'
        # Bir kullanıcı bir kitap için sadece bir değerlendirme yapabilir
        unique_together = ['book', 'user']
        
    def __str__(self):
        return f"{self.book.title} için {self.user.username} tarafından {self.rating}/5 değerlendirme"
    
    @property
    def rating_stars(self):
        """Return HTML for star rating display."""
        stars = ''
        for i in range(5):
            if i < self.rating:
                stars += '★'  # Dolu yıldız
            else:
                stars += '☆'  # Boş yıldız
        return stars
        
class BookReviewLike(models.Model):
    """
    Kitap değerlendirmelerine yapılan beğeniler için model.
    """
    review = models.ForeignKey(BookReview, verbose_name='Değerlendirme', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, related_name='review_likes')
    created_at = models.DateTimeField('Beğenme Tarihi', default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Değerlendirme Beğenisi'
        verbose_name_plural = 'Değerlendirme Beğenileri'
        # Bir kullanıcı bir değerlendirmeyi sadece bir kez beğenebilir
        unique_together = ['review', 'user']
        
    def __str__(self):
        return f"{self.user.username} kullanıcısı {self.review.user.username}'nin değerlendirmesini beğendi"
