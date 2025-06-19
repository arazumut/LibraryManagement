from django.contrib import admin
from .models import ReadingActivity, LibraryStatistics, UserStatistics

@admin.register(ReadingActivity)
class ReadingActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'start_date', 'end_date', 'is_completed', 'pages_read', 'reading_time_minutes')
    list_filter = ('is_completed', 'start_date')
    search_fields = ('user__username', 'book__title')
    date_hierarchy = 'start_date'

@admin.register(LibraryStatistics)
class LibraryStatisticsAdmin(admin.ModelAdmin):
    list_display = ('library', 'date', 'total_books', 'available_books', 'borrowed_books', 'overdue_books')
    list_filter = ('date',)
    search_fields = ('library__name',)
    date_hierarchy = 'date'

@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'month', 'books_read', 'pages_read', 'loans_count', 'returns_count')
    list_filter = ('year', 'month')
    search_fields = ('user__username',)
