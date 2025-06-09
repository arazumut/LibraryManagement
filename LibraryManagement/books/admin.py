from django.contrib import admin
from .models import Book, BookRequest, BookNote

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'library', 'is_available', 'created_at')
    list_filter = ('is_available', 'library', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'description')
    date_hierarchy = 'created_at'
    list_editable = ('is_available',)

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('book', 'requester', 'status', 'requested_at', 'response_at')
    list_filter = ('status', 'requested_at', 'response_at')
    search_fields = ('book__title', 'requester__username', 'message')
    date_hierarchy = 'requested_at'
    list_editable = ('status',)

@admin.register(BookNote)
class BookNoteAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'is_private', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('book__title', 'user__username', 'content')
    date_hierarchy = 'created_at'
    list_editable = ('is_private',)
