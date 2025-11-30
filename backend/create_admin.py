#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from src.models.user import User

# Delete existing admin user if exists
User.objects.filter(email='admin@example.com').delete()

# Create new admin user
user = User.objects.create_superuser(
    email='admin@example.com',
    name='Admin',
    surname='User',
    password='admin123'
)

print(f"Admin user created successfully!")
print(f"Email: admin@example.com")
print(f"Password: admin123")
