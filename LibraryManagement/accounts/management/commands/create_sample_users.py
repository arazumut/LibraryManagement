from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Örnek kullanıcılar oluşturur'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Mevcut kullanıcıları temizle (admin hariç)',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            # Admin olmayan kullanıcıları sil
            deleted_count = User.objects.filter(is_superuser=False).count()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(
                self.style.WARNING(f'{deleted_count} kullanıcı silindi.')
            )
        
        # Örnek kullanıcılar
        sample_users = [
            {
                'username': 'super_admin',
                'email': 'admin@library.com',
                'first_name': 'Süper',
                'last_name': 'Admin',
                'user_type': User.SUPER_ADMIN,
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'ahmet_yonetici',
                'email': 'ahmet@library.com',
                'first_name': 'Ahmet',
                'last_name': 'Kaya',
                'user_type': User.LIBRARY_ADMIN,
                'is_staff': True,
            },
            {
                'username': 'ayse_yonetici',
                'email': 'ayse@library.com',
                'first_name': 'Ayşe',
                'last_name': 'Demir',
                'user_type': User.LIBRARY_ADMIN,
                'is_staff': True,
            },
            {
                'username': 'mehmet_okuyucu',
                'email': 'mehmet@email.com',
                'first_name': 'Mehmet',
                'last_name': 'Özkan',
                'user_type': User.READER,
            },
            {
                'username': 'fatma_okuyucu',
                'email': 'fatma@email.com',
                'first_name': 'Fatma',
                'last_name': 'Yılmaz',
                'user_type': User.READER,
            },
            {
                'username': 'ali_okuyucu',
                'email': 'ali@email.com',
                'first_name': 'Ali',
                'last_name': 'Çelik',
                'user_type': User.READER,
            },
            {
                'username': 'zeynep_okuyucu',
                'email': 'zeynep@email.com',
                'first_name': 'Zeynep',
                'last_name': 'Aydın',
                'user_type': User.READER,
            },
            {
                'username': 'emre_okuyucu',
                'email': 'emre@email.com',
                'first_name': 'Emre',
                'last_name': 'Güler',
                'user_type': User.READER,
            },
        ]
        
        created_count = 0
        
        with transaction.atomic():
            for user_data in sample_users:
                username = user_data['username']
                
                # Kullanıcı zaten varsa atla
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Kullanıcı zaten mevcut: {username}')
                    )
                    continue
                
                # Şifreyi kullanıcı adıyla aynı yap (demo için)
                password = username
                
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    user_type=user_data['user_type'],
                    is_superuser=user_data.get('is_superuser', False),
                    is_staff=user_data.get('is_staff', False),
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {user.get_user_type_display()}: {username} (şifre: {password})'
                    )
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nToplam {created_count} kullanıcı oluşturuldu!')
            )
            self.stdout.write(
                self.style.WARNING(
                    '\nNOT: Bu demo verileridir. Tüm şifreler kullanıcı adıyla aynıdır.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Hiç yeni kullanıcı oluşturulmadı.')
            )
