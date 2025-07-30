from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'username', 'user_email', 'action', 'resource', 
            'resource_id', 'ip_address', 'timestamp', 'severity', 
            'details', 'session_id'
        ]
        read_only_fields = ['id', 'timestamp']

class AuditLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['action', 'resource', 'resource_id', 'details']
    
    def create(self, validated_data):
        request = self.context['request']
        validated_data['user'] = request.user
        validated_data['ip_address'] = self.get_client_ip(request)
        validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        validated_data['session_id'] = request.session.session_key
        
        return AuditLog.log_action(**validated_data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip