# 📚 Kütüphane Yönetim Sistemi - Örnek Veriler

Bu Django projesi için geliştirilmiş olan örnek veri oluşturma komutları.

## 🚀 Hızlı Başlangıç

### 1. Tüm Örnek Verileri Oluştur
```bash
python manage.py setup_sample_data
```

### 2. Mevcut Verileri Temizle ve Yeniden Oluştur
```bash
python manage.py setup_sample_data --clear
```

### 3. Ödünç Kayıtları Olmadan Oluştur
```bash
python manage.py setup_sample_data --no-loans
```

## 📋 Bireysel Komutlar

### Kullanıcılar
```bash
# Örnek kullanıcılar oluştur
python manage.py create_sample_users

# Mevcut kullanıcıları temizle ve yeniden oluştur
python manage.py create_sample_users --clear
```

### Kütüphaneler
```bash
# Örnek kütüphaneler oluştur
python manage.py create_sample_libraries

# Mevcut kütüphaneleri temizle ve yeniden oluştur
python manage.py create_sample_libraries --clear
```

### Kitaplar
```bash
# Örnek kitaplar, istekler ve notlar oluştur
python manage.py create_sample_books

# Sadece kitaplar oluştur (istekler ve notlar olmadan)
python manage.py create_sample_books --books-only

# Mevcut kitapları temizle ve yeniden oluştur
python manage.py create_sample_books --clear
```

### Ödünç Kayıtları
```bash
# Örnek ödünç kayıtları oluştur
python manage.py create_sample_loans

# Mevcut ödünç kayıtlarını temizle ve yeniden oluştur
python manage.py create_sample_loans --clear
```

## 👥 Oluşturulan Kullanıcılar

| Kullanıcı Adı | Şifre | Rol | E-posta |
|----------------|-------|-----|---------|
| super_admin | super_admin | Süper Admin | admin@library.com |
| ahmet_yonetici | ahmet_yonetici | Kütüphane Yöneticisi | ahmet@library.com |
| ayse_yonetici | ayse_yonetici | Kütüphane Yöneticisi | ayse@library.com |
| mehmet_okuyucu | mehmet_okuyucu | Okuyucu | mehmet@email.com |
| fatma_okuyucu | fatma_okuyucu | Okuyucu | fatma@email.com |
| ali_okuyucu | ali_okuyucu | Okuyucu | ali@email.com |
| zeynep_okuyucu | zeynep_okuyucu | Okuyucu | zeynep@email.com |
| emre_okuyucu | emre_okuyucu | Okuyucu | emre@email.com |

## 📚 Oluşturulan Kütüphaneler

1. **Merkez Kütüphanesi** (Sahip: Ahmet Kaya)
2. **Üniversite Kütüphanesi** (Sahip: Ayşe Demir)
3. **Çocuk Kütüphanesi** (Sahip: Ahmet Kaya)
4. **Bilim ve Teknoloji Kütüphanesi** (Sahip: Ayşe Demir)
5. **Edebiyat Kütüphanesi** (Sahip: Ahmet Kaya)

## 📖 Oluşturulan Kitap Kategorileri

- **Türk Edebiyatı**: Saatleri Ayarlama Enstitüsü, Tutunamayanlar, Kürk Mantolu Madonna, vb.
- **Dünya Edebiyatı**: 1984, Hayvan Çiftliği, Suç ve Ceza, Yüzüklerin Efendisi, vb.
- **Bilim ve Felsefe**: Sapiens, Homo Deus, Büyük Tasarım, vb.
- **Çocuk Kitapları**: Küçük Prens, Harry Potter, Matilda, vb.
- **Bilim ve Teknoloji**: Python Programlama, Clean Code, vb.
- **Tarih**: Nutuk, Osmanlı Tarihi, İkinci Dünya Savaşı, vb.
- **Psikoloji**: Düşünme Hızlı ve Yavaş, Atomik Alışkanlıklar, vb.

## 📊 Oluşturulan Veriler

- **8 Kullanıcı** (1 Süper Admin, 2 Kütüphane Yöneticisi, 5 Okuyucu)
- **5 Kütüphane**
- **27+ Kitap** (çeşitli kategorilerde)
- **~15 Kitap İsteği** (farklı durumlarla)
- **~50 Kitap Notu** (public ve private)
- **~20 Ödünç Kaydı** (aktif ve iade edilmiş)

## 🔧 Kurulum Öncesi Gereksinimler

```bash
# Migrasyonları çalıştır
python manage.py makemigrations
python manage.py migrate

# Örnek verileri oluştur
python manage.py setup_sample_data
```

## 🌐 Test Etme

1. Sunucuyu başlat:
```bash
python manage.py runserver
```

2. Admin paneline git: http://127.0.0.1:8000/admin/

3. Yukarıdaki kullanıcı bilgileriyle giriş yap

## ⚠️ Önemli Notlar

- Bu veriler sadece **geliştirme ve test** amaçlıdır
- Tüm şifreler kullanıcı adıyla aynıdır (güvenlik riski!)
- Production ortamında bu komutları **çalıştırmayın**
- Verileri temizlemek için `--clear` parametresini kullanın

## 🆘 Sorun Giderme

### Django bulunamadı hatası
```bash
# Sanal ortamı aktifleştir
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### Migrasyon hataları
```bash
python manage.py makemigrations accounts
python manage.py makemigrations libraries
python manage.py makemigrations books
python manage.py makemigrations loans
python manage.py migrate
```

### Veritabanını sıfırla
```bash
rm db.sqlite3
python manage.py migrate
python manage.py setup_sample_data
```
