from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from api.serializers.auth import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class SignUpView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        tags=['Auth'],
        responses={
            201: openapi.Response('User created successfully', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: 'Bad request - user already exists',
            422: 'Validation failed'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            response = Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
            
            # Set HttpOnly cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=15 * 60  # 15 minutes
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=7 * 24 * 60 * 60  # 7 days
            )
            
            return response
        return Response({'message': serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)



class LoginView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=['Auth'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            },
        ),
        responses={
            200: 'Login successful',
            401: 'Invalid credentials',
            422: 'Validation errors'
        }
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
             return Response({'message': 'Email and password are required'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user = authenticate(username=email, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            response = Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            
            # Set HttpOnly cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=15 * 60  # 15 minutes
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=7 * 24 * 60 * 60  # 7 days
            )
            
            return response
        
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(tags=['Auth'])
    def post(self, request):
        try:
            response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
            
            # Clear cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response
        except Exception as e:
            return Response({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RefreshView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=['Auth'])
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({'message': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken(refresh_token)
            
            response = Response({'message': 'Token refreshed'}, status=status.HTTP_200_OK)
            
            # Set new access token
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite='Lax',
                max_age=15 * 60  # 15 minutes
            )
            
            return response
        except Exception as e:
            return Response({'message': 'Invalid or expired refresh token'}, status=status.HTTP_403_FORBIDDEN)



class CreateAdminView(APIView):
    permission_classes = (AllowAny,)  # Should be restricted in production

    @swagger_auto_schema(tags=['Auth', 'Admin'])
    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email='admin@yura.com').exists():
            User.objects.create_superuser(
                email='admin@yura.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            return Response({'message': 'Admin account created successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Admin account already exists'}, status=status.HTTP_200_OK)
