"""
Management command for production setup and maintenance.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth import get_user_model
import os

import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Load .env file from parent directory
env = environ.Env()
env_path = BASE_DIR.parent / '.env'
environ.Env.read_env(env_path)


class Command(BaseCommand):
    help = 'Set up production environment and perform maintenance tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--collect-static',
            action='store_true',
            help='Collect static files',
        )
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Run database migrations',
        )
        parser.add_argument(
            '--check-deploy',
            action='store_true',
            help='Check deployment readiness',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting production setup...')

        # Run migrations
        if options['migrate']:
            self.stdout.write('Running database migrations...')
            call_command('migrate', '--noinput')

        # Collect static files
        if options['collect_static']:
            self.stdout.write('Collecting static files...')
            call_command('collectstatic', '--noinput')

        # Create superuser
        if options['create_superuser']:
            self.create_superuser()

        # Check deployment readiness
        if options['check_deploy']:
            self.check_deployment_readiness()

        self.stdout.write(
            self.style.SUCCESS('Production setup completed successfully!')
        )

    def create_superuser(self):
        """Create a superuser if one doesn't exist."""
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating superuser...')
            User.objects.create_superuser(
                username=env('ADMIN_USERNAME'),
                email=env('ADMIN_EMAIL'),
                password=env('ADMIN_PASSWORD')  # Change this in production!
            )
            self.stdout.write(
                self.style.WARNING(
                    'Superuser created with default credentials. '
                    'Please change the password immediately!'
                )
            )
        else:
            self.stdout.write('Superuser already exists.')

    def check_deployment_readiness(self):
        """Check if the application is ready for production deployment."""
        self.stdout.write('Checking deployment readiness...')

        # Check settings
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING('WARNING: DEBUG is True in production!')
            )

        # Check secret key
        if settings.SECRET_KEY == 'django-insecure-$!l85#z44*(1-f0v^5^uv*^^#9gt=^^^of6yls01aigkt8+q5b':
            self.stdout.write(
                self.style.WARNING('WARNING: Using default SECRET_KEY!')
            )

        # Check allowed hosts
        if 'localhost' in settings.ALLOWED_HOSTS and len(settings.ALLOWED_HOSTS) == 1:
            self.stdout.write(
                self.style.WARNING('WARNING: Only localhost in ALLOWED_HOSTS!')
            )

        # Check static files
        if not os.path.exists(settings.STATIC_ROOT):
            self.stdout.write(
                self.style.WARNING('WARNING: STATIC_ROOT directory does not exist!')
            )

        # Check logs directory
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(logs_dir):
            self.stdout.write(
                self.style.WARNING('WARNING: Logs directory does not exist!')
            )

        self.stdout.write('Deployment readiness check completed.')
