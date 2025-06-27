from django.db import models
from django.conf import settings
from books.models import Book
from libraries.models import Library
from django.utils import timezone
import json

class ReadingActivity(models.Model):
    """
    Kullanıcıların okuma aktivitelerini takip etmek için model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                             related_name='reading_activities')
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='reading_activities')
    start_date = models.DateTimeField('Başlangıç Tarihi', default=timezone.now)
    end_date = models.DateTimeField('Bitiş Tarihi', blank=True, null=True)
    is_completed = models.BooleanField('Tamamlandı mı?', default=False)
    pages_read = models.PositiveIntegerField('Okunan Sayfa Sayısı', default=0)
    reading_time_minutes = models.PositiveIntegerField('Okuma Süresi (dakika)', default=0)
    notes = models.TextField('Notlar', blank=True, null=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Okuma Aktivitesi'
        verbose_name_plural = 'Okuma Aktiviteleri'
        
    def __str__(self):
        status = "tamamlandı" if self.is_completed else "devam ediyor"
        return f"{self.user.username} - {self.book.title} ({status})"
    
    def complete_reading(self):
        """Okuma aktivitesini tamamlandı olarak işaretle."""
        self.is_completed = True
        self.end_date = timezone.now()
        self.save()
    
    @property
    def reading_duration(self):
        """Okuma süresini hesapla."""
        if self.end_date:
            return self.end_date - self.start_date
        return timezone.now() - self.start_date

class LibraryStatistics(models.Model):
    """
    Kütüphane istatistikleri için model.
    """
    library = models.ForeignKey(Library, verbose_name='Kütüphane', on_delete=models.CASCADE, related_name='statistics')
    date = models.DateField('Tarih', default=timezone.now)
    total_books = models.PositiveIntegerField('Toplam Kitap Sayısı', default=0)
    available_books = models.PositiveIntegerField('Mevcut Kitap Sayısı', default=0)
    borrowed_books = models.PositiveIntegerField('Ödünç Verilen Kitap Sayısı', default=0)
    new_loans = models.PositiveIntegerField('Yeni Ödünç Verme Sayısı', default=0)
    returned_books = models.PositiveIntegerField('İade Edilen Kitap Sayısı', default=0)
    overdue_books = models.PositiveIntegerField('Gecikmiş Kitap Sayısı', default=0)
    new_members = models.PositiveIntegerField('Yeni Üye Sayısı', default=0)
    active_members = models.PositiveIntegerField('Aktif Üye Sayısı', default=0)
    # İstatistiksel verileri JSON formatında saklayabilir
    additional_data = models.JSONField('Ek Veriler', blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Kütüphane İstatistiği'
        verbose_name_plural = 'Kütüphane İstatistikleri'
        # Bir kütüphane için bir günde bir istatistik kaydı olabilir
        unique_together = ['library', 'date']
        
    def __str__(self):
        return f"{self.library.name} - {self.date}"
    
    @property
    def books_utilization_rate(self):
        """Kitap kullanım oranını hesapla."""
        if self.total_books > 0:
            return (self.borrowed_books / self.total_books) * 100
        return 0
    
    @property
    def get_most_popular_books(self):
        """En popüler kitapları döndür."""
        if self.additional_data and 'popular_books' in self.additional_data:
            return self.additional_data['popular_books']
        return []
    
class UserStatistics(models.Model):
    """
    Kullanıcı okuma istatistikleri için model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                             related_name='reading_statistics')
    year = models.PositiveIntegerField('Yıl')
    month = models.PositiveIntegerField('Ay')
    books_read = models.PositiveIntegerField('Okunan Kitap Sayısı', default=0)
    pages_read = models.PositiveIntegerField('Okunan Sayfa Sayısı', default=0)
    reading_time_minutes = models.PositiveIntegerField('Okuma Süresi (dakika)', default=0)
    loans_count = models.PositiveIntegerField('Ödünç Alma Sayısı', default=0)
    returns_count = models.PositiveIntegerField('İade Sayısı', default=0)
    overdue_count = models.PositiveIntegerField('Gecikmiş İade Sayısı', default=0)
    # Favori kategoriler ve yazarlar gibi ek veriler
    reading_preferences = models.JSONField('Okuma Tercihleri', blank=True, null=True)
    
    class Meta:
        ordering = ['-year', '-month']
        verbose_name = 'Kullanıcı İstatistiği'
        verbose_name_plural = 'Kullanıcı İstatistikleri'
        # Bir kullanıcı için bir ay bir istatistik kaydı olabilir
        unique_together = ['user', 'year', 'month']
        
    def __str__(self):
        return f"{self.user.username} - {self.year}/{self.month}"
    
    @property
    def average_reading_time_per_day(self):
        """Günlük ortalama okuma süresini dakika cinsinden hesapla."""
        # Ayın gün sayısını hesapla
        import calendar
        days_in_month = calendar.monthrange(self.year, self.month)[1]
        if days_in_month > 0:
            return self.reading_time_minutes / days_in_month
        return 0

