from django.db import models
from django.conf import settings
from books.models import Book
from books.models_category import Category
from django.utils import timezone
import uuid

class AIBookRecommendation(models.Model):
    """
    AI tabanlı kitap önerisi sistemi için model.
    """
    RECOMMENDATION_TYPE_CHOICES = (
        ('ai_based', 'AI Tabanlı'),
        ('user_based', 'Kullanıcı Tabanlı'),
        ('category_based', 'Kategori Tabanlı'),
        ('similar_books', 'Benzer Kitaplar'),
        ('trending', 'Popüler'),
        ('new_releases', 'Yeni Çıkanlar'),
        ('manual', 'Manuel'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('viewed', 'Görüntülendi'),
        ('liked', 'Beğenildi'),
        ('disliked', 'Beğenilmedi'),
        ('saved', 'Kaydedildi'),
        ('borrowed', 'Ödünç Alındı'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', 
                            on_delete=models.CASCADE, related_name='book_recommendations')
    book = models.ForeignKey(Book, verbose_name='Önerilen Kitap', 
                            on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField('Öneri Tipi', max_length=20, choices=RECOMMENDATION_TYPE_CHOICES)
    confidence_score = models.FloatField('Güven Skoru', default=0.0, 
                                        help_text='0.0 - 1.0 arası öneri güvenilirlik skoru')
    reason = models.TextField('Öneri Sebebi', blank=True, null=True)
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    viewed_at = models.DateTimeField('Görüntülenme Tarihi', blank=True, null=True)
    responded_at = models.DateTimeField('Yanıtlanma Tarihi', blank=True, null=True)
    metadata = models.JSONField('Ek Bilgiler', blank=True, null=True, default=dict)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kitap Önerisi'
        verbose_name_plural = 'Kitap Önerileri'
        unique_together = ['user', 'book']
        
    def __str__(self):
        return f"{self.book.title} → {self.user.username}"
    
    def mark_as_viewed(self):
        """Öneriyi görüntülendi olarak işaretle."""
        if self.status == 'pending':
            self.status = 'viewed'
            self.viewed_at = timezone.now()
            self.save(update_fields=['status', 'viewed_at'])
    
    def mark_response(self, response_type):
        """Kullanıcı yanıtını kaydet."""
        if response_type in ['liked', 'disliked', 'saved', 'borrowed']:
            self.status = response_type
            self.responded_at = timezone.now()
            self.save(update_fields=['status', 'responded_at'])


class UserReadingProfile(models.Model):
    """
    Kullanıcının okuma profili ve tercihlerini tutan model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', 
                               on_delete=models.CASCADE, related_name='reading_profile')
    favorite_categories = models.ManyToManyField(Category, verbose_name='Favori Kategoriler', 
                                               blank=True, through='CategoryPreference')
    favorite_authors = models.JSONField('Favori Yazarlar', blank=True, null=True, default=list)
    preferred_languages = models.JSONField('Tercih Edilen Diller', blank=True, null=True, default=list)
    reading_speed = models.IntegerField('Okuma Hızı (sayfa/saat)', blank=True, null=True)
    preferred_book_length = models.CharField('Tercih Edilen Kitap Uzunluğu', max_length=20, 
                                           choices=[
                                               ('short', 'Kısa (< 200 sayfa)'),
                                               ('medium', 'Orta (200-400 sayfa)'),
                                               ('long', 'Uzun (400+ sayfa)'),
                                               ('any', 'Fark Etmez'),
                                           ], default='any')
    reading_goals = models.JSONField('Okuma Hedefleri', blank=True, null=True, default=dict)
    last_recommendation_date = models.DateTimeField('Son Öneri Tarihi', blank=True, null=True)
    recommendation_frequency = models.CharField('Öneri Sıklığı', max_length=20,
                                              choices=[
                                                  ('daily', 'Günlük'),
                                                  ('weekly', 'Haftalık'),
                                                  ('monthly', 'Aylık'),
                                                  ('never', 'Hiç'),
                                              ], default='weekly')
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        verbose_name = 'Kullanıcı Okuma Profili'
        verbose_name_plural = 'Kullanıcı Okuma Profilleri'
        
    def __str__(self):
        return f"{self.user.username} - Okuma Profili"
    
    def calculate_category_preferences(self):
        """Kullanıcının kategori tercihlerini hesapla."""
        from loans.models import Loan
        from books.models_review import BookReview
        
        # Ödünç alınan kitaplardan kategori tercihlerini çıkar
        user_loans = Loan.objects.filter(borrower=self.user)
        category_scores = {}
        
        for loan in user_loans:
            for book_category in loan.book.categories.all():
                category = book_category.category
                if category.id not in category_scores:
                    category_scores[category.id] = 0
                category_scores[category.id] += 1
        
        # Kullanıcı değerlendirmelerinden kategori tercihlerini güncelle
        user_reviews = BookReview.objects.filter(user=self.user, rating__gte=4)
        for review in user_reviews:
            for book_category in review.book.categories.all():
                category = book_category.category
                if category.id not in category_scores:
                    category_scores[category.id] = 0
                category_scores[category.id] += review.rating  # Yüksek puan verdiği kategorilere ağırlık ver
        
        return category_scores
    
    def update_preferences(self):
        """Okuma tercihlerini otomatik güncelle."""
        category_scores = self.calculate_category_preferences()
        
        # En çok tercih edilen kategorileri güncelle
        if category_scores:
            sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            top_categories = Category.objects.filter(
                id__in=[cat_id for cat_id, score in sorted_categories[:5]]
            )
            
            # Mevcut tercihleri temizle ve yenilerini ekle
            CategoryPreference.objects.filter(reading_profile=self).delete()
            for i, category in enumerate(top_categories):
                CategoryPreference.objects.create(
                    reading_profile=self,
                    category=category,
                    weight=sorted_categories[i][1]
                )


class CategoryPreference(models.Model):
    """
    Kullanıcının kategori tercihlerini ağırlıklandırmak için ara model.
    """
    reading_profile = models.ForeignKey(UserReadingProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    weight = models.FloatField('Ağırlık', default=1.0)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    
    class Meta:
        unique_together = ['reading_profile', 'category']
        ordering = ['-weight']
        verbose_name = 'Kategori Tercihi'
        verbose_name_plural = 'Kategori Tercihleri'
        
    def __str__(self):
        return f"{self.reading_profile.user.username} - {self.category.name} ({self.weight})"


class RecommendationFeedback(models.Model):
    """
    Öneri sistemine geri bildirim için model.
    """
    FEEDBACK_TYPE_CHOICES = (
        ('accuracy', 'Doğruluk'),
        ('relevance', 'İlgililik'),
        ('diversity', 'Çeşitlilik'),
        ('novelty', 'Yenilik'),
        ('general', 'Genel'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', 
                            on_delete=models.CASCADE, related_name='recommendation_feedbacks')
    recommendation = models.ForeignKey(AIBookRecommendation, verbose_name='Öneri', 
                                     on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField('Geri Bildirim Tipi', max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    rating = models.IntegerField('Değerlendirme', choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField('Yorum', blank=True, null=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'recommendation', 'feedback_type']
        verbose_name = 'Öneri Geri Bildirimi'
        verbose_name_plural = 'Öneri Geri Bildirimleri'
        
    def __str__(self):
        return f"{self.user.username} - {self.recommendation.book.title} - {self.rating}/5"
