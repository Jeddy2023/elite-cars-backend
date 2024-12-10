from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer, LogoutSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser
from rest_framework.pagination import PageNumberPagination

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response({'message': 'User registered successfully', 'user': user_data}, status=status.HTTP_201_CREATED)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                if not user.is_active:
                    return Response({'error': 'User account is deactivated'}, status=status.HTTP_403_FORBIDDEN)

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Return user details and tokens
                user_data = UserSerializer(user).data
                return Response({
                    'user': user_data,
                    'accessToken': access_token,
                    'refreshToken': refresh_token,
                }, status=status.HTTP_200_OK)

            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class GetUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_200_OK)

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        serializer = UserSerializer(instance=user, data=data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            user_data = UserSerializer(updated_user).data
            return Response({'message': 'User details updated successfully', 'user': user_data}, status=status.HTTP_200_OK)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']

                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                print(e)
                return Response({"message": "An error occurred during logout."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomUserPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size' 
    max_page_size = 100

class GetUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role == 'admin':
            return Response({"message": "You do not have permission to view all users."}, status=status.HTTP_403_FORBIDDEN)
        
        users = CustomUser.objects.all()
        paginator = CustomUserPagination()
        paginated_users = paginator.paginate_queryset(users, request)

        serializer = UserSerializer(paginated_users, many=True)
        response_data = paginator.get_paginated_response(serializer.data)
        response_data.status_code = status.HTTP_200_OK
        return response_data