#!/bin/bash

# Production startup script for Django Quotes Application

set -e

echo "Starting Django Quotes Application..."

# Wait for database to be ready (if using external database)
# while ! python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; do
#   echo "Waiting for database..."
#   sleep 1
# done

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
# echo "Creating superuser if needed..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'admin')
# "

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

