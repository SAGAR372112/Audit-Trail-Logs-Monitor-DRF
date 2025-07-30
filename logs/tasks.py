from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .models import AuditLog

@shared_task
def check_failed_login_attempts(ip_address, username):
    """
    Check for multiple failed login attempts and send email alert
    """
    # Check last 1 minute for failed attempts from same IP
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    
    failed_attempts = AuditLog.objects.filter(
        action='FAILED_LOGIN',
        ip_address=ip_address,
        timestamp__gte=one_minute_ago
    ).count()
    
    if failed_attempts >= 5:
        send_security_alert.delay(
            ip_address=ip_address,
            username=username,
            attempts=failed_attempts,
            timeframe='1 minute'
        )
        
        # Also log this security event
        AuditLog.objects.create(
            action='FAILED_LOGIN',
            resource='Security',
            ip_address=ip_address,
            severity='CRITICAL',
            details={
                'alert_type': 'Multiple failed login attempts',
                'attempts': failed_attempts,
                'timeframe': '1 minute',
                'username': username
            }
        )

@shared_task
def send_security_alert(ip_address, username, attempts, timeframe):
    """
    Send email alert for security incidents
    """
    subject = f'Security Alert: Multiple Failed Login Attempts'
    
    message = f"""
    Security Alert - Audit Trail System
    
    Multiple failed login attempts detected:
    
    IP Address: {ip_address}
    Username: {username}
    Attempts: {attempts} failed logins
    Timeframe: {timeframe}
    Time: {timezone.now().isoformat()}
    
    Please investigate this activity immediately.
    
    This is an automated security alert from the Audit Trail System.
    """
    
    try:
        # Send to all admin users
        from django.contrib.auth.models import User
        admin_emails = list(
            User.objects.filter(is_staff=True, email__isnull=False)
            .exclude(email='')
            .values_list('email', flat=True)
        )
        
        if admin_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
            
            # Log the alert sending
            AuditLog.objects.create(
                action='CREATE',
                resource='SecurityAlert',
                ip_address='127.0.0.1',  # System action
                severity='MEDIUM',
                details={
                    'alert_sent': True,
                    'recipients': len(admin_emails),
                    'reason': f'{attempts} failed logins from {ip_address}'
                }
            )
    except Exception as e:
        # Log the failure
        AuditLog.objects.create(
            action='CREATE',
            resource='SecurityAlert',
            ip_address='127.0.0.1',
            severity='HIGH',
            details={
                'alert_sent': False,
                'error': str(e),
                'reason': f'{attempts} failed logins from {ip_address}'
            }
        )