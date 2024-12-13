from rest_framework import serializers
from .models import Booking
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from users.serializers import UserSerializer
from django.utils.timezone import now, datetime, make_aware

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'vehicle', 'pickup_location', 'drop_off_location', 
            'booking_date', 'start_date', 'end_date', 'total_cost', 'status', 
            'created_at', 'updated_at'
        ]

class CreateBookingSerializer(serializers.Serializer):
    vehicle = serializers.IntegerField(write_only=True)
    pickup_location = serializers.CharField(max_length=255)
    drop_off_location = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        # Check if the start date is in the future
        if data['start_date'] < now().date():
            raise serializers.ValidationError({"start_date": "Start date must be in the future."})

        # Check if the end date is after the start date
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError({"end_date": "End date must be after the start date."})

        # Convert naive dates to aware datetimes
        data['start_date'] = make_aware(datetime.combine(data['start_date'], datetime.min.time()))
        data['end_date'] = make_aware(datetime.combine(data['end_date'], datetime.min.time()))

        # Check if the vehicle is available
        try:
            vehicle = Vehicle.objects.get(id=data['vehicle'])
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError({"vehicle": "Vehicle does not exist."})

        if not vehicle.availability_status:
            raise serializers.ValidationError({"vehicle": "Vehicle is not available for booking."})

        # Calculate the booking duration
        duration = (data['end_date'] - data['start_date']).days
        if duration < 1:
            raise serializers.ValidationError({"end_date": "Booking must be for at least one day."})

        data['duration'] = duration
        data['vehicle_instance'] = vehicle
        return data
    
class UpdateBookingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)

    def validate_status(self, value):
        if value not in dict(Booking.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status.")
        return value
