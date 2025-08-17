// Admin panel için özel JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Admin sayfası yüklendiğinde çalışacak kodlar
    console.log('Kütüphane Yönetim Paneli yüklendi');
    
    // Örnek: Tarihleri formatla
    const formatDates = () => {
        const dateElements = document.querySelectorAll('.field-created_at, .field-updated_at, .field-date');
        dateElements.forEach(el => {
            if (el.textContent && !el.dataset.formatted) {
                try {
                    const date = new Date(el.textContent.trim());
                    if (!isNaN(date)) {
                        el.textContent = date.toLocaleDateString('tr-TR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                        el.dataset.formatted = 'true';
                    }
                } catch (e) {
                    // Hata durumunda orijinal metni koru
                }
            }
        });
    };
    
    // Sayfa yüklendikten sonra tarihleri formatla
    setTimeout(formatDates, 500);
    
    // Admin formlarına özel iyileştirmeler
    const enhanceForms = () => {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            if (!textarea.dataset.enhanced) {
                textarea.style.minHeight = '150px';
                textarea.dataset.enhanced = 'true';
            }
        });
    };
    
    enhanceForms();
});
