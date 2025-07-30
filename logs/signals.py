from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AuditLog
from .tasks import check_failed_login_attempts

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login"""
    AuditLog.log_action(
        user=user,
        action='LOGIN',
        resource='User',
        resource_id=str(user.id),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        session_id=request.session.session_key,
        details={'login_method': 'web'}
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout"""
    if user:
        AuditLog.log_action(
            user=user,
            action='LOGOUT',
            resource='User',
            resource_id=str(user.id),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=request.session.session_key
        )

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts and trigger alert check"""
    username = credentials.get('username', 'Unknown')
    ip_address = get_client_ip(request)
    
    # Try to get user object
    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        pass
    
    AuditLog.log_action(
        user=user,
        action='FAILED_LOGIN',
        resource='User',
        resource_id=username,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details={
            'attempted_username': username,
            'reason': 'Invalid credentials'
        }
    )
    
    # Trigger async task to check for multiple failed attempts
    check_failed_login_attempts.delay(ip_address, username)

def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip