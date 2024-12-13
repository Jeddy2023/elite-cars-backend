from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_filters import filters
from rest_framework.response import Response
from rest_framework import status
from .models import Vehicle
from .serializers import VehicleSerializer, CreateVehicleSerializer, VehicleImageSerializer

class CreateVehicleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.role == 'admin':
            return Response({"message": "You do not have permission to create a vehicle."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CreateVehicleSerializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.save()
            vehicle_data = VehicleSerializer(vehicle).data
            return Response(
                {"message": "Vehicle created successfully!", "vehicle": vehicle_data},
                status=status.HTTP_201_CREATED
            )
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class UpdateVehicleDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateVehicleSerializer

    def get_vehicle(self, pk):
        try:
            return Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return None

    def put(self, request, pk):
        if request.user.role != 'admin':
            return Response({"message": "You do not have permission to update a vehicle."}, status=status.HTTP_403_FORBIDDEN)
        
        vehicle = self.get_vehicle(pk)
        if not vehicle:
            return Response({"message": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(instance=vehicle, data=request.data, partial=True)
        
        if serializer.is_valid():
            vehicle = serializer.save()
            vehicle_data = VehicleSerializer(vehicle).data 
            return Response({
                "message": "Vehicle details updated successfully.",
                "vehicle": vehicle_data
            }, status=status.HTTP_200_OK)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class UpdateVehicleImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get_vehicle(self, pk):
        try:
            return Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return None

    def put(self, request, pk, image_index=None):
        if request.user.role != 'admin':
            return Response({"message": "You do not have permission to update a vehicle."}, status=status.HTTP_403_FORBIDDEN)
        
        vehicle = self.get_vehicle(pk)
        if not vehicle:
            return Response({"message": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use serializer to update the vehicle image
        serializer = VehicleImageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if image_index is not None:
                    updated_image = serializer.update_vehicle_image(vehicle, image_index, request.data['image'])
                    return Response({
                        "message": "Image updated successfully.",
                        "updated_image": updated_image
                    }, status=status.HTTP_200_OK)
                else:
                    # Add new images
                    added_images = serializer.add_images(vehicle, request.data.get('images', []))
                    return Response({
                        "message": "Images added successfully.",
                        "added_images": added_images
                    }, status=status.HTTP_200_OK)
            except serializer.ValidationError as e:
                first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
                return Response({
                    'message': first_error 
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "message": f"An unexpected error occurred: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "message": "Invalid image data."
        }, status=status.HTTP_400_BAD_REQUEST)

class DeleteVehicleImagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get_vehicle(self, pk):
        try:
            return Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return None

    def delete(self, request, pk):
        if request.user.role != 'admin':
            return Response({"message": "You do not have permission to delete vehicle images."}, status=status.HTTP_403_FORBIDDEN)
        
        vehicle = self.get_vehicle(pk)
        if not vehicle:
            return Response({"message": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)

        image_indexes = request.data.get('image_indexes')
        if not image_indexes:
            return Response({"message": "No image indexes provided."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VehicleImageSerializer()
        try:
            serializer.remove_images(vehicle, image_indexes)
            return Response({
                "message": "Images deleted successfully."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"An unexpected error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteVehicleView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        if not request.user.role == 'admin':
            return Response({"message": "You do not have permission to create a vehicle."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            vehicle = Vehicle.objects.get(pk=pk)
            
            # Delete all images from Cloudinary
            # for image in vehicle.image_data:
            #     destroy(image['public_id'])

            vehicle.delete()
            return Response({"message": "Vehicle deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Vehicle.DoesNotExist:
            return Response({"message": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND)

class VehicleFilter(FilterSet):
    fuel_type = filters.ChoiceFilter(choices=Vehicle.FUEL_TYPES)
    transmission = filters.ChoiceFilter(choices=Vehicle.TRANSMISSION_CHOICES)
    category = filters.ChoiceFilter(choices=Vehicle.CATEGORY_CHOICES)
    daily_rent = filters.NumberFilter()
    availability_status = filters.BooleanFilter()
    seating_capacity = filters.NumberFilter()
    location = filters.CharFilter(lookup_expr="icontains") 

    class Meta:
        model = Vehicle
        fields = [
            "fuel_type",
            "transmission",
            "category",
            "daily_rent",
            "availability_status",
            "seating_capacity",
            "location",
        ]

class VehiclePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class GetAllVehiclesView(ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]
    pagination_class = VehiclePagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ["brand", "model", "year"]

    filterset_class = VehicleFilter

    ordering_fields = ["daily_rent", "year", "brand", "created_at"]
    ordering = ["-created_at"] 

class GetVehicleByIdView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    lookup_field = 'id'