from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import json

from analytics.models import (
    ReadingActivity, LibraryStatistics, UserStatistics, 
    BookPopularityMetrics, LibraryUsagePattern
)
from books.models import Book
from books.models_category import Category
from libraries.models import Library
from loans.models import Loan
from accounts.models import User

@login_required
def analytics_dashboard(request):
    """Ana analytics dashboard."""
    # Kullanıcının kütüphaneleri
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    # Genel istatistikler
    total_books = Book.objects.filter(library__in=user_libraries).count()
    total_loans = Loan.objects.filter(book__library__in=user_libraries).count()
    active_loans = Loan.objects.filter(
        book__library__in=user_libraries,
        status__in=['active', 'overdue']
    ).count()
    
    # Son 30 günlük veriler
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_loans = Loan.objects.filter(
        book__library__in=user_libraries,
        loan_date__gte=thirty_days_ago
    ).count()
    
    # Popüler kategoriler
    popular_categories = Category.objects.annotate(
        book_count=Count('bookcategory__book', filter=Q(bookcategory__book__library__in=user_libraries))
    ).filter(book_count__gt=0).order_by('-book_count')[:5]
    
    # Aylık trend verileri (son 12 ay)
    monthly_data = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - relativedelta(months=i)
        month_end = month_start + relativedelta(months=1)
        
        loan_count = Loan.objects.filter(
            book__library__in=user_libraries,
            loan_date__gte=month_start,
            loan_date__lt=month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'loans': loan_count
        })
    
    monthly_data.reverse()
    
    context = {
        'user_libraries': user_libraries,
        'total_books': total_books,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'recent_loans': recent_loans,
        'popular_categories': popular_categories,
        'monthly_data': json.dumps(monthly_data),
        'active_menu': 'analytics',
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def library_analytics(request, library_id):
    """Belirli bir kütüphane için detaylı analitik."""
    library = get_object_or_404(Library, id=library_id)
    
    # Yetki kontrolü
    if not (library.owner == request.user or request.user in library.admins.all()):
        return JsonResponse({'error': 'Bu kütüphaneye erişim yetkiniz yok.'}, status=403)
    
    # Kütüphane istatistikleri
    total_books = library.books.count()
    available_books = library.books.filter(status='available').count()
    borrowed_books = library.books.filter(status='borrowed').count()
    
    # Son 30 günlük aktivite
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_activity = {
        'loans': Loan.objects.filter(
            book__library=library,
            loan_date__gte=thirty_days_ago
        ).count(),
        'returns': Loan.objects.filter(
            book__library=library,
            return_date__gte=thirty_days_ago,
            status='returned'
        ).count(),
        'new_books': library.books.filter(
            created_at__gte=thirty_days_ago
        ).count(),
    }
    
    # En popüler kitaplar
    popular_books = library.books.annotate(
        loan_count=Count('loans')
    ).order_by('-loan_count')[:10]
    
    # Kategori dağılımı
    category_stats = Category.objects.filter(
        bookcategory__book__library=library
    ).annotate(
        book_count=Count('bookcategory__book')
    ).order_by('-book_count')[:8]
    
    # Günlük kullanım deseni (son 7 gün)
    daily_usage = []
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        usage = LibraryUsagePattern.objects.filter(
            library=library,
            date=date
        ).aggregate(
            total_loans=Sum('loan_count'),
            total_returns=Sum('return_count'),
            total_users=Sum('user_count')
        )
        
        daily_usage.append({
            'date': date.strftime('%Y-%m-%d'),
            'loans': usage['total_loans'] or 0,
            'returns': usage['total_returns'] or 0,
            'users': usage['total_users'] or 0,
        })
    
    daily_usage.reverse()
    
    # Saatlik kullanım deseni
    hourly_usage = LibraryUsagePattern.objects.filter(
        library=library,
        date__gte=thirty_days_ago
    ).values('hour').annotate(
        avg_loans=Avg('loan_count'),
        avg_users=Avg('user_count')
    ).order_by('hour')
    
    context = {
        'library': library,
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'recent_activity': recent_activity,
        'popular_books': popular_books,
        'category_stats': category_stats,
        'daily_usage': json.dumps(daily_usage),
        'hourly_usage': list(hourly_usage),
    }
    
    return render(request, 'analytics/library_detail.html', context)

@login_required
def user_reading_analytics(request):
    """Kullanıcının kişisel okuma analitikleri."""
    # Kullanıcının okuma aktiviteleri
    reading_activities = ReadingActivity.objects.filter(user=request.user)
    
    # Genel istatistikler
    total_books_read = reading_activities.filter(is_completed=True).count()
    total_pages_read = reading_activities.aggregate(
        total=Sum('pages_read')
    )['total'] or 0
    total_reading_time = reading_activities.aggregate(
        total=Sum('reading_time_minutes')
    )['total'] or 0
    
    # Ortalama okuma hızı
    avg_reading_speed = reading_activities.filter(
        reading_speed__gt=0
    ).aggregate(
        avg=Avg('reading_speed')
    )['avg'] or 0
    
    # Aylık okuma istatistikleri (son 12 ay)
    monthly_reading = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - relativedelta(months=i)
        month_end = month_start + relativedelta(months=1)
        
        month_stats = reading_activities.filter(
            start_date__gte=month_start,
            start_date__lt=month_end
        ).aggregate(
            books=Count('id', filter=Q(is_completed=True)),
            pages=Sum('pages_read'),
            time=Sum('reading_time_minutes')
        )
        
        monthly_reading.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B'),
            'books': month_stats['books'] or 0,
            'pages': month_stats['pages'] or 0,
            'time': month_stats['time'] or 0,
        })
    
    monthly_reading.reverse()
    
    # Favori kategoriler
    user_loans = Loan.objects.filter(borrower=request.user)
    favorite_categories = Category.objects.filter(
        bookcategory__book__loans__in=user_loans
    ).annotate(
        loan_count=Count('bookcategory__book__loans')
    ).order_by('-loan_count')[:5]
    
    # Okuma hedefleri
    from books.models_goals import ReadingGoal
    active_goals = ReadingGoal.objects.filter(
        user=request.user,
        status='active'
    )
    
    completed_goals = ReadingGoal.objects.filter(
        user=request.user,
        status='completed'
    ).count()
    
    context = {
        'total_books_read': total_books_read,
        'total_pages_read': total_pages_read,
        'total_reading_time': total_reading_time,
        'avg_reading_speed': round(avg_reading_speed, 2),
        'monthly_reading': json.dumps(monthly_reading),
        'favorite_categories': favorite_categories,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'active_menu': 'analytics',
    }
    
    return render(request, 'analytics/user_reading.html', context)

