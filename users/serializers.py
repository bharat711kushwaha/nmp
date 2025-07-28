from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegistrationSerializer(serializers.Serializer):
    """Serializer for user registration with OTP"""
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    referral_code = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def validate_referral_code(self, value):
        """Check if referral code is unique"""
        if User.objects.filter(referral_code=value).exists():
            raise serializers.ValidationError("Referral code already in use")
        return value


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    def validate_email(self, value):
        """Check if email exists in registration data"""
        # This validation assumes email was saved in session during registration
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'referral_code', 'is_email_verified')
        read_only_fields = ('id', 'username', 'is_email_verified')


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                if not user.is_email_verified:
                    raise serializers.ValidationError("Email is not verified. Please verify your email first.")
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")