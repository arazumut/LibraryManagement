# Library Management API Dokümantasyonu

Bu dokümantasyon, Library Management API'sini kullanarak mobil uygulamanızı lokal API sunucunuza nasıl bağlayacağınızı açıklar.

## API Genel Bakış

Library Management API'si, kitaplar, kullanıcılar, kütüphaneler ve ödünç alma işlemleri için bir RESTful API sağlar. API, Django REST Framework kullanılarak oluşturulmuştur ve aşağıdaki kaynakları içerir:

- `/api/users/` - Kullanıcı yönetimi
- `/api/books/` - Kitap yönetimi
- `/api/categories/` - Kategori yönetimi
- `/api/libraries/` - Kütüphane yönetimi
- `/api/loans/` - Ödünç alma işlemleri

## API Dokümantasyon Araçları

API'nin etkileşimli dokümantasyonuna erişmek için:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc UI: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema/`

## Mobil Uygulamanızı Lokal API'ye Bağlama

### 1. Yerel Sunucunun Çalıştığından Emin Olun

Django sunucunuzun çalıştığından emin olun:

```bash
python3 manage.py runserver
```

Varsayılan olarak, sunucu `http://127.0.0.1:8000` adresinde çalışacaktır.

### 2. Flutter Uygulamanızda API İstemcisi Oluşturun

#### 2.1. Gerekli Bağımlılıkları Ekleyin

Flutter projenizin `pubspec.yaml` dosyasına HTTP istemcisi için gerekli bağımlılıkları ekleyin:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0  # En güncel sürümü kullanın
  shared_preferences: ^2.2.0  # Token depolamak için (gerekirse)
```

Ardından bağımlılıkları yükleyin:

```bash
flutter pub get
```

#### 2.2. API Servis Sınıfı Oluşturun

Flutter projenizde bir API servis sınıfı oluşturun:

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Lokal makine için API taban URL'si
  // Emülatör için 10.0.2.2 kullanılır (localhost yerine)
  // Fiziksel cihaz için bilgisayarınızın IP adresi kullanılmalıdır
  final String baseUrl = 'http://10.0.2.2:8000/api';  // Android Emülatör için
  // final String baseUrl = 'http://192.168.1.XXX:8000/api';  // Fiziksel cihaz için
  // final String baseUrl = 'http://127.0.0.1:8000/api';  // iOS Simulator için
  
  // Kimlik doğrulama token'ı (varsa)
  String? _authToken;
  
  // Token ayarlama
  void setToken(String token) {
    _authToken = token;
  }

  // Headers oluşturma (kimlik doğrulama dahil)
  Map<String, String> _headers() {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    
    if (_authToken != null) {
      headers['Authorization'] = 'Token $_authToken'; // Django REST Token Auth kullanıyorsanız
      // JWT kullanıyorsanız: headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }
  
  // GET isteği
  Future<dynamic> get(String endpoint) async {
    final response = await http.get(
      Uri.parse('$baseUrl/$endpoint'),
      headers: _headers(),
    );
    
    return _processResponse(response);
  }
  
  // POST isteği
  Future<dynamic> post(String endpoint, dynamic data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/$endpoint'),
      headers: _headers(),
      body: jsonEncode(data),
    );
    
    return _processResponse(response);
  }
  
  // PUT isteği
  Future<dynamic> put(String endpoint, dynamic data) async {
    final response = await http.put(
      Uri.parse('$baseUrl/$endpoint'),
      headers: _headers(),
      body: jsonEncode(data),
    );
    
    return _processResponse(response);
  }
  
  // DELETE isteği
  Future<dynamic> delete(String endpoint) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/$endpoint'),
      headers: _headers(),
    );
    
    return _processResponse(response);
  }
  
  // Yanıt işleme
  dynamic _processResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isNotEmpty) {
        return jsonDecode(response.body);
      }
      return null;
    } else {
      // Hata durumunda
      throw Exception('API Hatası: ${response.statusCode} - ${response.reasonPhrase}\n${response.body}');
    }
  }
  
  // Oturum açma
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await post('token/', {
      'username': username,
      'password': password,
    });
    
    if (response != null && response['token'] != null) {
      setToken(response['token']);
    }
    
    return response;
  }
}
```

#### 2.3. Model Sınıfları Oluşturun

API'den gelen verileri işlemek için model sınıfları oluşturun:

```dart
// lib/models/book.dart
class Book {
  final int id;
  final String title;
  final String isbn;
  final String author;
  final String publisher;
  final int publicationYear;
  final String description;
  final String? coverImage;
  final Map<String, dynamic> category;
  final int pages;
  final String language;
  final String status;
  final bool available;
  
  Book({
    required this.id,
    required this.title,
    required this.isbn,
    required this.author,
    required this.publisher,
    required this.publicationYear,
    required this.description,
    this.coverImage,
    required this.category,
    required this.pages,
    required this.language,
    required this.status,
    required this.available,
  });
  
  factory Book.fromJson(Map<String, dynamic> json) {
    return Book(
      id: json['id'],
      title: json['title'],
      isbn: json['isbn'],
      author: json['author'],
      publisher: json['publisher'],
      publicationYear: json['publication_year'],
      description: json['description'],
      coverImage: json['cover_image'],
      category: json['category'],
      pages: json['pages'],
      language: json['language'],
      status: json['status'],
      available: json['available'],
    );
  }
  
  Map<String, dynamic> toJson() => {
    'title': title,
    'isbn': isbn,
    'author': author,
    'publisher': publisher,
    'publication_year': publicationYear,
    'description': description,
    'category_id': category['id'],
    'pages': pages,
    'language': language,
    'status': status,
  };
}
```