@login_required
def book_popularity_report(request):
    """Kitap popülerlik raporu."""
    # Kullanıcının kütüphaneleri
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    # En popüler kitaplar
    popular_books = Book.objects.filter(
        library__in=user_libraries
    ).annotate(
        loan_count=Count('loans'),
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(loan_count__gt=0).order_by('-loan_count')[:20]
    
    # Trend olan kitaplar (son 30 gün)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    trending_books = Book.objects.filter(
        library__in=user_libraries,
        loans__loan_date__gte=thirty_days_ago
    ).annotate(
        recent_loans=Count('loans', filter=Q(loans__loan_date__gte=thirty_days_ago))
    ).filter(recent_loans__gt=0).order_by('-recent_loans')[:10]
    
    # Kategori performansı
    category_performance = Category.objects.filter(
        bookcategory__book__library__in=user_libraries
    ).annotate(
        total_books=Count('bookcategory__book'),
        total_loans=Count('bookcategory__book__loans'),
        avg_rating=Avg('bookcategory__book__reviews__rating')
    ).filter(total_books__gt=0).order_by('-total_loans')[:10]
    
    # Yazar performansı
    author_performance = Book.objects.filter(
        library__in=user_libraries
    ).values('author').annotate(
        book_count=Count('id'),
        loan_count=Count('loans'),
        avg_rating=Avg('reviews__rating')
    ).filter(loan_count__gt=0).order_by('-loan_count')[:10]
    
    context = {
        'popular_books': popular_books,
        'trending_books': trending_books,
        'category_performance': category_performance,
        'author_performance': author_performance,
        'active_menu': 'analytics',
    }
    
    return render(request, 'analytics/book_popularity.html', context)

@login_required
def library_comparison(request):
    """Kütüphane karşılaştırma raporu."""
    # Kullanıcının kütüphaneleri
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    if user_libraries.count() < 2:
        context = {
            'error': 'Karşılaştırma için en az 2 kütüphaneye sahip olmalısınız.',
            'active_menu': 'analytics',
        }
        return render(request, 'analytics/library_comparison.html', context)
    
    # Her kütüphane için istatistikler
    library_stats = []
    for library in user_libraries:
        stats = {
            'library': library,
            'total_books': library.books.count(),
            'available_books': library.books.filter(status='available').count(),
            'total_loans': Loan.objects.filter(book__library=library).count(),
            'active_loans': Loan.objects.filter(
                book__library=library,
                status__in=['active', 'overdue']
            ).count(),
            'utilization_rate': 0,
            'avg_loan_duration': 0,
        }
        
        # Kullanım oranı
        if stats['total_books'] > 0:
            stats['utilization_rate'] = (stats['active_loans'] / stats['total_books']) * 100
        
        # Ortalama ödünç verme süresi
        completed_loans = Loan.objects.filter(
            book__library=library,
            status='returned',
            return_date__isnull=False
        )
        
        if completed_loans.exists():
            total_duration = sum([
                (loan.return_date.date() - loan.loan_date.date()).days 
                for loan in completed_loans
            ])
            stats['avg_loan_duration'] = total_duration / completed_loans.count()
        
        library_stats.append(stats)
    
    # Son 30 günlük karşılaştırma
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_comparison = []
    
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        day_data = {'date': date.strftime('%Y-%m-%d')}
        
        for library in user_libraries:
            loan_count = Loan.objects.filter(
                book__library=library,
                loan_date__date=date
            ).count()
            day_data[f'library_{library.id}'] = loan_count
        
        daily_comparison.append(day_data)
    
    daily_comparison.reverse()
    
    context = {
        'user_libraries': user_libraries,
        'library_stats': library_stats,
        'daily_comparison': json.dumps(daily_comparison),
        'active_menu': 'analytics',
    }
    
    return render(request, 'analytics/library_comparison.html', context)

@login_required
def export_analytics_data(request):
    """Analitik verilerini dışa aktar."""
    export_type = request.GET.get('type', 'csv')
    data_type = request.GET.get('data', 'loans')
    
    # Kullanıcının kütüphaneleri
    user_libraries = Library.objects.filter(
        Q(owner=request.user) | Q(admins=request.user)
    ).distinct()
    
    if export_type == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{data_type}_analytics.csv"'
        
        writer = csv.writer(response)
        
        if data_type == 'loans':
            writer.writerow(['Kitap', 'Kütüphane', 'Ödünç Alan', 'Ödünç Tarihi', 'İade Tarihi', 'Durum'])
            
            loans = Loan.objects.filter(book__library__in=user_libraries).select_related(
                'book', 'book__library', 'borrower'
            )
            
            for loan in loans:
                writer.writerow([
                    loan.book.title,
                    loan.book.library.name,
                    loan.borrower.get_full_name() or loan.borrower.username,
                    loan.loan_date.strftime('%Y-%m-%d'),
                    loan.return_date.strftime('%Y-%m-%d') if loan.return_date else '',
                    loan.get_status_display()
                ])
        
        elif data_type == 'books':
            writer.writerow(['Başlık', 'Yazar', 'ISBN', 'Kütüphane', 'Durum', 'Toplam Ödünç', 'Ortalama Puan'])
            
            books = Book.objects.filter(library__in=user_libraries).annotate(
                loan_count=Count('loans'),
                avg_rating=Avg('reviews__rating')
            )
            
            for book in books:
                writer.writerow([
                    book.title,
                    book.author,
                    book.isbn or '',
                    book.library.name,
                    book.get_status_display(),
                    book.loan_count,
                    f"{book.avg_rating:.2f}" if book.avg_rating else ''
                ])
        
        return response
    
    elif export_type == 'json':
        # JSON export implementasyonu
        pass
    
    return JsonResponse({'error': 'Desteklenmeyen export türü'}, status=400)
