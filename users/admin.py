from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTPVerification, TeamHierarchy


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'referral_code', 'is_email_verified', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'referral_code')
    readonly_fields = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'referral_code')}),
        ('Referral', {'fields': ('parent',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified',
                                   'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'referral_code', 'password1', 'password2'),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'is_used', 'created_at')
    search_fields = ('email', 'otp')
    list_filter = ('is_used', 'created_at')


@admin.register(TeamHierarchy)
class TeamHierarchyAdmin(admin.ModelAdmin):
    list_display = ('ancestor', 'descendant', 'depth')
    search_fields = ('ancestor__username', 'descendant__username')
    list_filter = ('depth',)