# 📚 Gelişmiş Kütüphane Yönetim Sistemi

Bu proje, modern teknolojiler kullanılarak geliştirilmiş kapsamlı bir kütüphane yönetim sistemidir. Django framework'ü üzerine inşa edilmiş olup, AI tabanlı öneri sistemi, QR kod entegrasyonu, gelişmiş analitikler ve sosyal özellikler içermektedir.

## 🚀 Yeni Eklenen Özellikler

### 🤖 AI Tabanlı Öneri Sistemi
- **Akıllı Kitap Önerileri**: Kullanıcının okuma geçmişi, beğenileri ve kategorilere göre özelleştirilmiş öneriler
- **Çoklu Öneri Algoritmaları**: AI tabanlı, kullanıcı tabanlı, kategori tabanlı ve trend bazlı öneriler
- **Geri Bildirim Sistemi**: Kullanıcıların önerileri değerlendirmesi ve sistemin sürekli öğrenmesi
- **Öneri Ayarları**: Kullanıcıların öneri sıklığı ve tercihlerini özelleştirmesi

### 📱 QR Kod ve Tanımlayıcı Sistemi
- **QR Kod Üretimi**: Her kitap için otomatik QR kod oluşturma
- **Mobil Tarayıcı**: Web tabanlı QR kod okuyucu
- **Çoklu Tanımlayıcı**: QR kod, barkod, RFID, ISBN desteği
- **Konum Takibi**: Kitapların fiziksel konumlarının izlenmesi
- **Tarama Geçmişi**: Tüm tarama işlemlerinin loglanması

### 📊 Gelişmiş Analitik Dashboard
- **Gerçek Zamanlı İstatistikler**: Canlı kullanım verileri
- **Trend Analizi**: Okuma trendleri ve popülerlik grafikleri
- **Kullanıcı Davranış Analizi**: Okuma alışkanlıkları ve tercihler
- **Kütüphane Performansı**: Kütüphaneler arası karşılaştırma
- **Dışa Aktarım**: CSV, PDF formatlarında raporlar

### 📚 Gelişmiş Koleksiyon Sistemi
- **Koleksiyon Türleri**: Kişisel, okuma listesi, istek listesi, favoriler, tematik
- **Sosyal Özellikler**: Koleksiyonları paylaşma ve takip etme
- **Görsel Koleksiyon Kapakları**: Otomatik oluşturulan koleksiyon görselleri
- **İlerleme Takibi**: Koleksiyon okuma ilerlemesi
- **Analitikler**: Koleksiyon başına detaylı istatistikler

### 🎯 Akıllı Okuma Hedefleri
- **Çoklu Hedef Türleri**: Kitap sayısı, sayfa, süre, kategori bazlı hedefler
- **Zorluk Seviyeleri**: Kolay, orta, zor hedef kategorileri
- **Ödül Sistemi**: Hedef tamamlama ödülleri
- **Kategori Bazlı Hedefler**: Belirli kategorilerde okuma hedefleri
- **İlerleme Takibi**: Gerçek zamanlı hedef ilerleme gösterimi

### 🔔 Gelişmiş Bildirim Sistemi
- **Öncelik Seviyeleri**: Düşük, orta, yüksek, kritik öncelik
- **Aksiyon Butonları**: Bildirimlerden direkt eylem alma
- **Metadata Desteği**: Zengin bildirim içeriği
- **Otomatik Süre Dolumu**: Belirlenen süre sonra otomatik silme
- **Gönderen Bilgisi**: Bildirimi gönderen kişi/sistem bilgisi

### 📈 Detaylı Metrikler
- **Kitap Popülerlik Skoru**: Algoritma bazlı popülerlik hesaplama
- **Kullanıcı Aktivite Analizi**: Günlük, haftalık, aylık aktivite raporları
- **Kategori Performansı**: En çok okunan kategoriler
- **Kütüphane Kullanım Desenleri**: Kullanım saatleri ve günleri
- **Okuma Hedefi İlerleme**: Toplu hedef durumu raporları

## 🛠️ Teknik Özellikler

### Yeni Bağımlılıklar
```
qrcode[pil]>=7.4.2           # QR kod üretimi
django-extensions>=3.2.3     # Gelişmiş Django araçları
django-notifications-hq>=1.8.0  # Bildirim sistemi
scikit-learn>=1.3.0         # Makine öğrenmesi (öneri sistemi)
django-celery-beat>=2.5.0   # Zamanlı görevler
redis>=4.6.0                # Cache ve görev kuyruğu
channels>=4.0.0             # WebSocket desteği
django-cleanup>=8.0.0       # Otomatik dosya temizleme
django-import-export>=3.3.0 # Veri içe/dışa aktarım
```

### Veritabanı Değişiklikleri
- **UUID Destekli Modeller**: Güvenli kimlik alanları
- **JSON Alanları**: Esnek metadata depolamak için
- **İndekslenmiş Alanlar**: Performans optimizasyonu
- **Cascade İlişkiler**: Veri bütünlüğü koruması

### Yeni Model Yapıları

#### Öneri Sistemi Modelleri
- `AIBookRecommendation`: AI tabanlı kitap önerileri
- `UserReadingProfile`: Kullanıcı okuma profili
- `CategoryPreference`: Kategori tercihleri
- `RecommendationFeedback`: Öneri geri bildirimleri

#### Tanımlayıcı Sistemi Modelleri
- `BookIdentifier`: Kitap tanımlayıcıları (QR, barkod, RFID)
- `ScanRecord`: Tarama kayıtları
- `BookLocation`: Kitap konum bilgileri

