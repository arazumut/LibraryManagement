# Django Backend Kurulum Rehberi 🚀

Bu rehber Flutter Library Management uygulamasının Django backend'ini kurmak için gerekli adımları içermektedir.

## 📋 Gereksinimler

- Python 3.8+
- Django 4.x
- Django REST Framework

## 🛠️ Kurulum Adımları

### 1. Python Sanal Ortamı Oluşturma

```bash
# Sanal ortam oluştur
python -m venv library_backend_env

# Sanal ortamı aktifleştir (Windows)
library_backend_env\Scripts\activate

# Sanal ortamı aktifleştir (macOS/Linux)
source library_backend_env/bin/activate
```

### 2. Gerekli Paketleri Yükleme

```bash
pip install django djangorestframework
pip install django-cors-headers  # CORS desteği için
```

### 3. Django Projesi Oluşturma

```bash
# Yeni Django projesi oluştur
django-admin startproject library_backend
cd library_backend

# Django uygulamaları oluştur
python manage.py startapp users
python manage.py startapp books
python manage.py startapp libraries
python manage.py startapp loans
```

### 4. Django Settings Konfigürasyonu

`library_backend/settings.py` dosyasını düzenleyin:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django REST Framework
    'rest_framework',
    'rest_framework.authtoken',
    
    # CORS
    'corsheaders',
    
    # Local apps
    'users',
    'books',
    'libraries',
    'loans',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware (en üstte olmalı)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'library_backend.urls'

# Django REST Framework ayarları
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS ayarları (Flutter uygulaması için)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Flutter web
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = True  # Geliştirme için - Production'da False yapın

# Veritabanı (varsayılan SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 5. URL Konfigürasyonu

`library_backend/urls.py` dosyasını düzenleyin:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('api/users/', include('users.urls')),
    path('api/books/', include('books.urls')),
    path('api/libraries/', include('libraries.urls')),
    path('api/loans/', include('loans.urls')),
]
```

### 6. Model Dosyalarını Oluşturma

#### `users/models.py`:
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='member')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return self.username
```

#### `books/models.py`:
```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    cover_image = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pages = models.IntegerField()
    language = models.CharField(max_length=50, default='Turkish')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

#### `libraries/models.py`:
```python
from django.db import models

class Library(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    opening_hours = models.CharField(max_length=100)
    image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
```

#### `loans/models.py`:
```python
from django.db import models
from django.contrib.auth import get_user_model
from books.models import Book

User = get_user_model()

class Loan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
```

### 7. URL Dosyalarını Oluşturma

Her uygulama için `urls.py` dosyası oluşturun:

#### `users/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.UserViewSet)

urlpatterns = [
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('', include(router.urls)),
]
```

#### `books/urls.py`:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.BookViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### 8. Settings'e Custom User Ekleme

`library_backend/settings.py` dosyasına ekleyin:

```python
AUTH_USER_MODEL = 'users.CustomUser'
```

### 9. Veritabanı Migrasyonları

```bash
# Migrasyonları oluştur
python manage.py makemigrations

# Migrasyonları uygula
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser
```

### 10. Sunucuyu Başlatma

```bash
# Django sunucusunu başlat
python manage.py runserver 0.0.0.0:8000
```

## 🧪 Test Etme

### 1. Token Alma:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 2. API Test:
```bash
curl -H "Authorization: Token your_token_here" \
  http://localhost:8000/api/users/me/
```

## 📱 Flutter Bağlantısı

Flutter uygulamanız şu URL'lere bağlanacak:

- **Android Emulator**: `http://10.0.2.2:8000/api`
- **iOS Simulator**: `http://localhost:8000/api`
- **Fiziksel Cihaz**: `http://YOUR_IP_ADDRESS:8000/api`

## 🔧 Sorun Giderme

### CORS Hatası:
```python
# settings.py'ye ekleyin
CORS_ALLOW_ALL_ORIGINS = True
```

### Token Hatası:
```bash
# Token oluştur
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from rest_framework.authtoken.models import Token
>>> User = get_user_model()
>>> user = User.objects.get(username='your_username')
>>> token = Token.objects.create(user=user)
>>> print(token.key)
```

## 🎉 Başarı!

Django backend'iniz hazır! Flutter uygulamanız artık API'ye bağlanabilir.

**Önemli:** Production ortamında `DEBUG = False` yapın ve güvenlik ayarlarını gözden geçirin.
