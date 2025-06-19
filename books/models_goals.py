from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone

class ReadingGoal(models.Model):
    """
    Kullanıcıların kişisel okuma hedefleri için model.
    """
    PERIOD_CHOICES = (
        ('daily', 'Günlük'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('yearly', 'Yıllık'),
        ('custom', 'Özel'),
    )
    
    GOAL_TYPE_CHOICES = (
        ('books', 'Kitap Sayısı'),
        ('pages', 'Sayfa Sayısı'),
        ('minutes', 'Okuma Süresi (Dakika)'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                             related_name='reading_goals')
    title = models.CharField('Hedef Başlığı', max_length=255)
    description = models.TextField('Açıklama', blank=True, null=True)
    goal_type = models.CharField('Hedef Tipi', max_length=20, choices=GOAL_TYPE_CHOICES)
    target_value = models.PositiveIntegerField('Hedef Değeri')
    current_value = models.PositiveIntegerField('Mevcut Değer', default=0)
    period = models.CharField('Periyod', max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField('Başlangıç Tarihi', default=timezone.now)
    end_date = models.DateField('Bitiş Tarihi', blank=True, null=True)
    is_completed = models.BooleanField('Tamamlandı mı?', default=False)
    is_public = models.BooleanField('Herkese Açık', default=False)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Okuma Hedefi'
        verbose_name_plural = 'Okuma Hedefleri'
        
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def update_progress(self, value):
        """Hedefe ilerlemeyi güncelle."""
        self.current_value += value
        if self.current_value >= self.target_value:
            self.is_completed = True
        self.save()
    
    @property
    def progress_percentage(self):
        """İlerleme yüzdesini hesapla."""
        if self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0
    
    @property
    def remaining(self):
        """Kalan hedef değerini hesapla."""
        return max(0, self.target_value - self.current_value)
    
    @property
    def days_remaining(self):
        """Kalan gün sayısını hesapla."""
        if self.end_date:
            return max(0, (self.end_date - timezone.now().date()).days)
        return None

class ReadingChallenge(models.Model):
    """
    Okuma meydan okumaları için model.
    """
    STATUS_CHOICES = (
        ('upcoming', 'Yaklaşan'),
        ('ongoing', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    )
    
    title = models.CharField('Başlık', max_length=255)
    description = models.TextField('Açıklama')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Oluşturan', on_delete=models.CASCADE, 
                              related_name='created_challenges')
    start_date = models.DateField('Başlangıç Tarihi')
    end_date = models.DateField('Bitiş Tarihi')
    goal_type = models.CharField('Hedef Tipi', max_length=20, choices=ReadingGoal.GOAL_TYPE_CHOICES)
    target_value = models.PositiveIntegerField('Hedef Değeri')
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_featured = models.BooleanField('Öne Çıkan', default=False)
    is_private = models.BooleanField('Özel', default=False)
    # Özel bir kitap listesi gerektirebilir
    required_books = models.ManyToManyField(Book, verbose_name='Gerekli Kitaplar', blank=True, related_name='required_for_challenges')
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Okuma Meydan Okuması'
        verbose_name_plural = 'Okuma Meydan Okumaları'
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Durum kontrolü
        today = timezone.now().date()
        if self.start_date <= today <= self.end_date:
            self.status = 'ongoing'
        elif today > self.end_date:
            self.status = 'completed'
        else:
            self.status = 'upcoming'
        super().save(*args, **kwargs)
    
    @property
    def participant_count(self):
        """Katılımcı sayısını döndürür."""
        return self.participants.count()
    
    @property
    def completion_rate(self):
        """Tamamlanma oranını hesapla."""
        completed = self.participants.filter(is_completed=True).count()
        if self.participant_count > 0:
            return (completed / self.participant_count) * 100
        return 0

class ChallengeParticipant(models.Model):
    """
    Meydan okuma katılımcıları için model.
    """
    challenge = models.ForeignKey(ReadingChallenge, verbose_name='Meydan Okuma', on_delete=models.CASCADE, 
                                related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Kullanıcı', on_delete=models.CASCADE, 
                           related_name='challenge_participations')
    current_value = models.PositiveIntegerField('Mevcut Değer', default=0)
    is_completed = models.BooleanField('Tamamlandı mı?', default=False)
    joined_at = models.DateTimeField('Katılım Tarihi', auto_now_add=True)
    completed_at = models.DateTimeField('Tamamlanma Tarihi', blank=True, null=True)
    
    class Meta:
        ordering = ['-joined_at']
        verbose_name = 'Meydan Okuma Katılımcısı'
        verbose_name_plural = 'Meydan Okuma Katılımcıları'
        # Bir kullanıcı bir meydan okumaya bir kez katılabilir
        unique_together = ['challenge', 'user']
        
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"
    
    def update_progress(self, value):
        """Meydan okuma ilerlemesini güncelle."""
        self.current_value += value
        if self.current_value >= self.challenge.target_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        self.save()
    
    @property
    def progress_percentage(self):
        """İlerleme yüzdesini hesapla."""
        if self.challenge.target_value > 0:
            return min(100, (self.current_value / self.challenge.target_value) * 100)
        return 0