#### Koleksiyon Sistemi Geliştirmeleri
- `CollectionFollow`: Koleksiyon takip sistemi
- **Renk Teması**: Koleksiyonlar için özel renkler
- **Etiket Sistemi**: Gelişmiş kategorilendirme

#### Analitik Modelleri
- `BookPopularityMetrics`: Kitap popülerlik metrikleri
- `UserStatistics`: Kullanıcı istatistikleri
- `LibraryUsagePattern`: Kütüphane kullanım desenleri
- `ReadingGoalProgress`: Okuma hedefi ilerlemesi

## 🎨 Frontend Geliştirmeleri

### Yeni Template Özellikleri
- **Responsive Dashboard**: Mobil uyumlu analitik paneli
- **Interaktif Grafikler**: Chart.js ile dinamik grafikler
- **QR Kod Tarayıcı**: Web tabanlı kamera entegrasyonu
- **Gelişmiş Koleksiyon Görünümü**: Grid ve liste görünümleri
- **Real-time Güncellemeler**: WebSocket ile canlı veri

### CSS Framework Entegrasyonu
- **Material Design**: Modern ve tutarlı tasarım dili
- **Animasyonlar**: Smooth geçişler ve hover efektleri
- **Responsive Grid**: Tüm cihazlarda optimize görünüm
- **Dark Mode**: Koyu tema desteği (opsiyonel)

## 📱 API Geliştirmeleri

### REST API Endpoints
```
/api/recommendations/          # Öneri API'leri
/api/analytics/chart-data/     # Grafik verileri
/api/scan/                     # QR kod tarama
/api/collections/analytics/    # Koleksiyon analitikleri
/api/goals/progress/           # Hedef ilerleme
```

### WebSocket Endpoints
```
/ws/notifications/             # Gerçek zamanlı bildirimler
/ws/analytics/                 # Canlı istatistikler
/ws/scan/                      # QR kod tarama sonuçları
```

## 🔧 Kurulum ve Yapılandırma

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Veritabanı Migration'larını Çalıştırın
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Redis Sunucusunu Başlatın
```bash
redis-server
```

### 4. Celery Worker'ı Başlatın
```bash
celery -A library_management worker -l info
```

### 5. Celery Beat'i Başlatın (Zamanlı görevler için)
```bash
celery -A library_management beat -l info
```

### 6. Django Sunucusunu Başlatın
```bash
python manage.py runserver
```

## 📊 Kullanım Kılavuzu

### Öneri Sistemi
1. **Ayarlar**: `/books/recommendations/settings/` adresinden öneri tercihlerinizi ayarlayın
2. **Dashboard**: `/books/recommendations/` adresinden önerileri görüntüleyin
3. **Geri Bildirim**: Beğen/beğenme butonları ile sistemi eğitin

### QR Kod Sistemi
1. **Tarayıcı**: `/books/scan/` adresinden QR kod tarayıcıya erişin
2. **Kitap Kodları**: Her kitabın detay sayfasında QR kodu bulunur
3. **Geçmiş**: `/books/scan-history/` adresinden tarama geçmişini görün

### Analitik Dashboard
1. **Ana Dashboard**: `/analytics/` adresinden genel istatistikleri görün
2. **Kütüphane Analitikleri**: Kütüphane bazlı raporlar
3. **Kullanıcı Analitikleri**: Kişisel okuma istatistikleri

### Gelişmiş Koleksiyonlar
1. **Oluşturma**: Koleksiyon türü, görünürlük ve tema seçin
2. **Paylaşım**: Herkese açık koleksiyonları sosyal medyada paylaşın
3. **Takip**: Diğer kullanıcıların koleksiyonlarını takip edin

## 🔐 Güvenlik Özellikleri

- **CSRF Koruması**: Tüm formlarda güvenlik token'ı
- **XSS Koruması**: Template güvenlik filtreleri
- **SQL Injection Koruması**: Django ORM güvenliği
- **Dosya Upload Güvenliği**: Dosya türü ve boyut kontrolü
- **Rate Limiting**: API isteklerinde hız sınırlaması

## 🧪 Test Coverage

Yeni eklenen özellikler için kapsamlı test suite'i:
- Unit testler
- Integration testler
- API testleri
- Frontend testleri

```bash
python manage.py test
```

## 📚 Dokümantasyon

Detaylı API dokümantasyonu ve kullanıcı kılavuzu için:
- **API Docs**: `/api/docs/`
- **Admin Panel**: `/admin/`
- **User Guide**: `/help/`

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🆘 Destek

Herhangi bir sorun veya öneriniz için:
- Issue açın
- Email: support@library-management.com
- Telegram: @library_support

## 🔄 Sürüm Geçmişi

### v2.0.0 (Mevcut)
- ✅ AI tabanlı öneri sistemi
- ✅ QR kod entegrasyonu
- ✅ Gelişmiş analitikler
- ✅ Sosyal koleksiyon özellikleri
- ✅ Akıllı okuma hedefleri

### v1.0.0
- ✅ Temel kütüphane yönetimi
- ✅ Kullanıcı sistemi
- ✅ Ödünç verme
- ✅ Basit koleksiyonlar

## 🔮 Gelecek Planları

- [ ] Mobil uygulama (React Native)
- [ ] Blockchain tabanlı sahiplik sistemi
- [ ] AR/VR kütüphane gezintisi
- [ ] Yapay zeka chat botu
- [ ] Çoklu dil desteği
- [ ] Microservices mimarisi

---

**Geliştirici:** Kütüphane Yönetim Sistemi Ekibi  
**Güncellenme:** 27 Haziran 2025  
**Sürüm:** 2.0.0
