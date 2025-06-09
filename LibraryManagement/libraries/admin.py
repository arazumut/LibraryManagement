from django.contrib import admin
from .models import Library

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'owner__username')
    date_hierarchy = 'created_at'
