from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
import os
import sys
import django

# This is a hack to make Django models work without database connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

# Get the User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Creates dummy data for the dashboard'

    def handle(self, *args, **kwargs):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type='super_admin'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))

        # Create library admin
        if not User.objects.filter(username='librarian').exists():
            User.objects.create_user(
                username='librarian',
                email='librarian@example.com',
                password='librarian123',
                user_type='library_admin',
                first_name='Library',
                last_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('Library admin created successfully'))

        # Create reader
        if not User.objects.filter(username='reader').exists():
            User.objects.create_user(
                username='reader',
                email='reader@example.com',
                password='reader123',
                user_type='reader',
                first_name='Regular',
                last_name='Reader'
            )
            self.stdout.write(self.style.SUCCESS('Reader created successfully'))

        # Create dummy data for dashboard
        from libraries.models import Library
        from books.models import Book, BookRequest
        from loans.models import Loan

        # Create libraries
        admin_user = User.objects.get(username='admin')
        librarian_user = User.objects.get(username='librarian')
        reader_user = User.objects.get(username='reader')

        if Library.objects.count() == 0:
            main_library = Library.objects.create(
                name='Main Library',
                description='The main library with a vast collection of books.',
                owner=admin_user,
                address='123 Main Street, Anytown',
                phone='555-123-4567',
                email='main@library.com'
            )
            main_library.admins.add(librarian_user)
            
            fiction_library = Library.objects.create(
                name='Fiction Library',
                description='A library dedicated to fiction books.',
                owner=librarian_user,
                address='456 Novel Avenue, Bookville',
                phone='555-987-6543',
                email='fiction@library.com'
            )
            
            science_library = Library.objects.create(
                name='Science Library',
                description='A library with science and technology books.',
                owner=admin_user,
                address='789 Science Blvd, Techville',
                phone='555-456-7890',
                email='science@library.com'
            )
            
            self.stdout.write(self.style.SUCCESS('Libraries created successfully'))

        # Create books
        if Book.objects.count() == 0:
            # Books for Main Library
            main_library = Library.objects.get(name='Main Library')
            
            Book.objects.create(
                title='The Great Gatsby',
                author='F. Scott Fitzgerald',
                isbn='9780743273565',
                description='A novel about the mysteriously wealthy Jay Gatsby and his love for Daisy Buchanan.',
                library=main_library,
                status='available',
                publication_year=1925,
                publisher='Scribner',
                language='English',
                pages=180
            )
            
            Book.objects.create(
                title='To Kill a Mockingbird',
                author='Harper Lee',
                isbn='9780061120084',
                description='A novel about racial inequality through the eyes of a young girl in Alabama.',
                library=main_library,
                status='borrowed',
                publication_year=1960,
                publisher='HarperCollins',
                language='English',
                pages=281
            )
            
            Book.objects.create(
                title='1984',
                author='George Orwell',
                isbn='9780451524935',
                description='A dystopian novel about totalitarianism and mass surveillance.',
                library=main_library,
                status='available',
                publication_year=1949,
                publisher='Signet Classics',
                language='English',
                pages=328
            )
            
            # Books for Fiction Library
            fiction_library = Library.objects.get(name='Fiction Library')
            
            Book.objects.create(
                title='Pride and Prejudice',
                author='Jane Austen',
                isbn='9780141439518',
                description='A romantic novel about the Bennet family and Mr. Darcy.',
                library=fiction_library,
                status='available',
                publication_year=1813,
                publisher='Penguin Classics',
                language='English',
                pages=435
            )
            
            Book.objects.create(
                title='The Hobbit',
                author='J.R.R. Tolkien',
                isbn='9780547928227',
                description='A fantasy novel about the journey of Bilbo Baggins.',
                library=fiction_library,
                status='reserved',
                publication_year=1937,
                publisher='Houghton Mifflin Harcourt',
                language='English',
                pages=300
            )
            
            # Books for Science Library
            science_library = Library.objects.get(name='Science Library')
            
            Book.objects.create(
                title='A Brief History of Time',
                author='Stephen Hawking',
                isbn='9780553380163',
                description='A book about cosmology and the nature of the universe.',
                library=science_library,
                status='available',
                publication_year=1988,
                publisher='Bantam Books',
                language='English',
                pages=212
            )
            
            Book.objects.create(
                title='Sapiens: A Brief History of Humankind',
                author='Yuval Noah Harari',
                isbn='9780062316097',
                description='A book about the history and evolution of Homo sapiens.',
                library=science_library,
                status='borrowed',
                publication_year=2011,
                publisher='Harper',
                language='English',
                pages=443
            )
            
            Book.objects.create(
                title='The Selfish Gene',
                author='Richard Dawkins',
                isbn='9780198788607',
                description='A book on evolution from a gene-centered perspective.',
                library=science_library,
                status='available',
                publication_year=1976,
                publisher='Oxford University Press',
                language='English',
                pages=360
            )
            
            self.stdout.write(self.style.SUCCESS('Books created successfully'))

        # Create loans
        if Loan.objects.count() == 0:
            # Get borrowed books
            borrowed_books = Book.objects.filter(status='borrowed')
            
            for book in borrowed_books:
                due_date = timezone.now() + timezone.timedelta(days=14)
                
                Loan.objects.create(
                    book=book,
                    borrower=reader_user,
                    loaned_by=librarian_user,
                    loan_date=timezone.now() - timezone.timedelta(days=random.randint(1, 5)),
                    due_date=due_date,
                    status='active'
                )
            
            # Create some past loans
            available_books = Book.objects.filter(status='available')
            
            for i in range(min(3, available_books.count())):
                book = available_books[i]
                loan_date = timezone.now() - timezone.timedelta(days=random.randint(20, 30))
                due_date = loan_date + timezone.timedelta(days=14)
                return_date = loan_date + timezone.timedelta(days=random.randint(7, 13))
                
                Loan.objects.create(
                    book=book,
                    borrower=reader_user,
                    loaned_by=librarian_user,
                    loan_date=loan_date,
                    due_date=due_date,
                    return_date=return_date,
                    status='returned'
                )
            
            self.stdout.write(self.style.SUCCESS('Loans created successfully'))

        # Create book requests
        if BookRequest.objects.count() == 0:
            # Get available books
            available_books = Book.objects.filter(status='available')
            
            for i in range(min(2, available_books.count())):
                book = available_books[i]
                
                BookRequest.objects.create(
                    book=book,
                    requester=reader_user,
                    message=f'I would like to borrow {book.title}, please.',
                    status='pending',
                    requested_at=timezone.now() - timezone.timedelta(days=random.randint(1, 5))
                )
            
            # Create some approved requests
            for i in range(min(2, available_books.count())):
                if i + 2 < available_books.count():
                    book = available_books[i + 2]
                    
                    BookRequest.objects.create(
                        book=book,
                        requester=reader_user,
                        message=f'I would like to borrow {book.title}, please.',
                        status='approved',
                        requested_at=timezone.now() - timezone.timedelta(days=random.randint(6, 10)),
                        response_message='Your request has been approved. You can pick up the book.'
                    )
            
            self.stdout.write(self.style.SUCCESS('Book requests created successfully'))
        
        self.stdout.write(self.style.SUCCESS('All demo data created successfully!'))
