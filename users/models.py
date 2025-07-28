from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class User(AbstractUser):
    """Custom User model with additional fields and referral system"""
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=15)
    referral_code = models.CharField(_('referral code'), max_length=10, unique=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referrals'
    )
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone', 'referral_code']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class OTPVerification(models.Model):
    """Model to store OTP verification codes"""
    
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.email} - {self.otp}"


class TeamHierarchy(models.Model):
    """Model to maintain team hierarchy for referral system"""
    
    ancestor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='descendant_relations'
    )
    descendant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ancestor_relations'
    )
    depth = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('ancestor', 'descendant')
        verbose_name = _('team hierarchy')
        verbose_name_plural = _('team hierarchies')
    
    def __str__(self):
        return f"{self.ancestor.username} -> {self.descendant.username} (Depth: {self.depth})"