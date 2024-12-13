from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/vehicles/', include('vehicles.urls')),
    path('api/v1/bookings/', include('bookings.urls')),
]