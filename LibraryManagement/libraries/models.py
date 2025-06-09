from django.db import models
from django.conf import settings

class Library(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kütüphane Adı")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='libraries',
        verbose_name="Sahip"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Kütüphane"
        verbose_name_plural = "Kütüphaneler"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.owner.username})"
