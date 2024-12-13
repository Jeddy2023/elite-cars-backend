from django.db import models

from django.db import models
from django.utils.timezone import now
from users.models import CustomUser
from vehicles.models import Vehicle
from django.core.validators import MinValueValidator

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    pickup_location = models.CharField(max_length=255)
    drop_off_location = models.CharField(max_length=255)
    booking_date = models.DateField(default=now)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_cost = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('Booking Confirmation', 'Booking Confirmation'),
        ('Payment Reminder', 'Payment Reminder'),
        ('Booking Ending', 'Booking Ending'),
        ('Booking Starting', 'Booking Starting'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'notifications'
