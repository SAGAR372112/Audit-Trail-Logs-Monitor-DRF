from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import AuditLog

class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log certain actions
    """
    
    def process_response(self, request, response):
        # Skip logging for static files and admin
        if (request.path.startswith('/static/') or 
            request.path.startswith('/admin/') or
            request.path.startswith('/api/logs/')):
            return response
        
        # Log database modifications (POST, PUT, PATCH, DELETE)
        if (request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and 
            response.status_code < 400 and
            not isinstance(request.user, AnonymousUser)):
            
            action_map = {
                'POST': 'CREATE',
                'PUT': 'UPDATE',
                'PATCH': 'UPDATE',
                'DELETE': 'DELETE'
            }
            
            # Determine resource from URL
            resource = self.extract_resource_from_path(request.path)
            
            if resource:
                AuditLog.log_action(
                    user=request.user,
                    action=action_map[request.method],
                    resource=resource,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    session_id=request.session.session_key,
                    details={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code
                    }
                )
        
        return response
    
    def extract_resource_from_path(self, path):
        """Extract resource name from URL path"""
        # Simple extraction - can be enhanced based on your URL patterns
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'api':
            return parts[1].title()
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip