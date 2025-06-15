from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
import json
from datetime import datetime, timedelta
from django.utils import timezone

from books.models import Book, BookRequest
from libraries.models import Library
from loans.models import Loan

@login_required
def dashboard(request):
    # Book statistics
    total_books = Book.objects.count()
    available_books = Book.objects.filter(status='available').count()
    borrowed_books = Book.objects.filter(status='borrowed').count()
    reserved_books = Book.objects.filter(status='reserved').count()
    
    # Calculate percentages
    available_percentage = int(available_books / total_books * 100) if total_books > 0 else 0
    
    # Libraries
    total_libraries = Library.objects.count()
    user_libraries = Library.objects.filter(Q(owner=request.user) | Q(admins=request.user)).distinct().count()
    
    # Count books in user's libraries
    user_library_ids = Library.objects.filter(Q(owner=request.user) | Q(admins=request.user)).values_list('id', flat=True)
    user_library_books = Book.objects.filter(library_id__in=user_library_ids).count()
    
    # Loans
    total_loans = Loan.objects.filter(status__in=['active', 'overdue']).count()
    active_loans = Loan.objects.filter(borrower=request.user, status__in=['active', 'overdue']).count()
    
    # Loan trend data - last 7 days
    today = timezone.now().date()
    loan_dates = [(today - timedelta(days=i)).strftime('%d %b') for i in range(6, -1, -1)]
    
    # Get loan data for the past 7 days
    loan_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        loan_count = Loan.objects.filter(loan_date__date=date).count()
        loan_data.append(loan_count)
    
    max_loan_value = max(loan_data) + 2 if loan_data and max(loan_data) > 0 else 5
    
    # Book requests
    pending_requests = BookRequest.objects.filter(status='pending').count()
    
    # Calculate success rate (approved requests / total non-pending requests)
    total_completed_requests = BookRequest.objects.exclude(status='pending').count()
    approved_requests = BookRequest.objects.filter(status='approved').count()
    request_success_rate = int((approved_requests / total_completed_requests) * 100) if total_completed_requests > 0 else 0
    
    # Recent book activity - most recently updated books
    recent_books = Book.objects.order_by('-updated_at')[:5]
    recent_activities = []
    
    for book in recent_books:
        # Get status color based on book status
        color_map = {
            'available': 'success',
            'borrowed': 'primary',
            'reserved': 'warning',
            'maintenance': 'danger'
        }
        color = color_map.get(book.status, 'primary')
        
        recent_activities.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'status': dict(Book.STATUS_CHOICES).get(book.status),
            'color': color
        })
    
    # Popular books - books with the most loans
    # Manually create a list of book data with loan count
    popular_books_query = Book.objects.all().order_by('-id')[:5]  # Temporary get some books
    
    # Get loan counts for these books
    book_loan_counts = {}
    for book in popular_books_query:
        book_loan_counts[book.id] = book.loans.count()
    
    # Sort books by loan count
    sorted_book_ids = sorted(book_loan_counts.keys(), key=lambda x: book_loan_counts[x], reverse=True)
    
    # Create a list of books with loan count for template
    popular_books = []
    for book_id in sorted_book_ids:
        book = next((b for b in popular_books_query if b.id == book_id), None)
        if book:
            popular_books.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'library': book.library,
                'status': book.status,
                'status_color': book.status_color,
                'get_status_display': book.get_status_display(),
                'loan_count': book_loan_counts[book.id],
                'cover_image': book.cover_image
            })
    
    # User's active loans
    user_loans = Loan.objects.filter(
        borrower=request.user,
        status__in=['active', 'overdue']
    ).order_by('due_date')[:5]
    
    context = {
        'active_menu': 'dashboard',
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'reserved_books': reserved_books,
        'available_percentage': available_percentage,
        'total_libraries': total_libraries,
        'user_libraries': user_libraries,
        'user_library_books': user_library_books,
        'total_loans': total_loans,
        'active_loans': active_loans,
        'loan_dates': json.dumps(loan_dates),
        'loan_data': json.dumps(loan_data),
        'max_loan_value': max_loan_value,
        'pending_requests': pending_requests,
        'request_success_rate': request_success_rate,
        'recent_activities': recent_activities,
        'popular_books': popular_books,
        'user_loans': user_loans,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def search(request):
    """
    Kitapları ve kütüphaneleri arama fonksiyonu
    """
    query = request.GET.get('q', '')
    
    # Boş sorgu ise tüm sonuçları gösterme
    if not query:
        return render(request, 'search/results.html', {
            'active_menu': 'search',
            'query': query,
            'books': [],
            'libraries': [],
            'total_results': 0
        })
    
    # Kitapları ara
    books = Book.objects.filter(
        Q(title__icontains=query) | 
        Q(author__icontains=query) | 
        Q(isbn__icontains=query) |
        Q(description__icontains=query)
    ).distinct()
    
    # Kütüphaneleri ara
    libraries = Library.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(address__icontains=query)
    ).distinct()
    
    total_results = books.count() + libraries.count()
    
    context = {
        'active_menu': 'search',
        'query': query,
        'books': books,
        'libraries': libraries,
        'total_results': total_results
    }
    
    return render(request, 'search/results.html', context)
