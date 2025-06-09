from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from libraries.models import Library

User = get_user_model()

class Command(BaseCommand):
    help = 'Örnek kütüphaneler oluşturur'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Mevcut kütüphaneleri temizle',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            deleted_count = Library.objects.count()
            Library.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'{deleted_count} kütüphane silindi.')
            )
        
        # Kütüphane yöneticilerini al
        library_admins = User.objects.filter(user_type=User.LIBRARY_ADMIN)
        
        if not library_admins.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Kütüphane yöneticisi bulunamadı! Önce kullanıcıları oluşturun: '
                    'python manage.py create_sample_users'
                )
            )
            return
        
        # Örnek kütüphaneler
        sample_libraries = [
            {
                'name': 'Merkez Kütüphanesi',
                'description': 'Şehrin en büyük ve kapsamlı kütüphanesi. Genel koleksiyona sahip.',
                'owner_username': 'ahmet_yonetici',
            },
            {
                'name': 'Üniversite Kütüphanesi',
                'description': 'Akademik kaynaklara odaklanan üniversite kütüphanesi.',
                'owner_username': 'ayse_yonetici',
            },
            {
                'name': 'Çocuk Kütüphanesi',
                'description': 'Çocuklar için özel olarak tasarlanmış kütüphane.',
                'owner_username': 'ahmet_yonetici',
            },
            {
                'name': 'Bilim ve Teknoloji Kütüphanesi',
                'description': 'Bilim, teknoloji ve mühendislik alanlarında uzmanlaşmış kütüphane.',
                'owner_username': 'ayse_yonetici',
            },
            {
                'name': 'Edebiyat Kütüphanesi',
                'description': 'Türk ve dünya edebiyatı eserlerine odaklanan özel kütüphane.',
                'owner_username': 'ahmet_yonetici',
            },
        ]
        
        created_count = 0
        
        with transaction.atomic():
            for library_data in sample_libraries:
                name = library_data['name']
                
                # Kütüphane zaten varsa atla
                if Library.objects.filter(name=name).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Kütüphane zaten mevcut: {name}')
                    )
                    continue
                
                # Sahip kullanıcıyı bul
                try:
                    owner = User.objects.get(username=library_data['owner_username'])
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Sahip kullanıcı bulunamadı: {library_data["owner_username"]}'
                        )
                    )
                    continue
                
                library = Library.objects.create(
                    name=name,
                    description=library_data['description'],
                    owner=owner
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Kütüphane oluşturuldu: {name} (Sahip: {owner.get_full_name()})'
                    )
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nToplam {created_count} kütüphane oluşturuldu!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Hiç yeni kütüphane oluşturulmadı.')
            )