#### 2.4. Kitap Servisi Oluşturun

Kitap verilerini işlemek için özel bir servis oluşturun:

```dart
// lib/services/book_service.dart
import 'package:your_app/models/book.dart';
import 'package:your_app/services/api_service.dart';

class BookService {
  final ApiService _apiService = ApiService();
  
  // Tüm kitapları getir
  Future<List<Book>> getAllBooks() async {
    final response = await _apiService.get('books/');
    return (response as List).map((data) => Book.fromJson(data)).toList();
  }
  
  // ID'ye göre kitap getir
  Future<Book> getBookById(int id) async {
    final response = await _apiService.get('books/$id/');
    return Book.fromJson(response);
  }
  
  // Kategori ID'sine göre kitapları getir
  Future<List<Book>> getBooksByCategory(int categoryId) async {
    final response = await _apiService.get('categories/$categoryId/books/');
    return (response as List).map((data) => Book.fromJson(data)).toList();
  }
  
  // Yeni kitap ekle (admin için)
  Future<Book> addBook(Book book) async {
    final response = await _apiService.post('books/', book.toJson());
    return Book.fromJson(response);
  }
  
  // Kitap güncelle (admin için)
  Future<Book> updateBook(int id, Book book) async {
    final response = await _apiService.put('books/$id/', book.toJson());
    return Book.fromJson(response);
  }
  
  // Kitap sil (admin için)
  Future<void> deleteBook(int id) async {
    await _apiService.delete('books/$id/');
  }
}
```

### 3. Fiziksel Cihaz Bağlantı Ayarları

Eğer fiziksel bir cihazla test ediyorsanız:

1. Bilgisayarınızın IP adresini bulun:
   - macOS/Linux: `ifconfig | grep "inet " | grep -v 127.0.0.1`
   - Windows: `ipconfig`

2. Django sunucunuzu tüm arayüzlere açın:
   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```

3. API servisinizde IP adresini güncelleyin:
   ```dart
   final String baseUrl = 'http://192.168.1.XXX:8000/api';  // Bilgisayarınızın IP adresi
   ```

4. Aynı Wi-Fi ağında olduğunuzdan emin olun

### 4. Emülatörde Test

#### Android Emülatör
Android Emülatör kullanıyorsanız, `10.0.2.2` özel IP adresi, emülatörün ana bilgisayarınızın `127.0.0.1` adresine erişmesini sağlar.

```dart
final String baseUrl = 'http://10.0.2.2:8000/api';
```

#### iOS Simulator
iOS Simulator kullanıyorsanız, doğrudan `127.0.0.1` adresini kullanabilirsiniz.

```dart
final String baseUrl = 'http://127.0.0.1:8000/api';
```

### 5. CORS Ayarları

Eğer API'nize mobil uygulamanızdan erişirken CORS (Cross-Origin Resource Sharing) hatası alırsanız, Django projenize `django-cors-headers` paketini eklemeniz gerekebilir:

```bash
pip install django-cors-headers
```

Ardından, `settings.py` dosyanızı güncelleyin:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Diğer middleware'lerden önce olmalı
    # ... diğer middleware'ler
]

# Tüm kaynaklar için CORS'u etkinleştir (Geliştirme için)
CORS_ALLOW_ALL_ORIGINS = True

# Alternatif olarak, belirli kaynakları belirtebilirsiniz
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8000",
#     "http://localhost:3000",
# ]
```

### 6. Örnek Flutter UI İmplementasyonu

Kitapları listeleyen basit bir Flutter ekranı örneği:

```dart
// lib/screens/book_list_screen.dart
import 'package:flutter/material.dart';
import 'package:your_app/models/book.dart';
import 'package:your_app/services/book_service.dart';

class BookListScreen extends StatefulWidget {
  @override
  _BookListScreenState createState() => _BookListScreenState();
}

class _BookListScreenState extends State<BookListScreen> {
  final BookService _bookService = BookService();
  List<Book> _books = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadBooks();
  }

  Future<void> _loadBooks() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final books = await _bookService.getAllBooks();
      
      setState(() {
        _books = books;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Kitap Listesi'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadBooks,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Hata: $_error', style: TextStyle(color: Colors.red)),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadBooks,
              child: Text('Tekrar Dene'),
            ),
          ],
        ),
      );
    }

    if (_books.isEmpty) {
      return Center(child: Text('Kitap bulunamadı'));
    }

    return RefreshIndicator(
      onRefresh: _loadBooks,
      child: ListView.builder(
        itemCount: _books.length,
        itemBuilder: (context, index) {
          final book = _books[index];
          return ListTile(
            leading: book.coverImage != null
                ? Image.network(
                    book.coverImage!,
                    width: 50,
                    height: 75,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) =>
                        Icon(Icons.book, size: 50),
                  )
                : Icon(Icons.book, size: 50),
            title: Text(book.title),
            subtitle: Text('${book.author} • ${book.publicationYear}'),
            trailing: Container(
              padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: book.available ? Colors.green : Colors.red,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                book.available ? 'Mevcut' : 'Ödünç Verildi',
                style: TextStyle(color: Colors.white),
              ),
            ),
            onTap: () {
              // Kitap detay sayfasına yönlendirme
              // Navigator.push(context, MaterialPageRoute(...));
            },
          );
        },
      ),
    );
  }
}
```

