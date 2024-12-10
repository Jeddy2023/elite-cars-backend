from django.db import models

from django.db import models
from django.utils.timezone import now
from users.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Vehicle(models.Model):

    FUEL_TYPES = [
        ('Petrol', 'Petrol'), 
        ('Diesel', 'Diesel'), 
        ('Electric', 'Electric')
    ]

    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'), 
        ('Manual', 'Manual')
    ]

    CATEGORY_CHOICES = [
        ('SUV', 'SUV'), 
        ('Sedan', 'Sedan'), 
        ('Hatchback', 'Hatchback')
    ]

    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(
        validators=[
            MinValueValidator(1886),  # The year when the first car was made
            MaxValueValidator(now().year)  # Ensure the year is not in the future
        ]
    )
    registration_number = models.CharField(max_length=20, unique=True)
    daily_rent = models.IntegerField(
        validators=[MinValueValidator(0)]  
    )
    availability_status = models.BooleanField(default=True)
    seating_capacity = models.IntegerField(validators=[MinValueValidator(1)])
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=255)
    # image_data = models.JSONField(default=list) 
    image_data = models.JSONField(default=lambda: [{
        'url': 'https://res.cloudinary.com/dyktnfgye/image/upload/v1722173585/8_hyx9vy.png',
        'public_id': 'default_vehicle_image'
    }]) 
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicles'

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) - {self.registration_number}"

class ReviewAndRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'reviews'
