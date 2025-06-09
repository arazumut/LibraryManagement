from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction

class Command(BaseCommand):
    help = 'Tüm örnek verileri oluşturur (kullanıcılar, kütüphaneler, kitaplar, ödünçler)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Tüm verileri temizle ve yeniden oluştur',
        )
        parser.add_argument(
            '--no-loans',
            action='store_true',
            help='Ödünç kayıtları oluşturma',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '🚀 Kütüphane Yönetim Sistemi - Örnek Veriler Oluşturuluyor...\n'
            )
        )
        
        clear_data = options['clear']
        create_loans = not options['no_loans']
        
        try:
            with transaction.atomic():
                # 1. Kullanıcıları oluştur
                self.stdout.write('👥 Kullanıcılar oluşturuluyor...')
                call_command('create_sample_users', clear=clear_data, verbosity=1)
                
                # 2. Kütüphaneleri oluştur
                self.stdout.write('\n📚 Kütüphaneler oluşturuluyor...')
                call_command('create_sample_libraries', clear=clear_data, verbosity=1)
                
                # 3. Kitapları, istekleri ve notları oluştur
                self.stdout.write('\n📖 Kitaplar, istekler ve notlar oluşturuluyor...')
                call_command('create_sample_books', clear=clear_data, verbosity=1)
                
                # 4. Ödünç kayıtları oluştur (opsiyonel)
                if create_loans:
                    self.stdout.write('\n📋 Ödünç kayıtları oluşturuluyor...')
                    call_command('create_sample_loans', clear=clear_data, verbosity=1)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n🎉 Tüm örnek veriler başarıyla oluşturuldu!\n'
                        '\n📋 Giriş bilgileri:\n'
                        '  • Süper Admin: super_admin / super_admin\n'
                        '  • Kütüphane Yöneticisi: ahmet_yonetici / ahmet_yonetici\n'
                        '  • Kütüphane Yöneticisi: ayse_yonetici / ayse_yonetici\n'
                        '  • Okuyucu: mehmet_okuyucu / mehmet_okuyucu\n'
                        '  • Okuyucu: fatma_okuyucu / fatma_okuyucu\n'
                        '\n🌐 Admin paneline gitmek için: python manage.py runserver\n'
                        '   Ardından http://127.0.0.1:8000/admin/ adresini ziyaret edin\n'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'\n❌ Hata oluştu: {str(e)}\n'
                    'Lütfen veritabanı migrasyonlarının yapıldığından emin olun:\n'
                    '  python manage.py makemigrations\n'
                    '  python manage.py migrate\n'
                )
            )
            raise
