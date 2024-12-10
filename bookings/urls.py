from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateBookingView.as_view(), name='create_booking'),
    path('user-bookings/', views.GetUserBookingsView.as_view(), name='get_user_bookings'),
    path('<int:booking_id>/', views.GetBookingByIdView.as_view(), name='get_booking_by_id'),
    path('cancel/<int:booking_id>/', views.CancelBookingView.as_view(), name='cancel_booking'),
    path('get-bookings-admin/', views.GetAllBookingsView.as_view(), name='get_all_bookings_admin'),
    path('update-status/<int:booking_id>/', views.UpdateBookingStatusView.as_view(), name='update_booking_status'),
]