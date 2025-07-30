from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'resource', 'ip_address', 'timestamp', 'severity']
    list_filter = ['action', 'severity', 'timestamp', 'resource']
    search_fields = ['user__username', 'resource', 'ip_address', 'resource_id']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action', 'resource', 'resource_id', 'severity')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent', 'session_id')
        }),
        ('Metadata', {
            'fields': ('timestamp', 'details')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent modification
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser 