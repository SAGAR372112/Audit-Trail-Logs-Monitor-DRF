from rest_framework import permissions

class AuditLogPermission(permissions.BasePermission):
    """
    Custom permission for audit logs:
    - Admins can view all logs
    - Regular users can only view their own logs
    - Only admins can export logs
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Export permission only for admins
        if view.action == 'export':
            return request.user.is_staff
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admins can access any log
        if request.user.is_staff:
            return True
        
        # Users can only access their own logs
        return obj.user == request.user