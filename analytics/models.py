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
