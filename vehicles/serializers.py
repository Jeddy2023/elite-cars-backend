from rest_framework import serializers
from .models import Vehicle
import cloudinary.uploader
from django.db import transaction

# class CreateVehicleSerializer(serializers.ModelSerializer):
#     images = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False
#     )

#     class Meta:
#         model = Vehicle
#         fields = '__all__'

#     def create(self, validated_data):
#         images = validated_data.pop('images', [])
#         image_data = []

#         for image in images:
#             upload_result = cloudinary.uploader.upload(
#                 image, folder="EliteCars"
#             )
#             image_data.append({
#                 'url': upload_result.get('secure_url'),
#                 'public_id': upload_result.get('public_id')
#             })

#         validated_data['image_data'] = image_data
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         new_images = validated_data.pop('images', [])
#         with transaction.atomic(): 
#             if new_images:
#                 for image in new_images:
#                     upload_result = cloudinary.uploader.upload(
#                         image, folder="EliteCars"
#                     )
#                     instance.image_data.append({
#                         'url': upload_result.get('secure_url'),
#                         'public_id': upload_result.get('public_id')
#                     })

#             for attr, value in validated_data.items():
#                 setattr(instance, attr, value)

#             instance.save()
#         return instance

class CreateVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['brand', 'model', 'year', 'registration_number', 'daily_rent', 'availability_status', 
                  'seating_capacity', 'fuel_type', 'transmission', 'category', 'location']

    def create(self, validated_data):
        # No images field handling here
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle updates without images field
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
        return instance
    
class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'id', 
            'brand', 
            'model', 
            'year', 
            'registration_number', 
            'daily_rent', 
            'availability_status', 
            'seating_capacity', 
            'fuel_type', 
            'transmission', 
            'category', 
            'location', 
            'image_data', 
            'created_at', 
            'updated_at'
        ]

class VehicleImageSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Vehicle
        fields = ['image_data']

    def add_images(self, instance, images):
        image_data = []
        for image in images:
            upload_result = cloudinary.uploader.upload(image, folder="EliteCars")
            image_data.append({
                'url': upload_result.get('secure_url'),
                'public_id': upload_result.get('public_id')
            })
        instance.image_data.extend(image_data)
        instance.save()
        return image_data

    def remove_images(self, instance, image_indexes):
        image_data = instance.image_data
        for index in image_indexes:
            if 0 <= index < len(image_data):
                old_image = image_data[index]
                cloudinary.uploader.destroy(old_image['public_id'])
                del image_data[index]
        instance.save()

    def update_vehicle_image(self, instance, image_index, new_image):
        if not (0 <= image_index < len(instance.image_data)):
            raise serializers.ValidationError("Invalid image index.")
        
        old_image = instance.image_data[image_index]
        cloudinary.uploader.destroy(old_image['public_id'])
        
        upload_result = cloudinary.uploader.upload(new_image, folder="EliteCars")
        instance.image_data[image_index] = {
            'url': upload_result.get('secure_url'),
            'public_id': upload_result.get('public_id')
        }
        instance.save()
        return instance.image_data[image_index]