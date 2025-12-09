# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import CustomUser, UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer with validation"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Confirm password must match password"
    )
    email = serializers.EmailField(
        help_text="Valid email address for account verification"
    )
    first_name = serializers.CharField(
        max_length=30,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        max_length=30,
        help_text="User's last name"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

class UserLoginSerializer(serializers.Serializer):
    """User login serializer"""
    
    email = serializers.EmailField(
        help_text="User's email address"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="User's password"
    )

class EmailOTPSerializer(serializers.Serializer):
    """Email OTP serializer"""
    
    email = serializers.EmailField(
        help_text="Email address to send OTP to"
    )

class EmergencyContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_blank=True)
    phone = serializers.CharField(max_length=15, allow_blank=True)
    relationship = serializers.CharField(max_length=50, allow_blank=True)

class UserProfileSerializer(serializers.ModelSerializer):
    emergency_contact = EmergencyContactSerializer(write_only=True, required=False)
    age = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'health_goals', 'custom_goals', 'dietary_preferences', 
            'medical_conditions', 'health_concerns', 'occupation',
            'work_hours', 'travel_frequency', 'sleep_hours', 'activity_level',
            'energy_level', 'sleep_quality', 'wearables', 'emergency_contact',
            'user_data_complete', 'intake_completed_at'
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'profile'
        ]
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        emergency_contact = None
        
        if profile_data:
            emergency_contact = profile_data.pop('emergency_contact', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create profile
        if profile_data is not None:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            
            # Handle emergency contact
            if emergency_contact:
                profile.emergency_contact_name = emergency_contact.get('name', '')
                profile.emergency_contact_phone = emergency_contact.get('phone', '')
                profile.emergency_contact_relationship = emergency_contact.get('relationship', '')
            
            # Update profile fields
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            
            # Set intake completion timestamp if not already set
            if profile_data.get('user_data_complete') and not profile.intake_completed_at:
                profile.intake_completed_at = timezone.now()
            
            profile.save()
        
        return instance

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()