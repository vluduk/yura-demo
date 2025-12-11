from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from api.serializers.auth import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

User = get_user_model()


class SignUpView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
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
            
            # Get cookie settings from environment
            secure_cookie = os.environ.get('DEBUG', 'True') != 'True'
            access_lifetime = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 15))
            refresh_lifetime = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))
            
            response = Response({
                'message': 'User created successfully',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
            
            # Set HttpOnly cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=access_lifetime * 60
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=refresh_lifetime * 24 * 60 * 60
            )
            
            return response
        return Response({'message': serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)



class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

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
            
            # Get cookie settings from environment
            secure_cookie = os.environ.get('DEBUG', 'True') != 'True'
            access_lifetime = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 15))
            refresh_lifetime = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))
            
            response = Response({
                'message': 'Login successful',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
            
            # Set HttpOnly cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=access_lifetime * 60
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=refresh_lifetime * 24 * 60 * 60
            )
            
            return response
        
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=['Auth'],
        responses={
            200: 'Logged out successfully',
            400: 'Invalid token',
            500: 'Internal server error'
        }
    )
    def post(self, request):
        try:
            # Get refresh token from cookie to blacklist it
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                try:
                    # Blacklist the refresh token
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except TokenError:
                    # Token already blacklisted or invalid, continue anyway
                    pass
            
            response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
            
            # Clear cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response
        except Exception as e:
            return Response({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RefreshView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @swagger_auto_schema(
        tags=['Auth'],
        responses={
            200: 'Token refreshed successfully',
            401: 'Refresh token not found',
            403: 'Invalid or expired refresh token'
        }
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'message': 'Refresh token not found',
                'code': 'refresh_token_missing'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Get cookie settings from environment
            secure_cookie = os.environ.get('DEBUG', 'True') != 'True'
            access_lifetime = int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 15))
            refresh_lifetime = int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))
            
            # Create refresh token object (this will validate it)
            refresh = RefreshToken(refresh_token)
            
            response = Response({'message': 'Token refreshed'}, status=status.HTTP_200_OK)
            
            # Set new access token (refresh.access_token generates a new one)
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=access_lifetime * 60
            )
            
            # With ROTATE_REFRESH_TOKENS and BLACKLIST_AFTER_ROTATION enabled,
            # the old token is automatically blacklisted and a new one is issued
            # Update the refresh token cookie with the rotated token
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=secure_cookie,
                samesite='Lax',
                max_age=refresh_lifetime * 24 * 60 * 60
            )
            
            return response
        except TokenError as e:
            return Response({
                'message': 'Invalid or expired refresh token',
                'code': 'refresh_token_invalid'
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'message': 'Token refresh failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        tags=['Auth'],
        responses={
            200: openapi.Response('Current user information', UserSerializer),
            401: 'Not authenticated'
        }
    )
    def get(self, request):
        """Get current authenticated user information"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['Auth'],
        request_body=UserSerializer,
        responses={200: openapi.Response('Updated user info', UserSerializer)}
    )
    def patch(self, request):
        """Update current authenticated user information"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    """Simple endpoint to ensure `csrftoken` cookie is set for SPA clients.

    Call this with GET from the frontend during app initialization so the
    browser receives the `csrftoken` cookie that Angular will read and send
    on subsequent state-changing requests.
    """
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=['Auth'], responses={200: 'CSRF cookie set'})
    def get(self, request, *args, **kwargs):
        return Response({'message': 'CSRF cookie set'}, status=status.HTTP_200_OK)
