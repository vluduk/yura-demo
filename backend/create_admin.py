#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Delete existing admin user if exists
User.objects.filter(phone='admin').delete()

# Create new admin user
user = User.objects.create_superuser(
    phone='admin',
    name='Admin',
    surname='User',
    password='admin123'
)

print(f"Admin user created successfully!")
print(f"Username (phone): admin")
print(f"Password: admin123")
