from django.db import models
from django.conf import settings
from books.models import Book
from datetime import timedelta
from django.utils import timezone

class Loan(models.Model):
    """
    Kitap ödünç alma ve iade işlemleri için model.
    """
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('returned', 'İade Edildi'),
        ('overdue', 'Gecikmiş'),
    )
    
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Ödünç Alan', on_delete=models.CASCADE, related_name='borrowed_books')
    loaned_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Ödünç Veren', on_delete=models.CASCADE, related_name='managed_loans')
    loan_date = models.DateTimeField('Ödünç Verme Tarihi', default=timezone.now)
    due_date = models.DateTimeField('İade Tarihi')
    return_date = models.DateTimeField('Gerçek İade Tarihi', blank=True, null=True)
    status = models.CharField('Durum', max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField('Notlar', blank=True, null=True)
    
    class Meta:
        ordering = ['-loan_date']
        verbose_name = 'Ödünç Verme'
        verbose_name_plural = 'Ödünç Vermeler'
        
    def __str__(self):
        return f"{self.book.title} kitabı {self.borrower.username} tarafından ödünç alındı"
    
    def save(self, *args, **kwargs):
        # Eğer iade tarihi belirlenmemişse, ödünç verme tarihinden 14 gün sonrasını ata
        if not self.due_date:
            self.due_date = self.loan_date + timedelta(days=14)
        
        # Ödünç verme oluşturulduğunda kitap durumunu güncelle
        if not self.pk:  # Yeni ödünç verme
            self.book.status = 'borrowed'
            self.book.save()
            
        # İade tarihine göre ödünç verme durumunu güncelle
        if self.status == 'active' and self.due_date < timezone.now():
            self.status = 'overdue'
            
        super().save(*args, **kwargs)
    
    def return_book(self):
        """Kitabı iade edilmiş olarak işaretle ve durumunu güncelle."""
        self.return_date = timezone.now()
        self.status = 'returned'
        self.book.status = 'available'
        self.book.save()
        self.save()
