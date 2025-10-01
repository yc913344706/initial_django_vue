from django.core.management.base import BaseCommand
from apps.user.models import User
from lib.password_tools import aes
from lib.log import color_logger


class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **options):
        admin_username = 'admin'
        admin_password = 'Admin@123'
        
        # Check if admin user already exists
        admin_user = User.objects.filter(username=admin_username).first()
        
        if admin_user:
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists')
            )
        else:
            # Encrypt the password using the AES encryption used by the application
            encrypted_password = aes.encrypt(admin_password)
            
            # Create the admin user
            admin_user = User.objects.create(
                username=admin_username,
                password=encrypted_password,
                email='admin@example.com',
                nickname='Admin',
                phone='12345678901',
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user "{admin_username}" with password "Admin@123"'
                )
            )
            
        color_logger.info(f'Admin user check completed. User exists: {admin_user is not None}')