from django.db import models
from django.conf import settings
from libraries.models import Library

class Book(models.Model):
    """
    Model for representing books in the library system.
    """
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
    )
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField('ISBN', max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='books')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    publication_year = models.PositiveIntegerField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title', 'author']
        
    def __str__(self):
        return f"{self.title} by {self.author}"

class BookRequest(models.Model):
    """
    Model for handling book requests between users.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_requests')
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    response_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-requested_at']
        
    def __str__(self):
        return f"Request for {self.book.title} by {self.requester.username} - {self.get_status_display()}"

class BookNote(models.Model):
    """
    Model for user's personal notes about books.
    """
    VISIBILITY_CHOICES = (
        ('private', 'Private'),
        ('public', 'Public'),
    )
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_notes')
    note = models.TextField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"Note on {self.book.title} by {self.user.username}"
