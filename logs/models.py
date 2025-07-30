from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('FAILED_LOGIN', 'Failed Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Record Created'),
        ('UPDATE', 'Record Updated'),
        ('DELETE', 'Record Deleted'),
        ('VIEW', 'Record Viewed'),
        ('EXPORT', 'Data Exported'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    resource = models.CharField(
        max_length=100, 
        help_text="Resource affected (e.g., User, Product, etc.)"
    )
    resource_id = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="ID of the affected resource"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        null=True, 
        blank=True,
        help_text="User agent string"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the action occurred"
    )
    severity = models.CharField(
        max_length=10, 
        choices=SEVERITY_CHOICES, 
        default='LOW',
        help_text="Severity level of the action"
    )
    details = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional details about the action"
    )
    session_id = models.CharField(
        max_length=40, 
        null=True, 
        blank=True,
        help_text="Session ID when action occurred"
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['severity', '-timestamp']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        return f"{username} - {self.action} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, resource, ip_address, **kwargs):
        """Convenience method to create audit log entries"""
        severity_map = {
            'FAILED_LOGIN': 'HIGH',
            'DELETE': 'MEDIUM',
            'LOGIN': 'LOW',
            'LOGOUT': 'LOW',
        }
        
        return cls.objects.create(
            user=user,
            action=action,
            resource=resource,
            ip_address=ip_address,
            severity=severity_map.get(action, 'LOW'),
            **kwargs
        )