"""
Management command to optimize static files for production.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = 'Optimize static files for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing static files before collecting',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting static files optimization...')

        # Clear existing static files if requested
        if options['clear']:
            self.stdout.write('Clearing existing static files...')
            if os.path.exists(settings.STATIC_ROOT):
                shutil.rmtree(settings.STATIC_ROOT)

        # Collect static files
        self.stdout.write('Collecting static files...')
        call_command('collectstatic', '--noinput', '--clear')

        # Create media directory if it doesn't exist
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            self.stdout.write(f'Created media directory: {settings.MEDIA_ROOT}')

        self.stdout.write(
            self.style.SUCCESS('Static files optimization completed successfully!')
        )

