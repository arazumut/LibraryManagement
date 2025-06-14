from django.shortcuts import render
import json
import random
from datetime import datetime, timedelta

def dashboard(request):
    # Create dummy data for dashboard
    # Create dummy data for dashboard
    
    # Book statistics
    total_books = 8
    available_books = 5
    borrowed_books = 2
    reserved_books = 1
    
    # Calculate percentages
    available_percentage = int(available_books / total_books * 100)
    
    # Libraries
    total_libraries = 3
    user_libraries = 1
    user_library_books = 3
    
    # Loans
    total_loans = 2
    active_loans = 1
    
    # Loan trend data - last 7 days
    today = datetime.now().date()
    loan_dates = [(today - timedelta(days=i)).strftime('%d %b') for i in range(6, -1, -1)]
    loan_data = [random.randint(0, 3) for _ in range(7)]
    max_loan_value = max(loan_data) + 2
    
    # Requests
    pending_requests = 2
    request_success_rate = 75
    
    # Recent book activity
    recent_activities = [
        {
            'id': 1,
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'status': 'Available',
            'color': 'success'
        },
        {
            'id': 2,
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'status': 'Borrowed',
            'color': 'primary'
        },
        {
            'id': 3,
            'title': '1984',
            'author': 'George Orwell',
            'status': 'Available',
            'color': 'success'
        },
        {
            'id': 4,
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'status': 'Available',
            'color': 'success'
        },
        {
            'id': 5,
            'title': 'The Hobbit',
            'author': 'J.R.R. Tolkien',
            'status': 'Reserved',
            'color': 'warning'
        }
    ]
    
    # Popular books
    class DummyBook:
        def __init__(self, id, title, author, library_name, library_id, status, status_color, loan_count):
            self.id = id
            self.title = title
            self.author = author
            self.library = type('obj', (object,), {'name': library_name, 'id': library_id})
            self.status = status
            self.status_color = status_color
            self.loan_count = loan_count
            self.get_status_display = lambda: status.title()
    
    popular_books = [
        DummyBook(1, 'The Great Gatsby', 'F. Scott Fitzgerald', 'Main Library', 1, 'available', 'success', 15),
        DummyBook(7, 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'Science Library', 3, 'borrowed', 'primary', 12),
        DummyBook(2, 'To Kill a Mockingbird', 'Harper Lee', 'Main Library', 1, 'borrowed', 'primary', 10),
        DummyBook(6, 'A Brief History of Time', 'Stephen Hawking', 'Science Library', 3, 'available', 'success', 8),
        DummyBook(3, '1984', 'George Orwell', 'Main Library', 1, 'available', 'success', 7)
    ]
    
    # User loans
    class DummyLoan:
        def __init__(self, book_id, book_title, book_author, due_date, status, status_color):
            self.book = type('obj', (object,), {'id': book_id, 'title': book_title, 'author': book_author, 'cover_image': None})
            self.due_date = due_date
            self.status = status
            self.status_color = status_color
            self.get_status_display = lambda: status.title()
    
    user_loans = [
        DummyLoan(2, 'To Kill a Mockingbird', 'Harper Lee', datetime.now() + timedelta(days=7), 'active', 'primary'),
        DummyLoan(7, 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', datetime.now() + timedelta(days=3), 'active', 'primary'),
        DummyLoan(4, 'Pride and Prejudice', 'Jane Austen', datetime.now() - timedelta(days=3), 'returned', 'success'),
        DummyLoan(3, '1984', 'George Orwell', datetime.now() - timedelta(days=5), 'returned', 'success'),
        DummyLoan(6, 'A Brief History of Time', 'Stephen Hawking', datetime.now() - timedelta(days=7), 'returned', 'success')
    ]
    
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
