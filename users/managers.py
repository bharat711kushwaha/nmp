from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
import random
import string


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication and username is generated automatically.
    """
    
    def generate_unique_username(self):
        """Generate a unique username starting with 'M' followed by 6 random digits"""
        while True:
            # Generate a username with 'M' prefix and 6 random digits
            random_digits = ''.join(random.choices(string.digits, k=6))
            username = f"M{random_digits}"
            
            # Check if username already exists
            if not self.model.objects.filter(username=username).exists():
                return username
    
    def create_user(self, email, phone, referral_code, password=None, **extra_fields):
        """
        Create and save a user with the given email, phone, referral_code and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        if not phone:
            raise ValueError(_('The Phone must be set'))
        if not referral_code:
            raise ValueError(_('The Referral Code must be set'))
        
        email = self.normalize_email(email)
        
        # Generate a unique username if not provided
        if 'username' not in extra_fields:
            username = self.generate_unique_username()
            extra_fields['username'] = username
        
        user = self.model(
            email=email,
            phone=phone,
            referral_code=referral_code,
            **extra_fields
        )
        
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, phone, referral_code, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email, phone, referral_code and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
            
        return self.create_user(email, phone, referral_code, password, **extra_fields)