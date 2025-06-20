from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('my-books/', views.my_books, name='my_books'),
    path('users/', views.user_list, name='users'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('social/', views.social_feed, name='social_feed'),
    path('inactive-account/', views.inactive_account, name='inactive_account'),
    path('admin/users/', views.admin_user_management, name='admin_user_management'),
]
