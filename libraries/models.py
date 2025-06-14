from django.db import models
from django.conf import settings

class Library(models.Model):
    """
    Model for managing libraries in the system.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_libraries'
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='administered_libraries',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Library'
        verbose_name_plural = 'Libraries'
        ordering = ['name']
    
    def __str__(self):
        return self.name
