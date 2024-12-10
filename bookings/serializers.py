from rest_framework import serializers
from .models import Booking
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from users.serializers import UserSerializer
from django.utils.timezone import now

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)

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

    def create(self, validated_data):
        user = self.context['request'].user
        vehicle = validated_data['vehicle_instance']

        # Calculate total cost
        total_cost = vehicle.daily_rent * validated_data['duration']

        # Create the booking
        booking = Booking.objects.create(
            user=user,
            vehicle=vehicle,
            pickup_location=validated_data['pickup_location'],
            drop_off_location=validated_data['drop_off_location'],
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            total_cost=total_cost
        )

        vehicle.availability_status = False
        vehicle.save()

        return booking

class UpdateBookingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)

    def validate_status(self, value):
        if value not in dict(Booking.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid status.")
        return value