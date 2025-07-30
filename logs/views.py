import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogCreateSerializer
from .permissions import AuditLogPermission

class AuditLogViewSet(viewsets.ModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, AuditLogPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'severity', 'resource']
    search_fields = ['user__username', 'resource', 'ip_address']
    ordering_fields = ['timestamp', 'severity']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user')
        
        # Admins see all logs, users see only their own
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Date range filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                queryset = queryset.filter(timestamp__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
                queryset = queryset.filter(timestamp__lte=end_date)
            except ValueError:
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AuditLogCreateSerializer
        return AuditLogSerializer
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export logs to CSV - Admin only"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can export logs'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Username', 'Email', 'Action', 'Resource', 'Resource ID',
            'IP Address', 'Timestamp', 'Severity', 'Details'
        ])
        
        queryset = self.filter_queryset(self.get_queryset())
        for log in queryset:
            writer.writerow([
                log.id,
                log.user.username if log.user else 'Anonymous',
                log.user.email if log.user else '',
                log.action,
                log.resource,
                log.resource_id or '',
                log.ip_address,
                log.timestamp.isoformat(),
                log.severity,
                str(log.details)
            ])
        
        # Log the export action
        AuditLog.log_action(
            user=request.user,
            action='EXPORT',
            resource='AuditLog',
            ip_address=self.get_client_ip(request),
            details={'exported_count': queryset.count()}
        )
        
        return response
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get log statistics - Admin only"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can view statistics'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        now = timezone.now()
        
        stats = {
            'total_logs': queryset.count(),
            'logs_today': queryset.filter(timestamp__date=now.date()).count(),
            'logs_this_week': queryset.filter(timestamp__gte=now - timedelta(days=7)).count(),
            'failed_logins_today': queryset.filter(
                action='FAILED_LOGIN',
                timestamp__date=now.date()
            ).count(),
            'top_actions': list(
                queryset.values('action')
                .annotate(count=Count('action'))
                .order_by('-count')[:5]
            ),
            'top_ips': list(
                queryset.values('ip_address')
                .annotate(count=Count('ip_address'))
                .order_by('-count')[:10]
            )
        }
        
        return Response(stats)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip