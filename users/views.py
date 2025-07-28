from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login

from .models import User
from .serializers import (
    RegistrationSerializer, 
    OTPVerificationSerializer, 
    UserSerializer,
    LoginSerializer
)
from .utils import send_otp_email, verify_otp, create_team_hierarchy


class RegistrationView(APIView):
    """
    API view for user registration with OTP verification
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Store registration data in session
            request.session['registration_data'] = serializer.validated_data
            
            # Send OTP to email
            email = serializer.validated_data['email']
            send_otp_email(email)
            
            return Response({
                'message': 'OTP sent to your email for verification',
                'email': email
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    """
    API view for OTP verification and user creation
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            # Get registration data from session
            registration_data = request.session.get('registration_data', None)
            
            if not registration_data:
                return Response({
                    'error': 'Registration data not found. Please register again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify OTP
            if verify_otp(email, otp):
                # Check if email matches the one in registration data
                if email != registration_data['email']:
                    return Response({
                        'error': 'Email does not match with registration data'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create user
                name = registration_data['name']
                phone = registration_data['phone']
                referral_code = registration_data['referral_code']
                password = registration_data['password']
                
                # Check if referral code is valid (exists as another user's referral_code)
                parent = None
                if 'parent_referral_code' in registration_data:
                    parent_code = registration_data['parent_referral_code']
                    try:
                        parent = User.objects.get(referral_code=parent_code)
                    except User.DoesNotExist:
                        pass
                
                # Create user with CustomUserManager
                user = User.objects.create_user(
                    email=email,
                    phone=phone,
                    referral_code=referral_code,
                    password=password
                )
                
                # Set name (first_name and last_name)
                name_parts = name.split(maxsplit=1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                
                # Set parent if exists
                if parent:
                    user.parent = parent
                
                # Mark email as verified
                user.is_email_verified = True
                user.save()
                
                # Create team hierarchy
                create_team_hierarchy(user)
                
                # Create JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Clear session data
                if 'registration_data' in request.session:
                    del request.session['registration_data']
                
                return Response({
                    'message': 'User registered successfully',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Invalid OTP or OTP expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view for user login
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Log in the user
            login(request, user)
            
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API view for user profile management
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)