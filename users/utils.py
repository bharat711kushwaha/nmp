import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import OTPVerification, TeamHierarchy


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email):
    """Send OTP verification email"""
    otp = generate_otp()
    
    # Save OTP to database
    OTPVerification.objects.create(
        email=email,
        otp=otp
    )
    
    # Send email
    subject = 'OTP Verification for Registration'
    message = f'Your OTP for registration is: {otp}. It is valid for 10 minutes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    
    return True


def verify_otp(email, otp):
    """Verify OTP for the given email"""
    # Check for valid OTP
    otp_obj = OTPVerification.objects.filter(
        email=email,
        otp=otp,
        is_used=False,
        created_at__gte=timezone.now() - timedelta(seconds=settings.OTP_EXPIRY_TIME)
    ).first()
    
    if otp_obj:
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        return True
    
    return False


def create_team_hierarchy(user):
    """Create team hierarchy for a new user"""
    entries = []

    # Self reference
    entries.append(TeamHierarchy(ancestor=user, descendant=user, depth=0))

    # If user has a parent (was referred)
    if user.parent:
        # Get all ancestors of parent and create relationships
        ancestors = TeamHierarchy.objects.filter(descendant=user.parent).select_related(
            "ancestor"
        )

        for ancestor_relation in ancestors:
            entries.append(
                TeamHierarchy(
                    ancestor=ancestor_relation.ancestor,
                    descendant=user,
                    depth=ancestor_relation.depth + 1,
                )
            )

        # Create direct parent relationship
        entries.append(TeamHierarchy(ancestor=user.parent, descendant=user, depth=1))

    # Bulk create all hierarchy entries
    TeamHierarchy.objects.bulk_create(entries)
    
    return True