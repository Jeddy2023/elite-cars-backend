from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import BookingSerializer, CreateBookingSerializer, UpdateBookingStatusSerializer
from .models import Booking
from vehicles.models import Vehicle

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data)
        if serializer.is_valid():
            vehicle_id = serializer.validated_data['vehicle']
            pickup_location = serializer.validated_data['pickup_location']
            drop_off_location = serializer.validated_data['drop_off_location']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            # Check if the vehicle exists
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
            except Vehicle.DoesNotExist:
                return Response({"message": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND)

            # Create the booking
            booking = Booking.objects.create(
                user=request.user,
                vehicle=vehicle,
                pickup_location=pickup_location,
                drop_off_location=drop_off_location,
                start_date=start_date,
                end_date=end_date,
                total_cost=vehicle.daily_rent * ((end_date - start_date).days),
            )

            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class GetUserBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetBookingByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        if booking.status in ['Cancelled', 'Completed']:
            return Response({"message": "Cannot cancel this booking"}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = 'Cancelled'
        booking.save()
        return Response({"message": "Booking cancelled successfully"}, status=status.HTTP_200_OK)

class GetAllBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role == 'admin':
            return Response({"message": "You do not have permission to view all bookings."}, status=status.HTTP_403_FORBIDDEN)
        
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateBookingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        if not request.user.role == 'admin':
            return Response({"message": "You do not have permission to update booking status."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"message": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateBookingStatusSerializer(data=request.data)
        if serializer.is_valid():
            booking.status = serializer.validated_data['status']
            booking.save()
            return Response({"message": "Booking status updated successfully"}, status=status.HTTP_200_OK)

        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error
        }, status=status.HTTP_400_BAD_REQUEST)