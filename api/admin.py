from django.contrib import admin
from .models import APIKey, APIRequest

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'key_type', 'is_active', 'created_at', 'expires_at')
    list_filter = ('key_type', 'is_active')
    search_fields = ('name', 'user__username', 'key')
    readonly_fields = ('key',)
    date_hierarchy = 'created_at'

@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'user', 'response_code', 'response_time_ms', 'created_at')
    list_filter = ('method', 'response_code')
    search_fields = ('endpoint', 'user__username', 'ip_address')
    date_hierarchy = 'created_at'
    readonly_fields = ('api_key', 'user', 'endpoint', 'method', 'request_data', 'response_code', 
                     'response_time_ms', 'ip_address', 'user_agent', 'created_at')
