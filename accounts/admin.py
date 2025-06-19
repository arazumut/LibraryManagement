from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models_notification import Notification
from .models_social import Friendship, BookRecommendation, UserMessage

# Kullanıcı yönetimi
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {'fields': ('user_type', 'profile_picture', 'phone_number', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Ek Bilgiler', {'fields': ('user_type', 'profile_picture', 'phone_number', 'address')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Bildirim Sistemi
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    date_hierarchy = 'created_at'

# Sosyal Sistem
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
    date_hierarchy = 'created_at'

@admin.register(BookRecommendation)
class BookRecommendationAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'book_author', 'sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('book_title', 'book_author', 'sender__username', 'receiver__username', 'message')
    date_hierarchy = 'created_at'

@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('subject', 'message', 'sender__username', 'receiver__username')
    date_hierarchy = 'created_at'
