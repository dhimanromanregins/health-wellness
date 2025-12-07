from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import EmailOTP, RegistrationSession
import logging


logger = logging.getLogger(__name__)


class OTPService:
    """
    Service class to handle OTP generation, sending, and verification
    """
    
    @staticmethod
    def send_otp_email(email, purpose='registration', session_id=None):
        """
        Generate and send OTP via email
        """
        try:
            # Clear any existing unverified OTPs for this email and purpose
            EmailOTP.objects.filter(
                email=email, 
                purpose=purpose, 
                is_verified=False
            ).delete()
            
            # Create new OTP
            otp_instance = EmailOTP.objects.create(
                email=email,
                purpose=purpose
            )
            
            # Update registration session if provided
            if session_id and purpose == 'registration':
                try:
                    session = RegistrationSession.objects.get(session_id=session_id)
                    session.status = 'email_sent'
                    session.save()
                except RegistrationSession.DoesNotExist:
                    pass
            
            # Prepare email context
            context = {
                'otp_code': otp_instance.otp_code,
                'email': email,
                'purpose': purpose.replace('_', ' ').title(),
                'expiry_minutes': getattr(settings, 'OTP_EXPIRY_MINUTES', 10),
                'company_name': 'VELORA',
                'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@velora.com')
            }
            
            # Choose template based on purpose
            template_name = f'authentication/emails/otp_{purpose}.html'
            
            # Render email content
            try:
                html_message = render_to_string(template_name, context)
                plain_message = strip_tags(html_message)
            except:
                # Fallback to simple message if template doesn't exist
                plain_message = f"""
Hello,

Your VELORA verification code is: {otp_instance.otp_code}

This code will expire in {getattr(settings, 'OTP_EXPIRY_MINUTES', 10)} minutes.

If you didn't request this code, please ignore this email.

Best regards,
VELORA Team
                """.strip()
                html_message = plain_message.replace('\n', '<br>')
            
            # Subject mapping
            subject_map = {
                'registration': 'Welcome to VELORA - Verify Your Email',
                'login': 'VELORA - Your Login Code',
                'password_reset': 'VELORA - Reset Your Password',
                'email_verification': 'VELORA - Verify Your Email'
            }
            
            subject = subject_map.get(purpose, 'VELORA - Verification Code')
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@velora.com'),
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"OTP sent successfully to {email} for {purpose}")
            return {
                'success': True, 
                'message': 'OTP sent successfully',
                'expires_at': otp_instance.expires_at
            }
            
        except Exception as e:
            logger.error(f"Failed to send OTP to {email}: {str(e)}")
            return {
                'success': False, 
                'message': 'Failed to send OTP. Please try again.'
            }
    
    @staticmethod
    def verify_otp(email, otp_code, purpose='registration'):
        """
        Verify OTP code
        """
        try:
            otp_instance = EmailOTP.objects.get(
                email=email,
                purpose=purpose,
                is_verified=False
            )
            
            # Check if OTP can be attempted
            if not otp_instance.can_attempt():
                if otp_instance.is_expired():
                    return {
                        'success': False,
                        'message': 'OTP has expired. Please request a new one.',
                        'error_code': 'OTP_EXPIRED'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Too many failed attempts. Please request a new OTP.',
                        'error_code': 'MAX_ATTEMPTS_EXCEEDED'
                    }
            
            # Increment attempt count
            otp_instance.attempts += 1
            otp_instance.save()
            
            # Verify OTP code
            if otp_instance.otp_code == otp_code:
                otp_instance.is_verified = True
                otp_instance.save()
                
                # Update registration session if applicable
                if purpose == 'registration':
                    try:
                        session = RegistrationSession.objects.get(
                            email=email,
                            status='email_sent'
                        )
                        session.status = 'email_verified'
                        session.save()
                    except RegistrationSession.DoesNotExist:
                        pass
                
                logger.info(f"OTP verified successfully for {email}")
                return {
                    'success': True,
                    'message': 'OTP verified successfully'
                }
            else:
                remaining_attempts = otp_instance.max_attempts - otp_instance.attempts
                return {
                    'success': False,
                    'message': f'Invalid OTP. {remaining_attempts} attempts remaining.',
                    'error_code': 'INVALID_OTP',
                    'remaining_attempts': remaining_attempts
                }
                
        except EmailOTP.DoesNotExist:
            return {
                'success': False,
                'message': 'Invalid or expired OTP. Please request a new one.',
                'error_code': 'OTP_NOT_FOUND'
            }
        except Exception as e:
            logger.error(f"OTP verification failed for {email}: {str(e)}")
            return {
                'success': False,
                'message': 'Verification failed. Please try again.',
                'error_code': 'VERIFICATION_ERROR'
            }
    
    @staticmethod
    def cleanup_expired_otps():
        """
        Clean up expired OTP records
        """
        try:
            expired_count = EmailOTP.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()[0]
            logger.info(f"Cleaned up {expired_count} expired OTP records")
            return expired_count
        except Exception as e:
            logger.error(f"Failed to cleanup expired OTPs: {str(e)}")
            return 0


class RegistrationService:
    """
    Service class to handle registration workflow
    """
    
    @staticmethod
    def initiate_registration(email):
        """
        Start the registration process by creating a session
        """
        try:
            # Clear any existing sessions for this email
            RegistrationSession.objects.filter(email=email).delete()
            
            # Create new registration session
            session = RegistrationSession.objects.create(email=email)
            
            logger.info(f"Registration initiated for {email}")
            return {
                'success': True,
                'session_id': session.session_id,
                'message': 'Registration session created successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate registration for {email}: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to initiate registration. Please try again.'
            }
    
    @staticmethod
    def get_session(session_id):
        """
        Get registration session by ID
        """
        try:
            session = RegistrationSession.objects.get(session_id=session_id)
            if session.is_expired():
                session.status = 'expired'
                session.save()
                return None
            return session
        except RegistrationSession.DoesNotExist:
            return None
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Clean up expired registration sessions
        """
        try:
            expired_count = RegistrationSession.objects.filter(
                expires_at__lt=timezone.now()
            ).update(status='expired')
            logger.info(f"Marked {expired_count} registration sessions as expired")
            return expired_count
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0