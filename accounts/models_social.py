from django.db import models
from django.conf import settings
from django.utils import timezone

class Friendship(models.Model):
    """
    Kullanıcılar arası arkadaşlık ilişkileri için model.
    """
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
        ('blocked', 'Engellendi'),
    )
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Gönderen', on_delete=models.CASCADE, 
                             related_name='sent_friendships')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Alıcı', on_delete=models.CASCADE, 
                               related_name='received_friendships')
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Arkadaşlık'
        verbose_name_plural = 'Arkadaşlıklar'
        # Bir kullanıcı diğer bir kullanıcıya sadece bir arkadaşlık isteği gönderebilir
        unique_together = ['sender', 'receiver']
        
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.get_status_display()})"
    
    def accept(self):
        """Arkadaşlık isteğini kabul et."""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            return True
        return False
    
    def reject(self):
        """Arkadaşlık isteğini reddet."""
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False
    
    def block(self):
        """Kullanıcıyı engelle."""
        self.status = 'blocked'
        self.save()
        return True

class BookRecommendation(models.Model):
    """
    Kullanıcılar arası kitap önerileri için model.
    """
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('accepted', 'Kabul Edildi'),
        ('rejected', 'Reddedildi'),
        ('read', 'Okundu'),
    )
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Gönderen', on_delete=models.CASCADE, 
                             related_name='sent_recommendations')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Alıcı', on_delete=models.CASCADE, 
                               related_name='received_recommendations')
    book_title = models.CharField('Kitap Başlığı', max_length=255)
    book_author = models.CharField('Kitap Yazarı', max_length=255)
    # Kitap sistemde var ise ilişkilendirebiliriz
    book = models.ForeignKey('books.Book', verbose_name='Kitap', on_delete=models.SET_NULL, 
                           blank=True, null=True, related_name='recommendations')
    message = models.TextField('Mesaj', blank=True, null=True)
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kitap Önerisi'
        verbose_name_plural = 'Kitap Önerileri'
        
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.book_title}"
    
    def accept(self):
        """Öneriyi kabul et."""
        self.status = 'accepted'
        self.save()
        return True
    
    def reject(self):
        """Öneriyi reddet."""
        self.status = 'rejected'
        self.save()
        return True
    
    def mark_as_read(self):
        """Önerilen kitabı okundu olarak işaretle."""
        self.status = 'read'
        self.save()
        return True

class UserMessage(models.Model):
    """
    Kullanıcılar arası mesajlaşma için model.
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Gönderen', on_delete=models.CASCADE, 
                             related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Alıcı', on_delete=models.CASCADE, 
                               related_name='received_messages')
    subject = models.CharField('Konu', max_length=255, blank=True, null=True)
    message = models.TextField('Mesaj')
    is_read = models.BooleanField('Okundu', default=False)
    read_at = models.DateTimeField('Okunma Tarihi', blank=True, null=True)
    created_at = models.DateTimeField('Gönderilme Tarihi', default=timezone.now)
    
    # Mesaj bir kitap hakkında olabilir
    book = models.ForeignKey('books.Book', verbose_name='Kitap', on_delete=models.SET_NULL, 
                           blank=True, null=True, related_name='messages')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kullanıcı Mesajı'
        verbose_name_plural = 'Kullanıcı Mesajları'
        
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.subject or 'Konu yok'}"
    
    def mark_as_read(self):
        """Mesajı okundu olarak işaretle."""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
