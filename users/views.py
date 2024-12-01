from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response({'message': 'User registered successfully', 'user': user_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
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

            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
