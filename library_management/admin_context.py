from django.apps import apps

def admin_stats(request):
    """
    Admin paneli için istatistikleri sağlar
    """
    if not request.path.startswith('/admin/'):
        return {}
    
    # Sadece admin kullanıcıları için veri yükle
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    
    # İstatistikleri al
    try:
        model_count = {
            'books': apps.get_model('books', 'Book').objects.count(),
            'users': apps.get_model('accounts', 'User').objects.count(),
            'loans': apps.get_model('loans', 'Loan').objects.count(),
            'libraries': apps.get_model('libraries', 'Library').objects.count(),
        }
        
        # Son ödünç alınan kitapları al
        recent_loans = apps.get_model('loans', 'Loan').objects.order_by('-created_at')[:5]
        
        return {
            'model_count': model_count,
            'recent_loans': recent_loans,
        }
    except:
        # Hata durumunda boş değerler döndür
        return {
            'model_count': {
                'books': 0,
                'users': 0,
                'loans': 0,
                'libraries': 0,
            },
            'recent_loans': [],
        }
