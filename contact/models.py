from django.db import models
from django.utils.timezone import now

class ContactQuery(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'contacts'

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'subscribers'
