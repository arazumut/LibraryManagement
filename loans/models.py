from django.db import models
from django.conf import settings
from books.models import Book
from datetime import timedelta
from django.utils import timezone

class Loan(models.Model):
    """
    Model for handling book loans and returns.
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowed_books')
    loaned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_loans')
    loan_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-loan_date']
        
    def __str__(self):
        return f"{self.book.title} borrowed by {self.borrower.username}"
    
    def save(self, *args, **kwargs):
        # If due date is not set, default to 14 days from loan date
        if not self.due_date:
            self.due_date = self.loan_date + timedelta(days=14)
        
        # Update book status when loan is created
        if not self.pk:  # New loan
            self.book.status = 'borrowed'
            self.book.save()
            
        # Update loan status based on due date
        if self.status == 'active' and self.due_date < timezone.now():
            self.status = 'overdue'
            
        super().save(*args, **kwargs)
    
    def return_book(self):
        """Mark the book as returned and update its status."""
        self.return_date = timezone.now()
        self.status = 'returned'
        self.book.status = 'available'
        self.book.save()
        self.save()
