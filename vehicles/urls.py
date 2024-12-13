from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateVehicleView.as_view(), name='create_vehicle'),
    path('update/<int:pk>/', views.UpdateVehicleDetailsView.as_view(), name='update_vehicle_details'),
    path('all/', views.GetAllVehiclesView.as_view(), name='get_all_vehicles'),
    path('vehicle/<int:id>/', views.GetVehicleByIdView.as_view(), name='get_vehicle_by_id'),

    path('update-image/<int:pk>/images/<int:image_index>/', views.UpdateVehicleImageView.as_view(), name='update-vehicle-image-index'),

    path('delete-images/<int:pk>/', views.DeleteVehicleImagesView.as_view(), name='delete-vehicle-images'),
    path('delete-vehicle/<int:pk>/', views.DeleteVehicleView.as_view(), name='delete-vehicle'),
]