## API Endpoint Referansı

### Kitaplar (Books)

#### Kitap Listesi Alma
- **URL**: `/api/books/`
- **Method**: GET
- **Yetkilendirme**: İsteğe bağlı
- **Yanıt**:
  ```json
  [
    {
      "id": 1,
      "title": "Django for Beginners",
      "isbn": "978-1234567890",
      "author": "William S. Vincent",
      "publisher": "Example Press",
      "publication_year": 2020,
      "description": "Learn Django from scratch",
      "cover_image": "http://127.0.0.1:8000/media/covers/django.jpg",
      "category": {
        "id": 1,
        "name": "Programming",
        "slug": "programming",
        "description": "Programming books"
      },
      "pages": 300,
      "language": "en",
      "status": "available",
      "available": true,
      "created_at": "2025-01-01T12:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ]
  ```

#### Tek Kitap Alma
- **URL**: `/api/books/{id}/`
- **Method**: GET
- **Yetkilendirme**: İsteğe bağlı

#### Kitap Oluşturma
- **URL**: `/api/books/`
- **Method**: POST
- **Yetkilendirme**: Gerekli (Admin)
- **İstek Gövdesi**:
  ```json
  {
    "title": "New Book",
    "isbn": "978-0987654321",
    "author": "Author Name",
    "publisher": "Publisher Name",
    "publication_year": 2022,
    "description": "Book description",
    "category_id": 1,
    "pages": 200,
    "language": "en",
    "status": "available"
  }
  ```

#### Kitap Güncelleme
- **URL**: `/api/books/{id}/`
- **Method**: PUT
- **Yetkilendirme**: Gerekli (Admin)

#### Kitap Silme
- **URL**: `/api/books/{id}/`
- **Method**: DELETE
- **Yetkilendirme**: Gerekli (Admin)

### Kullanıcılar (Users)

#### Kullanıcı Listesi
- **URL**: `/api/users/`
- **Method**: GET
- **Yetkilendirme**: Gerekli (Admin)

#### Kullanıcı Kimlik Doğrulama
- **URL**: `/api/token/`
- **Method**: POST
- **İstek Gövdesi**:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- **Yanıt**:
  ```json
  {
    "token": "your_auth_token"
  }
  ```

#### Mevcut Kullanıcı Bilgisi
- **URL**: `/api/users/me/`
- **Method**: GET
- **Yetkilendirme**: Gerekli
- **Yanıt**:
  ```json
  {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com",
    "first_name": "Your",
    "last_name": "Name",
    "user_type": "member"
  }
  ```

## Kimlik Doğrulama

API, Token tabanlı kimlik doğrulama kullanır. Bir token almak için:

1. `/api/token/` endpoint'ine kullanıcı adı ve şifre gönderin
2. Dönen token'ı, sonraki isteklerinizde `Authorization` header'ında kullanın

```dart
// Token almak
final response = await apiService.post('token/', {
  'username': 'your_username',
  'password': 'your_password',
});

final token = response['token'];

// Token'ı kullanmak için
apiService.setToken(token);
```

## Yaygın Sorunlar ve Çözümleri

### CORS Hataları
Eğer "Access-Control-Allow-Origin header is missing" gibi hatalar alıyorsanız, yukarıda belirtildiği gibi Django projenize `django-cors-headers` ekleyin.

### Ağ Bağlantısı Hataları
- Telefonunuzun ve bilgisayarınızın aynı ağda olduğundan emin olun
- Django sunucusunun `0.0.0.0:8000` adresinde çalıştığından emin olun
- Doğru IP adresini kullandığınızdan emin olun

### 401 Unauthorized Hataları
- Token'ın doğru formatta olduğundan emin olun
- Token'ın süresi dolmadığından emin olun
- Kullanıcının gerekli yetkilere sahip olduğundan emin olun

## Sonuç

Bu dokümantasyon, Django API'nizi Flutter mobil uygulamanıza nasıl bağlayacağınızı temel hatlarıyla anlatmaktadır. Django API'nin dokümantasyonunu görmek ve API'yi test etmek için Swagger UI'yi (`http://127.0.0.1:8000/api/docs/`) kullanabilirsiniz.
