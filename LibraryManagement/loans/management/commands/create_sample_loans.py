from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from loans.models import Loan
from books.models import Book
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Örnek ödünç alma kayıtları oluşturur'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Mevcut ödünç kayıtlarını temizle',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            # Önce tüm kitapları uygun yap
            Book.objects.all().update(is_available=True)
            
            deleted_count = Loan.objects.count()
            Loan.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'{deleted_count} ödünç kaydı silindi.')
            )
        
        # Okuyucuları ve kitapları al
        readers = User.objects.filter(user_type=User.READER)
        library_admins = User.objects.filter(user_type=User.LIBRARY_ADMIN)
        books = Book.objects.all()
        
        if not readers.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Okuyucu bulunamadı! Önce kullanıcıları oluşturun.'
                )
            )
            return
        
        if not library_admins.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Kütüphane yöneticisi bulunamadı! Önce kullanıcıları oluşturun.'
                )
            )
            return
        
        if not books.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Kitap bulunamadı! Önce kitapları oluşturun.'
                )
            )
            return
        
        created_loans = 0
        now = timezone.now()
        
        with transaction.atomic():
            # Her okuyucu için 1-4 arası ödünç kayıt oluştur
            for reader in readers:
                loan_count = random.randint(1, 4)
                used_books = []
                
                for _ in range(loan_count):
                    # Kullanılmamış kitapları al
                    available_books = [b for b in books if b not in used_books]
                    if not available_books:
                        break
                    
                    book = random.choice(available_books)
                    used_books.append(book)
                    
                    # Kitabın kütüphanesi sahibini ödünç veren olarak ata
                    lender = book.library.owner
                    
                    # Rastgele geçmiş bir tarih seç (son 60 gün)
                    start_date = now - timedelta(days=random.randint(1, 60))
                    due_date = start_date + timedelta(days=14)  # 14 gün ödünç süresi
                    
                    # %70 ihtimalle kitap iade edilmiş olsun
                    is_returned = random.choice([True, True, True, False])
                    
                    returned_date = None
                    if is_returned:
                        # İade tarihi son tarihten önce veya sonra olabilir
                        days_offset = random.randint(-5, 10)  # -5 ile +10 gün arası
                        returned_date = due_date + timedelta(days=days_offset)
                        # İade tarihi başlangıç tarihinden önce olamaz
                        if returned_date < start_date:
                            returned_date = start_date + timedelta(days=1)
                    
                    # Ödünç kaydını oluştur
                    loan = Loan(
                        book=book,
                        borrower=reader,
                        lender=lender,
                        start_date=start_date,
                        due_date=due_date,
                        returned_date=returned_date,
                        notes=self.get_random_note()
                    )
                    
                    # save() metodunu çağırmadan önce kitap durumunu manuel güncelle
                    # çünkü save() metodu otomatik olarak is_available=False yapar
                    loan.save()
                    
                    # Eğer kitap iade edilmişse kitabı uygun yap
                    if returned_date:
                        book.is_available = True
                        book.save()
                    else:
                        # Iade edilmemişse kitap uygun değil
                        book.is_available = False
                        book.save()
                    
                    created_loans += 1
                    
                    status = "İade Edildi" if returned_date else "Ödünçte"
                    overdue = ""
                    if not returned_date and loan.is_overdue:
                        overdue = " (Gecikmiş)"
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {reader.get_full_name()} -> {book.title} [{status}{overdue}]'
                        )
                    )
        
        if created_loans > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nToplam {created_loans} ödünç kaydı oluşturuldu!')
            )
            
            # İstatistikler
            total_loans = Loan.objects.count()
            active_loans = Loan.objects.filter(returned_date__isnull=True).count()
            overdue_loans = Loan.objects.filter(
                returned_date__isnull=True,
                due_date__lt=timezone.now()
            ).count()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n📊 İstatistikler:\n'
                    f'  • Toplam ödünç: {total_loans}\n'
                    f'  • Aktif ödünç: {active_loans}\n'
                    f'  • Gecikmiş: {overdue_loans}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Hiç ödünç kaydı oluşturulmadı.')
            )
    
    def get_random_note(self):
        """Rastgele not döndür"""
        notes = [
            "Kitap çok iyi durumda.",
            "Okuyucu düzenli bir kişi.",
            "İlk kez ödünç alıyor.",
            "Daha önce de ödünç almıştı.",
            "Kitabı çok beğendi.",
            "Önerilerde bulundu.",
            "",  # Boş not
            "",
            "",
        ]
        return random.choice(notes)
