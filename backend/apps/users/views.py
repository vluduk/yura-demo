from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, TokenResponseSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'accessToken': str(refresh.access_token),
        'refreshToken': str(refresh),
    }

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            phone=serializer.validated_data['phone'],
            password=serializer.validated_data['password']
        )
        if user:
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # In simplejwt, logout is client-side (delete token), but we can blacklist refresh token if needed.
        # For now, just return success as per swagger
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

class CreateAdminView(APIView):
    permission_classes = (permissions.AllowAny,) # Should be restricted in real prod

    def post(self, request):
        # Demo only
        if not User.objects.filter(phone='admin').exists():
            User.objects.create_superuser(phone='admin', password='adminpassword', name='Admin', surname='User')
        return Response({'message': 'Admin account created successfully'}, status=status.HTTP_201_CREATED)

class UserMeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

