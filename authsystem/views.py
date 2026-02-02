from rest_framework import status, generics, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.files.base import ContentFile
from django.conf import settings
import random
import requests
from .serializers import (
    UserRegistrationSerializer,
    OTPVerificationSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_otp():
    return str(random.randint(100000, 999999))

class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and save OTP
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            
            # Send OTP
            context = {'otp': otp}
            html_message = render_to_string('authsystem/otp_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                'Verify your account',
                plain_message,
                settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@example.com',
                [user.email],
                fail_silently=False,
                html_message=html_message
            )
            
            return Response({
                'message': 'Registration successful. Check your email for OTP.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(views.APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if user.otp == otp:
                # Check expiration (e.g., 10 minutes) - Optional but good practice
                # if timezone.now() > user.otp_created_at + timezone.timedelta(minutes=10):
                #     return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
                
                user.is_active = True
                user.is_verified = True
                user.otp = None
                user.save()
                return Response({'message': 'Account verified successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password) # username is email in our case

            if user is not None:
                if not user.is_active:
                     return Response({'error': 'Account is inactive or not verified.'}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class GoogleLoginView(views.APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        google_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        response = requests.get(google_url)
        
        if response.status_code != 200:
            return Response({"error": "Invalid access token"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Verify token and get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            google_response = requests.get(user_info_url, headers=headers)
            if google_response.status_code != 200:
                return Response({"error": "Invalid access token or failed to fetch user info"}, status=status.HTTP_400_BAD_REQUEST)
            
            google_data = google_response.json()
            email = google_data.get("email")
            name = google_data.get("name", "")
            picture = google_data.get("picture", "")
            if not email:
                return Response({"error": "Google account does not have an email address"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if user exists
            try:
                user = User.objects.get(email=email)
                if not user.is_active or not user.is_verified:
                    user.is_active = True
                    user.is_verified = True
                    user.save()
            except User.DoesNotExist:
                # Create user
                user = User.objects.create(
                    email=email,
                    name=name,
                    is_active=True,
                    is_verified=True
                )
                user.set_unusable_password()
                user.save()

            if not user.image and picture:
                try:
                    img_response = requests.get(picture)
                    if img_response.status_code == 200:
                        user.image.save(f"google_{random.randint(1000,9999)}.jpg", ContentFile(img_response.content), save=True)
                except Exception:
                    pass
            
            if not user.is_active:
                return Response({'error': 'Account is inactive.'}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
