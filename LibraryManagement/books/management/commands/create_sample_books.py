from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from books.models import Book, BookRequest, BookNote
from libraries.models import Library
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Örnek kitaplar, istekler ve notlar oluşturur'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Mevcut kitapları, istekleri ve notları temizle',
        )
        parser.add_argument(
            '--books-only',
            action='store_true',
            help='Sadece kitapları oluştur, istek ve not oluşturma',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            book_count = Book.objects.count()
            request_count = BookRequest.objects.count()
            note_count = BookNote.objects.count()
            
            Book.objects.all().delete()
            BookRequest.objects.all().delete()
            BookNote.objects.all().delete()
            
            self.stdout.write(
                self.style.WARNING(
                    f'{book_count} kitap, {request_count} istek, {note_count} not silindi.'
                )
            )
        
        # Kütüphaneleri al
        libraries = Library.objects.all()
        if not libraries.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Kütüphane bulunamadı! Önce kütüphaneleri oluşturun: '
                    'python manage.py create_sample_libraries'
                )
            )
            return
        
        # Örnek kitaplar
        sample_books = [
            # Türk Edebiyatı
            {'title': 'Saatleri Ayarlama Enstitüsü', 'author': 'Ahmet Hamdi Tanpınar', 'isbn': '9789750719851'},
            {'title': 'Tutunamayanlar', 'author': 'Oğuz Atay', 'isbn': '9789750718922'},
            {'title': 'Kürk Mantolu Madonna', 'author': 'Sabahattin Ali', 'isbn': '9789750718915'},
            {'title': 'İçimizdeki Şeytan', 'author': 'Sabahattin Ali', 'isbn': '9789750718908'},
            {'title': 'Sinekli Bakkal', 'author': 'Halide Edib Adıvar', 'isbn': '9789750718939'},
            
            # Dünya Edebiyatı
            {'title': '1984', 'author': 'George Orwell', 'isbn': '9780451524935'},
            {'title': 'Hayvan Çiftliği', 'author': 'George Orwell', 'isbn': '9780451526342'},
            {'title': 'Suç ve Ceza', 'author': 'Fyodor Dostoyevski', 'isbn': '9780486454115'},
            {'title': 'Karamazov Kardeşler', 'author': 'Fyodor Dostoyevski', 'isbn': '9780486437910'},
            {'title': 'Yüzüklerin Efendisi: Yüzük Kardeşliği', 'author': 'J.R.R. Tolkien', 'isbn': '9780547928210'},
            
            # Bilim ve Felsefe
            {'title': 'Sapiens: İnsan Türünün Kısa Tarihi', 'author': 'Yuval Noah Harari', 'isbn': '9780062316097'},
            {'title': 'Homo Deus: Yarının Kısa Tarihi', 'author': 'Yuval Noah Harari', 'isbn': '9780062464316'},
            {'title': 'Büyük Tasarım', 'author': 'Stephen Hawking', 'isbn': '9780553819229'},
            {'title': 'Zamanın Kısa Tarihi', 'author': 'Stephen Hawking', 'isbn': '9780553380163'},
            
            # Çocuk Kitapları
            {'title': 'Küçük Prens', 'author': 'Antoine de Saint-Exupéry', 'isbn': '9780156012195'},
            {'title': 'Harry Potter ve Felsefe Taşı', 'author': 'J.K. Rowling', 'isbn': '9780439708180'},
            {'title': 'Matilda', 'author': 'Roald Dahl', 'isbn': '9780142410370'},
            {'title': 'Charlie ve Çikolata Fabrikası', 'author': 'Roald Dahl', 'isbn': '9780142410318'},
            
            # Bilim ve Teknoloji
            {'title': 'Python Programlama', 'author': 'Mark Lutz', 'isbn': '9781449355739'},
            {'title': 'Clean Code', 'author': 'Robert C. Martin', 'isbn': '9780132350884'},
            {'title': 'Algoritmalar: Tasarım ve Analiz', 'author': 'Thomas H. Cormen', 'isbn': '9780262033848'},
            {'title': 'Yapay Zeka: Modern Yaklaşım', 'author': 'Stuart Russell', 'isbn': '9780136042594'},
            
            # Tarih
            {'title': 'Nutuk', 'author': 'Mustafa Kemal Atatürk', 'isbn': '9789750718984'},
            {'title': 'Osmanlı Tarihi', 'author': 'Halil İnalcık', 'isbn': '9789750718977'},
            {'title': 'İkinci Dünya Savaşı', 'author': 'Antony Beevor', 'isbn': '9780316023740'},
            
            # Psikoloji ve Kişisel Gelişim
            {'title': 'Düşünme, Hızlı ve Yavaş', 'author': 'Daniel Kahneman', 'isbn': '9780374533557'},
            {'title': 'Atomik Alışkanlıklar', 'author': 'James Clear', 'isbn': '9780735211292'},
            {'title': 'İnsanın Anlam Arayışı', 'author': 'Viktor E. Frankl', 'isbn': '9780807014295'},
        ]
        
        # Kitap açıklamaları
        descriptions = [
            "Çok etkileyici ve düşündürücü bir eser.",
            "Bu kitap okuyuculara yeni perspektifler sunuyor.",
            "Yazarın üslubu oldukça akıcı ve sürükleyici.",
            "Konuyla ilgili derinlemesine bilgi edinmek isteyenler için ideal.",
            "Hem eğlenceli hem de öğretici bir okuma deneyimi.",
            "Klasik eserlerden biri, mutlaka okunmalı.",
            "Modern yaklaşımlarla ele alınmış güncel bir çalışma.",
            "Okuyucuları farklı dünyalara götüren büyüleyici bir hikaye.",
        ]
        
        created_books = 0
        
        with transaction.atomic():
            for book_data in sample_books:
                title = book_data['title']
                
                # Kitap zaten varsa atla
                if Book.objects.filter(title=title).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Kitap zaten mevcut: {title}')
                    )
                    continue
                
                # Rastgele bir kütüphane seç
                library = random.choice(libraries)
                
                book = Book.objects.create(
                    title=title,
                    author=book_data['author'],
                    isbn=book_data['isbn'],
                    library=library,
                    description=random.choice(descriptions),
                    is_available=random.choice([True, True, True, False])  # %75 uygun
                )
                
                created_books += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Kitap: {title} - {book_data["author"]} ({library.name})'
                    )
                )
        
        if created_books > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nToplam {created_books} kitap oluşturuldu!')
            )
        
        # Sadece kitap oluştur seçeneği varsa burada dur
        if options['books_only']:
            return
        
        # Kitap istekleri ve notlar oluştur
        self.create_book_requests()
        self.create_book_notes()
    
    def create_book_requests(self):
        """Örnek kitap istekleri oluştur"""
        readers = User.objects.filter(user_type=User.READER)
        books = Book.objects.all()
        
        if not readers.exists() or not books.exists():
            return
        
        # Rastgele kitap istekleri oluştur
        created_requests = 0
        
        for _ in range(min(15, len(books) * len(readers) // 3)):
            reader = random.choice(readers)
            book = random.choice(books)
            
            # Aynı kullanıcı aynı kitap için tekrar istek yapmış mı?
            if BookRequest.objects.filter(book=book, requester=reader).exists():
                continue
            
            status = random.choice([
                BookRequest.STATUS_PENDING,
                BookRequest.STATUS_APPROVED,
                BookRequest.STATUS_REJECTED,
            ])
            
            BookRequest.objects.create(
                book=book,
                requester=reader,
                status=status,
                message=f"{book.title} kitabını okumak istiyorum."
            )
            created_requests += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {created_requests} kitap isteği oluşturuldu!')
        )
    
    def create_book_notes(self):
        """Örnek kitap notları oluştur"""
        users = User.objects.all()
        books = Book.objects.all()
        
        if not users.exists() or not books.exists():
            return
        
        sample_notes = [
            "Bu kitap gerçekten çok güzel, herkese tavsiye ederim!",
            "Yazarın üslubu beni çok etkiledi, harika bir eser.",
            "Konuyla ilgili çok şey öğrendim, çok faydalı.",
            "Okunması gereken klasiklerden biri.",
            "Biraz ağır bir kitap ama sonunda değiyor.",
            "İlginç yaklaşımlar sunuyor, farklı perspektifler kazandırıyor.",
            "Akıcı bir dille yazılmış, kolay okunuyor.",
            "Düşündürücü ve etkileyici bir hikaye.",
            "Bu konuda yazılmış en iyi kitaplardan biri.",
            "Tekrar tekrar okumaya değer bir eser.",
        ]
        
        created_notes = 0
        
        # Her kitap için 1-3 arası not oluştur
        for book in books:
            note_count = random.randint(1, 3)
            used_users = []
            
            for _ in range(note_count):
                available_users = [u for u in users if u not in used_users]
                if not available_users:
                    break
                
                user = random.choice(available_users)
                used_users.append(user)
                
                BookNote.objects.create(
                    book=book,
                    user=user,
                    content=random.choice(sample_notes),
                    is_private=random.choice([True, False])
                )
                created_notes += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {created_notes} kitap notu oluşturuldu!')
        )
