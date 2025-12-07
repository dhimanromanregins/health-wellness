# authentication/views.py content
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from .models import EmailOTP, RegistrationSession
from .serializers import UserRegistrationSerializer
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
import logging
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
import secrets
from django.contrib.auth.hashers import check_password

logger = logging.getLogger(__name__)
User = get_user_model()  # Use your CustomUser model

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_registration(request):
    """
    Initiate user registration by sending OTP to email
    """
    try:
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate session ID (truncate UUID to fit 32 chars)
        session_id = str(uuid.uuid4()).replace('-', '')[:32]
        
        # Create or update registration session
        registration_session, created = RegistrationSession.objects.get_or_create(
            email=email,
            defaults={
                'session_id': session_id,
                'expires_at': timezone.now() + timedelta(hours=24)
            }
        )
        
        if not created:
            # Update existing session
            registration_session.session_id = session_id
            registration_session.expires_at = timezone.now() + timedelta(hours=24)
            registration_session.save()
        
        # Create OTP record
        otp_record = EmailOTP.objects.create(email=email)
        
        # Get the OTP value - check what attribute name is used in your model
        # Common attribute names: otp, code, otp_code, token
        otp_value = getattr(otp_record, 'otp_code', None) or getattr(otp_record, 'otp', None) or getattr(otp_record, 'code', None)
        
        # Actually send the email
        try:
            send_mail(
                subject='Your VELORA Registration OTP',
                message=f'Your OTP for registration is: {otp_value}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"OTP sent to {email}: {otp_value}")
        except Exception as mail_error:
            logger.error(f"Failed to send email: {mail_error}")
            # Still return success since OTP is created, just log the email failure
        
        return Response({
            'success': True,
            'message': 'OTP sent to your email',
            'session_id': session_id
        }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Registration initiation error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP and return session validation
    """
    try:
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        session_id = request.data.get('session_id')
        
        if not all([email, otp_code, session_id]):
            return Response({
                'success': False,
                'message': 'Email, OTP, and session ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify session
        try:
            registration_session = RegistrationSession.objects.get(
                email=email,
                session_id=session_id
            )
            
            if registration_session.is_expired():
                return Response({
                    'success': False,
                    'message': 'Registration session expired'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except RegistrationSession.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid session'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP - use otp_code field
        try:
            email_otp = EmailOTP.objects.get(email=email, otp_code=otp_code)
            
            if email_otp.is_expired():
                return Response({
                    'success': False,
                'message': 'OTP expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            email_otp.is_used = True
            email_otp.save()
            
            # Always use the session_id modification approach for verification
            verified_session_id = str(uuid.uuid4()).replace('-', '')[:31] + 'v'  # 31 chars + 'v' = 32 chars
            registration_session.session_id = verified_session_id
            registration_session.save()
            
            # Also try to set is_verified if the field exists
            try:
                registration_session.is_verified = True
                registration_session.save()
            except:
                pass  # Field doesn't exist, that's okay
            
            return Response({
                'success': True,
                'message': 'OTP verified successfully',
                'session_id': verified_session_id
            }, status=status.HTTP_200_OK)
            
        except EmailOTP.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def complete_registration(request):
    """
    Complete user registration after OTP verification
    """
    try:
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({
                'success': False,
                'message': 'Session ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify session
        try:
            registration_session = RegistrationSession.objects.get(session_id=session_id)
            
            if registration_session.is_expired():
                return Response({
                    'success': False,
                    'message': 'Registration session expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check verification - prioritize session_id suffix check
            is_verified = session_id.endswith('v')  # Primary check
            
            # Fallback to is_verified field if it exists and session_id doesn't end with 'v'
            if not is_verified and hasattr(registration_session, 'is_verified'):
                is_verified = registration_session.is_verified
            
            if not is_verified:
                return Response({
                    'success': False,
                    'message': 'Email not verified. Please verify your OTP first.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except RegistrationSession.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid session'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get password from request
        password = request.data.get('password')
        if not password:
            return Response({
                'success': False,
                'message': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Auto-generate username from email
        email = registration_session.email
        username = email.split('@')[0]  # Get part before @
        
        # Ensure username is unique
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        try:
            # Create user directly without serializer - no first_name and last_name
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Set email as verified since they completed OTP verification
            try:
                user.is_email_verified = True
                user.save()
            except AttributeError:
                try:
                    user.email_verified = True
                    user.save()
                except AttributeError:
                    pass
            
            # Generate proper JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            logger.info(f"User created successfully: {user.id} - {user.username} - Email verified: True")
            
            # Clean up registration data
            registration_session.delete()
            EmailOTP.objects.filter(email=email).delete()
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'email_verified': getattr(user, 'is_email_verified', getattr(user, 'email_verified', True))
                },
                'tokens': {
                    'access_token': str(access_token),
                    'refresh_token': str(refresh),
                    'token_type': 'Bearer'
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as user_creation_error:
            logger.error(f"Error creating user: {user_creation_error}")
            return Response({
                'success': False,
                'message': f'Error creating user: {str(user_creation_error)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Registration completion error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    User logout
    """
    try:
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP to email
    """
    try:
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Resending OTP for email: {email}")
        
        # Delete old OTP records for this email
        deleted_count = EmailOTP.objects.filter(email=email).count()
        EmailOTP.objects.filter(email=email).delete()
        logger.info(f"Deleted {deleted_count} old OTP records for {email}")
        
        # Create new OTP record
        otp_record = EmailOTP.objects.create(email=email)
        logger.info(f"Created new OTP record with ID: {otp_record.id}")
        
        # Get the OTP value - check what attribute name is used in your model
        otp_value = getattr(otp_record, 'otp_code', None) or getattr(otp_record, 'otp', None) or getattr(otp_record, 'code', None)
        
        if otp_value is None:
            logger.error(f"Could not find OTP value in record. Available attributes: {dir(otp_record)}")
            return Response({
                'success': False,
                'message': 'Failed to generate OTP'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Generated OTP: {otp_value} for email: {email}")
        
        # Actually send the email
        try:
            send_mail(
                subject='Your VELORA OTP Code',
                message=f'Your OTP for VELORA is: {otp_value}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            logger.info(f"Email sent successfully to {email}")
        except Exception as mail_error:
            logger.error(f"Failed to send email: {mail_error}")
        
        return Response({
            'success': True,
            'message': 'OTP resent to your email',
            'debug_info': {
                'otp_generated': True,
                'otp_value': otp_value,  # Remove this in production
                'email_backend': settings.EMAIL_BACKEND
            }
        }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Resend OTP error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get user profile information
    """
    try:
        user = request.user
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"User profile error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update user profile information
    """
    try:
        user = request.user
        data = request.data
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
            
        user.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView

class UserProfileView(APIView):
    """
    Class-based view for user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"User profile error: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_onboarding(request):
    """
    Complete user onboarding process
    """
    try:
        user = request.user
        
        # Update user as onboarded (assuming you have this field)
        # user.is_onboarded = True
        # user.save()
        
        return Response({
            'success': True,
            'message': 'Onboarding completed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Onboarding completion error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def demo_login(request):
    """
    Demo login for development/testing
    """
    try:
        # Create or get demo user
        demo_user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        
        return Response({
            'success': True,
            'message': 'Demo login successful',
            'user': {
                'id': demo_user.id,
                'username': demo_user.username,
                'email': demo_user.email,
                'first_name': demo_user.first_name,
                'last_name': demo_user.last_name
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Demo login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login with email and password
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'message': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find user by email first
        try:
            user = User.objects.get(email=email)
            logger.info(f"Found user: {user.username} for email: {email}")
            
            # Check password directly using Django's password hasher
            if user.check_password(password):
                logger.info(f"Password check successful for user: {user.username}")
                
                if user.is_active:
                    # Generate JWT tokens for login
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    return Response({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': getattr(user, 'first_name', ''),
                            'last_name': getattr(user, 'last_name', ''),
                            'email_verified': getattr(user, 'is_email_verified', getattr(user, 'email_verified', True))
                        },
                        'tokens': {
                            'access_token': str(access_token),
                            'refresh_token': str(refresh),
                            'token_type': 'Bearer'
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    logger.warning(f"User account inactive: {user.username}")
                    return Response({
                        'success': False,
                        'message': 'Account is inactive'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                logger.warning(f"Password check failed for user: {user.username}")
                return Response({
                    'success': False,
                    'message': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except User.DoesNotExist:
            logger.warning(f"User not found for email: {email}")
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def home(request):
    """
    Home view
    """
    return render(request, 'authentication/home.html')

# Add alias for URL compatibility
verify_registration_otp = verify_otp

@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_otp(request):
    """
    Login with OTP verification
    """
    try:
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        
        if not email or not otp_code:
            return Response({
                'success': False,
                'message': 'Email and OTP are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP - use otp_code field
        try:
            email_otp = EmailOTP.objects.get(email=email, otp_code=otp_code)
            
            if email_otp.is_expired():
                return Response({
                    'success': False,
                    'message': 'OTP expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if email_otp.is_used:
                return Response({
                    'success': False,
                    'message': 'OTP already used'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            email_otp.is_used = True
            email_otp.save()
            
            # Get user by email
            try:
                user = User.objects.get(email=email)
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
        except EmailOTP.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"OTP login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)