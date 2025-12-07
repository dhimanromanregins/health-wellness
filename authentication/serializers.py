# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

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

class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()