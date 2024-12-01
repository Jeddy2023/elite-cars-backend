from django.db import models

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.timezone import now

class CustomUser(AbstractBaseUser):

    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    profile_picture = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

