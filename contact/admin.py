from django.contrib import admin
from .models import ContactQuery, Subscriber

# Register your models here.
admin.site.register(ContactQuery)
admin.site.register(Subscriber)