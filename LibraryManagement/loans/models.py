from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone
from datetime import timedelta

class Loan(models.Model):
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE,
        related_name='loans',
        verbose_name="Kitap"
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrowed_books',
        verbose_name="Ödünç Alan"
    )
    lender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lent_books',
        verbose_name="Ödünç Veren"
    )
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Başlangıç Tarihi")
    due_date = models.DateTimeField(verbose_name="Son Tarih")
    returned_date = models.DateTimeField(blank=True, null=True, verbose_name="İade Tarihi")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    
    class Meta:
        verbose_name = "Ödünç"
        verbose_name_plural = "Ödünçler"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.borrower.username} tarafından ödünç alındı"
    
    def save(self, *args, **kwargs):
        # Eğer son tarih belirlenmemişse, varsayılan olarak 14 gün sonrasını belirle
        if not self.due_date:
            self.due_date = self.start_date + timedelta(days=14)
        
        # Kitap ödünç alındığında durumunu güncelle
        if not self.id:  # Yeni bir kayıt oluşturuluyorsa
            self.book.is_available = False
            self.book.save()
            
        super().save(*args, **kwargs)
    
    def return_book(self):
        """Kitabı iade et ve kitap durumunu güncelle"""
        self.returned_date = timezone.now()
        self.book.is_available = True
        self.book.save()
        self.save()
    
    @property
    def is_returned(self):
        """Kitabın iade edilip edilmediğini kontrol et"""
        return self.returned_date is not None
    
    @property
    def is_overdue(self):
        """Kitabın iade süresinin geçip geçmediğini kontrol et"""
        if self.is_returned:
            return False
        return timezone.now() > self.due_date
