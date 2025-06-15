import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from libraries.models import Library
from books.models import Book, BookRequest, BookNote
from loans.models import Loan
from faker import Faker

User = get_user_model()
fake = Faker(['tr_TR', 'en_US'])

class Command(BaseCommand):
    help = 'Kütüphane yönetim sistemi için örnek veriler oluşturur'

    def handle(self, *args, **options):
        self.stdout.write('Örnek veriler oluşturuluyor...')
        
        # Kullanıcılar oluşturalım
        self.create_users()
        
        # Kütüphaneler oluşturalım
        self.create_libraries()
        
        # Kitaplar oluşturalım
        self.create_books()
        
        # Ödünç vermeler oluşturalım
        self.create_loans()
        
        # Kitap istekleri oluşturalım
        self.create_book_requests()
        
        # Kitap notları oluşturalım
        self.create_book_notes()
        
        self.stdout.write(self.style.SUCCESS('Örnek veriler başarıyla oluşturuldu!'))
    
    def create_users(self):
        self.stdout.write('Kullanıcılar oluşturuluyor...')
        
        # Süper yönetici oluştur (eğer yoksa)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword',
                user_type='super_admin',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Süper yönetici oluşturuldu: admin'))
        
        # Kütüphane yöneticileri oluştur
        library_admins = []
        for i in range(5):
            username = f'libadmin{i+1}'
            if not User.objects.filter(username=username).exists():
                admin = User.objects.create_user(
                    username=username,
                    email=f'libadmin{i+1}@example.com',
                    password=f'password{i+1}',
                    user_type='library_admin',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone_number=fake.phone_number(),
                    address=fake.address()
                )
                library_admins.append(admin)
                self.stdout.write(f'Kütüphane yöneticisi oluşturuldu: {username}')
        
        # Normal okuyucular oluştur
        readers = []
        for i in range(20):
            username = f'reader{i+1}'
            if not User.objects.filter(username=username).exists():
                reader = User.objects.create_user(
                    username=username,
                    email=f'reader{i+1}@example.com',
                    password=f'password{i+1}',
                    user_type='reader',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone_number=fake.phone_number(),
                    address=fake.address()
                )
                readers.append(reader)
                self.stdout.write(f'Okuyucu oluşturuldu: {username}')
    
    def create_libraries(self):
        self.stdout.write('Kütüphaneler oluşturuluyor...')
        
        # Kütüphane yöneticilerini al
        library_admins = User.objects.filter(user_type='library_admin')
        
        if not library_admins.exists():
            self.stdout.write(self.style.WARNING('Kütüphane yöneticisi bulunamadı!'))
            return
            
        # Kütüphaneler oluştur
        library_names = [
            'Merkez Kütüphanesi',
            'Bilim Kütüphanesi',
            'Edebiyat Kütüphanesi',
            'Çocuk Kütüphanesi',
            'Tarih Kütüphanesi',
            'Teknoloji Kütüphanesi',
            'Sanat Kütüphanesi'
        ]
        
        for i, name in enumerate(library_names):
            admin = library_admins[i % library_admins.count()]
            
            if not Library.objects.filter(name=name).exists():
                library = Library.objects.create(
                    name=name,
                    description=fake.paragraph(),
                    owner=admin,
                    address=fake.address(),
                    phone=fake.phone_number(),
                    email=fake.email()
                )
                
                # Her kütüphaneye 1-3 yönetici ata
                other_admins = list(library_admins.exclude(id=admin.id))
                num_admins = min(random.randint(1, 3), len(other_admins))
                for j in range(num_admins):
                    library.admins.add(other_admins[j])
                
                self.stdout.write(f'Kütüphane oluşturuldu: {name}')
    
    def create_books(self):
        self.stdout.write('Kitaplar oluşturuluyor...')
        
        libraries = Library.objects.all()
        if not libraries.exists():
            self.stdout.write(self.style.WARNING('Kütüphane bulunamadı!'))
            return
        
        # Türk ve dünya klasiklerinden kitaplar
        books_data = [
            {'title': 'İnce Memed', 'author': 'Yaşar Kemal', 'year': 1955, 'publisher': 'Yapı Kredi Yayınları', 'language': 'Türkçe', 'pages': 420},
            {'title': 'Tutunamayanlar', 'author': 'Oğuz Atay', 'year': 1971, 'publisher': 'İletişim Yayınları', 'language': 'Türkçe', 'pages': 724},
            {'title': 'Kürk Mantolu Madonna', 'author': 'Sabahattin Ali', 'year': 1943, 'publisher': 'Yapı Kredi Yayınları', 'language': 'Türkçe', 'pages': 160},
            {'title': 'Mai ve Siyah', 'author': 'Halit Ziya Uşaklıgil', 'year': 1897, 'publisher': 'Can Yayınları', 'language': 'Türkçe', 'pages': 336},
            {'title': 'Çalıkuşu', 'author': 'Reşat Nuri Güntekin', 'year': 1922, 'publisher': 'İnkılap Kitabevi', 'language': 'Türkçe', 'pages': 544},
            {'title': 'Ulysses', 'author': 'James Joyce', 'year': 1922, 'publisher': 'Shakespeare and Company', 'language': 'İngilizce', 'pages': 730},
            {'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'year': 1813, 'publisher': 'T. Egerton', 'language': 'İngilizce', 'pages': 432},
            {'title': 'Crime and Punishment', 'author': 'Fyodor Dostoevsky', 'year': 1866, 'publisher': 'The Russian Messenger', 'language': 'Rusça', 'pages': 576},
            {'title': 'One Hundred Years of Solitude', 'author': 'Gabriel García Márquez', 'year': 1967, 'publisher': 'Harper & Row', 'language': 'İspanyolca', 'pages': 417},
            {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'year': 1925, 'publisher': 'Charles Scribner\'s Sons', 'language': 'İngilizce', 'pages': 180},
            {'title': 'Don Quixote', 'author': 'Miguel de Cervantes', 'year': 1605, 'publisher': 'Francisco de Robles', 'language': 'İspanyolca', 'pages': 863},
            {'title': 'The Alchemist', 'author': 'Paulo Coelho', 'year': 1988, 'publisher': 'HarperOne', 'language': 'Portekizce', 'pages': 163},
            {'title': '1984', 'author': 'George Orwell', 'year': 1949, 'publisher': 'Secker & Warburg', 'language': 'İngilizce', 'pages': 328},
            {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'year': 1960, 'publisher': 'J. B. Lippincott & Co.', 'language': 'İngilizce', 'pages': 281},
            {'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupéry', 'year': 1943, 'publisher': 'Reynal & Hitchcock', 'language': 'Fransızca', 'pages': 96},
            {'title': 'War and Peace', 'author': 'Leo Tolstoy', 'year': 1869, 'publisher': 'The Russian Messenger', 'language': 'Rusça', 'pages': 1225},
            {'title': 'The Odyssey', 'author': 'Homer', 'year': 800, 'publisher': 'Ancient Text', 'language': 'Antik Yunanca', 'pages': 442, 'description': 'M.Ö. 800 civarında yazılmıştır.'},
            {'title': 'Madame Bovary', 'author': 'Gustave Flaubert', 'year': 1856, 'publisher': 'Revue de Paris', 'language': 'Fransızca', 'pages': 432},
            {'title': 'The Brothers Karamazov', 'author': 'Fyodor Dostoevsky', 'year': 1880, 'publisher': 'The Russian Messenger', 'language': 'Rusça', 'pages': 824},
            {'title': 'Les Misérables', 'author': 'Victor Hugo', 'year': 1862, 'publisher': 'A. Lacroix, Verboeckhoven & Cie', 'language': 'Fransızca', 'pages': 1232},
            {'title': 'Hamlet', 'author': 'William Shakespeare', 'year': 1603, 'publisher': 'First Quarto', 'language': 'İngilizce', 'pages': 342},
            {'title': 'The Divine Comedy', 'author': 'Dante Alighieri', 'year': 1320, 'publisher': 'Ancient Text', 'language': 'İtalyanca', 'pages': 798},
            {'title': 'Moby Dick', 'author': 'Herman Melville', 'year': 1851, 'publisher': 'Harper & Brothers', 'language': 'İngilizce', 'pages': 635},
            {'title': 'Anna Karenina', 'author': 'Leo Tolstoy', 'year': 1877, 'publisher': 'The Russian Messenger', 'language': 'Rusça', 'pages': 864},
            {'title': 'The Iliad', 'author': 'Homer', 'year': 750, 'publisher': 'Ancient Text', 'language': 'Antik Yunanca', 'pages': 683, 'description': 'M.Ö. 750 civarında yazılmıştır.'},
            {'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'year': 1951, 'publisher': 'Little, Brown and Company', 'language': 'İngilizce', 'pages': 277},
            {'title': 'The Stranger', 'author': 'Albert Camus', 'year': 1942, 'publisher': 'Éditions Gallimard', 'language': 'Fransızca', 'pages': 159},
            {'title': 'Jane Eyre', 'author': 'Charlotte Brontë', 'year': 1847, 'publisher': 'Smith, Elder & Co.', 'language': 'İngilizce', 'pages': 624},
            {'title': 'The Metamorphosis', 'author': 'Franz Kafka', 'year': 1915, 'publisher': 'Kurt Wolff Verlag', 'language': 'Almanca', 'pages': 201},
            {'title': 'The Count of Monte Cristo', 'author': 'Alexandre Dumas', 'year': 1844, 'publisher': 'Journal des débats', 'language': 'Fransızca', 'pages': 1276}
        ]
        
        # Her kütüphane için kitaplar oluştur
        for library in libraries:
            for book_data in books_data:
                # Her kütüphaneye her kitaptan 1-3 kopya ekle
                copies = random.randint(1, 3)
                for i in range(copies):
                    # Her kopyanın %80 ihtimalle mevcut olması, %20 ihtimalle ödünç verilmiş olması
                    status = 'available' if random.random() < 0.8 else 'borrowed'
                    
                    isbn = f"978-{random.randint(0, 9)}-{random.randint(100, 999)}-{random.randint(10000, 99999)}-{random.randint(0, 9)}"
                    
                    # Açıklama varsa onu kullan, yoksa random oluştur
                    description = book_data.get('description', fake.paragraph())
                    
                    book = Book.objects.create(
                        title=book_data['title'],
                        author=book_data['author'],
                        isbn=isbn,
                        description=description,
                        library=library,
                        status=status,
                        publication_year=book_data['year'],
                        publisher=book_data['publisher'],
                        language=book_data['language'],
                        pages=book_data['pages']
                    )
            
            self.stdout.write(f'{library.name} için kitaplar oluşturuldu')
    
    def create_loans(self):
        self.stdout.write('Ödünç vermeler oluşturuluyor...')
        
        # Kitaplar ve kullanıcıları al
        books = Book.objects.all()
        admins = User.objects.filter(user_type__in=['super_admin', 'library_admin'])
        readers = User.objects.filter(user_type='reader')
        
        if not books.exists() or not readers.exists() or not admins.exists():
            self.stdout.write(self.style.WARNING('Kitap, okuyucu veya yönetici bulunamadı!'))
            return
        
        # Mevcut durumu borrowed olan kitapları al
        borrowed_books = Book.objects.filter(status='borrowed')
        
        # Eğer borrowed durumunda kitap varsa, bunlar için aktif ödünç vermeler oluştur
        for book in borrowed_books:
            # Rastgele bir okuyucu seç
            borrower = random.choice(readers)
            # Rastgele bir yönetici seç
            loaned_by = random.choice(admins.filter(administered_libraries=book.library) | 
                                      User.objects.filter(owned_libraries=book.library))
            
            # Ödünç verme tarihi: 1-30 gün önce
            loan_date = timezone.now() - timedelta(days=random.randint(1, 30))
            # İade tarihi: Ödünç verme tarihinden 14 gün sonra
            due_date = loan_date + timedelta(days=14)
            
            # Durumunu belirle: %70 aktif, %30 gecikmiş
            status = 'active'
            if due_date < timezone.now():
                status = 'overdue'
            
            # Ödünç verme oluştur
            Loan.objects.create(
                book=book,
                borrower=borrower,
                loaned_by=loaned_by,
                loan_date=loan_date,
                due_date=due_date,
                status=status,
                notes=fake.paragraph() if random.random() < 0.3 else None
            )
            
            self.stdout.write(f'Aktif ödünç verme oluşturuldu: {book.title} -> {borrower.username}')
        
        # Rastgele tamamlanmış ödünç vermeler oluştur
        for _ in range(50):
            # Mevcut durumu available olan kitapları al
            available_books = Book.objects.filter(status='available')
            
            if not available_books.exists():
                break
                
            # Rastgele bir kitap seç
            book = random.choice(available_books)
            # Rastgele bir okuyucu seç
            borrower = random.choice(readers)
            # Rastgele bir yönetici seç
            admin_options = list(admins.filter(administered_libraries=book.library)) + list(User.objects.filter(owned_libraries=book.library))
            loaned_by = random.choice(admin_options) if admin_options else random.choice(admins)
            
            # Ödünç verme tarihi: 1-60 gün önce
            loan_date = timezone.now() - timedelta(days=random.randint(30, 90))
            # İade tarihi: Ödünç verme tarihinden 14 gün sonra
            due_date = loan_date + timedelta(days=14)
            # Gerçek iade tarihi: İade tarihinden 1-3 gün önce veya 1-5 gün sonra
            return_date = due_date + timedelta(days=random.randint(-3, 5))
            
            # Ödünç verme oluştur
            Loan.objects.create(
                book=book,
                borrower=borrower,
                loaned_by=loaned_by,
                loan_date=loan_date,
                due_date=due_date,
                return_date=return_date,
                status='returned',
                notes=fake.paragraph() if random.random() < 0.3 else None
            )
            
            self.stdout.write(f'Tamamlanmış ödünç verme oluşturuldu: {book.title} -> {borrower.username}')
    
    def create_book_requests(self):
        self.stdout.write('Kitap istekleri oluşturuluyor...')
        
        books = Book.objects.all()
        readers = User.objects.filter(user_type='reader')
        
        if not books.exists() or not readers.exists():
            self.stdout.write(self.style.WARNING('Kitap veya okuyucu bulunamadı!'))
            return
        
        # Tüm statüslerden rastgele kitap istekleri oluştur
        statuses = ['pending', 'approved', 'rejected', 'cancelled']
        
        for _ in range(30):
            book = random.choice(books)
            requester = random.choice(readers)
            status = random.choice(statuses)
            
            # İstek tarihi: 1-30 gün önce
            requested_at = timezone.now() - timedelta(days=random.randint(1, 30))
            
            BookRequest.objects.create(
                book=book,
                requester=requester,
                message=fake.paragraph() if random.random() < 0.7 else None,
                status=status,
                requested_at=requested_at,
                response_message=fake.paragraph() if status in ['approved', 'rejected'] and random.random() < 0.8 else None
            )
            
            self.stdout.write(f'Kitap isteği oluşturuldu: {book.title} -> {requester.username} ({status})')
    
    def create_book_notes(self):
        self.stdout.write('Kitap notları oluşturuluyor...')
        
        books = Book.objects.all()
        readers = User.objects.filter(user_type='reader')
        
        if not books.exists() or not readers.exists():
            self.stdout.write(self.style.WARNING('Kitap veya okuyucu bulunamadı!'))
            return
        
        # Rastgele kitap notları oluştur
        for _ in range(50):
            book = random.choice(books)
            user = random.choice(readers)
            visibility = random.choice(['private', 'public'])
            
            BookNote.objects.create(
                book=book,
                user=user,
                note=fake.paragraph(),
                visibility=visibility,
                created_at=timezone.now() - timedelta(days=random.randint(1, 60))
            )
            
            self.stdout.write(f'Kitap notu oluşturuldu: {book.title} -> {user.username} ({visibility})')