class BookPopularityMetrics(models.Model):
    """
    Kitap popülerlik metrikleri için model.
    """
    book = models.OneToOneField(Book, verbose_name='Kitap', on_delete=models.CASCADE, 
                               related_name='popularity_metrics')
    total_loans = models.PositiveIntegerField('Toplam Ödünç Alma', default=0)
    total_views = models.PositiveIntegerField('Toplam Görüntülenme', default=0)
    total_reviews = models.PositiveIntegerField('Toplam Değerlendirme', default=0)
    average_rating = models.FloatField('Ortalama Puan', default=0.0)
    total_recommendations = models.PositiveIntegerField('Toplam Öneri', default=0)
    total_collections = models.PositiveIntegerField('Koleksiyonlarda Yer Alma', default=0)
    popularity_score = models.FloatField('Popülerlik Skoru', default=0.0)
    trending_score = models.FloatField('Trend Skoru', default=0.0)
    last_calculated = models.DateTimeField('Son Hesaplama', auto_now=True)
    
    class Meta:
        verbose_name = 'Kitap Popülerlik Metriği'
        verbose_name_plural = 'Kitap Popülerlik Metrikleri'
        
    def __str__(self):
        return f"{self.book.title} - Popülerlik: {self.popularity_score:.2f}"
    
    def calculate_popularity_score(self):
        """Popülerlik skorunu hesapla."""
        # Ağırlıklı skorlama sistemi
        loan_weight = 0.4
        view_weight = 0.2
        review_weight = 0.3
        recommendation_weight = 0.1
        
        max_loans = 100  # Normalleştirme için maksimum değerler
        max_views = 1000
        max_reviews = 50
        max_recommendations = 20
        
        loan_score = min(self.total_loans / max_loans, 1.0) * loan_weight
        view_score = min(self.total_views / max_views, 1.0) * view_weight
        review_score = min(self.total_reviews / max_reviews, 1.0) * review_weight
        recommendation_score = min(self.total_recommendations / max_recommendations, 1.0) * recommendation_weight
        
        # Ortalama puanı da dahil et
        rating_bonus = (self.average_rating / 5.0) * 0.2 if self.average_rating > 0 else 0
        
        self.popularity_score = (loan_score + view_score + review_score + 
                               recommendation_score + rating_bonus) * 100
        self.save(update_fields=['popularity_score', 'last_calculated'])


class LibraryUsagePattern(models.Model):
    """
    Kütüphane kullanım desenleri analizi için model.
    """
    library = models.ForeignKey(Library, verbose_name='Kütüphane', on_delete=models.CASCADE, 
                               related_name='usage_patterns')
    date = models.DateField('Tarih', default=timezone.now)
    hour = models.PositiveIntegerField('Saat', choices=[(i, f"{i:02d}:00") for i in range(24)])
    user_count = models.PositiveIntegerField('Kullanıcı Sayısı', default=0)
    loan_count = models.PositiveIntegerField('Ödünç Alma Sayısı', default=0)
    return_count = models.PositiveIntegerField('İade Sayısı', default=0)
    search_count = models.PositiveIntegerField('Arama Sayısı', default=0)
    
    class Meta:
        unique_together = ['library', 'date', 'hour']
        ordering = ['date', 'hour']
        verbose_name = 'Kütüphane Kullanım Deseni'
        verbose_name_plural = 'Kütüphane Kullanım Desenleri'
        
    def __str__(self):
        return f"{self.library.name} - {self.date} {self.hour:02d}:00"


class ReadingGoalProgress(models.Model):
    """
    Okuma hedefi ilerleme takibi için model.
    """
    goal = models.ForeignKey('books.ReadingGoal', verbose_name='Hedef', 
                            on_delete=models.CASCADE, related_name='progress_records')
    date = models.DateField('Tarih', default=timezone.now)
    daily_progress = models.PositiveIntegerField('Günlük İlerleme', default=0)
    cumulative_progress = models.PositiveIntegerField('Kümülatif İlerleme', default=0)
    percentage_complete = models.FloatField('Tamamlanma Yüzdesi', default=0.0)
    
    class Meta:
        unique_together = ['goal', 'date']
        ordering = ['date']
        verbose_name = 'Hedef İlerleme Kaydı'
        verbose_name_plural = 'Hedef İlerleme Kayıtları'
        
    def __str__(self):
        return f"{self.goal.title} - {self.date} - %{self.percentage_complete:.1f}"
