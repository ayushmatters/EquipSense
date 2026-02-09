"""
Django Admin Configuration for Equipment Dataset Management

This module configures the Django admin interface for the DatasetHistory model
with advanced features for efficient data management and monitoring.

Author: Senior Django Backend Architect
Date: February 6, 2026
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DatasetHistory


@admin.register(DatasetHistory)
class DatasetHistoryAdmin(admin.ModelAdmin):
    """
    Advanced admin interface for DatasetHistory model.
    
    Features:
    - Comprehensive list display with calculated fields
    - Advanced search and filtering
    - Read-only fields for analytics
    - Custom actions for bulk operations
    - Inline file download links
    """
    
    # List view configuration
    list_display = (
        'id',
        'dataset_name_display',
        'user_link',
        'total_equipment_count',
        'file_size_display',
        'uploaded_at_display',
        'status_badge',
        'download_link',
    )
    
    list_display_links = ('id', 'dataset_name_display')
    
    # Search functionality
    search_fields = (
        'dataset_name',
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    
    # Filtering sidebar
    list_filter = (
        'is_active',
        'uploaded_at',
        'user',
    )
    
    # Ordering
    ordering = ('-uploaded_at',)
    
    # Items per page
    list_per_page = 25
    
    # Read-only fields (computed/auto-generated)
    readonly_fields = (
        'uploaded_at',
        'file_size',
        'file_size_display_detailed',
        'age_display',
        'type_distribution_display',
        'analytics_summary',
    )
    
    # Fieldset organization for detail view
    fieldsets = (
        ('Dataset Information', {
            'fields': (
                'dataset_name',
                'user',
                'file',
                'is_active',
            )
        }),
        ('Upload Metadata', {
            'fields': (
                'uploaded_at',
                'file_size',
                'file_size_display_detailed',
                'age_display',
            ),
            'classes': ('collapse',),
        }),
        ('Analytics Summary', {
            'fields': (
                'total_equipment_count',
                'avg_flowrate',
                'avg_pressure',
                'avg_temperature',
                'type_distribution',
                'type_distribution_display',
                'analytics_summary',
            ),
            'description': 'Automatically calculated analytics from the uploaded dataset.',
        }),
    )
    
    # Custom actions
    actions = [
        'mark_as_active',
        'mark_as_inactive',
        'export_analytics_csv',
    ]
    
    # ==================== Custom Display Methods ====================
    
    @admin.display(description='Dataset Name', ordering='dataset_name')
    def dataset_name_display(self, obj):
        """Display dataset name with icon"""
        return format_html(
            '<strong>📊 {}</strong>',
            obj.dataset_name
        )
    
    @admin.display(description='User', ordering='user__username')
    def user_link(self, obj):
        """Display clickable link to user detail page"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}" style="color: #447e9b;">👤 {}</a>',
            url,
            obj.user.username
        )
    
    @admin.display(description='File Size', ordering='file_size')
    def file_size_display(self, obj):
        """Display human-readable file size"""
        return obj.get_file_size_display()
    
    @admin.display(description='Uploaded', ordering='uploaded_at')
    def uploaded_at_display(self, obj):
        """Display formatted upload timestamp with relative time"""
        days_ago = obj.age_in_days
        if days_ago == 0:
            relative = "Today"
        elif days_ago == 1:
            relative = "Yesterday"
        else:
            relative = f"{days_ago} days ago"
        
        return format_html(
            '<span title="{}">{}</span>',
            obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            relative
        )
    
    @admin.display(description='Status', ordering='is_active')
    def status_badge(self, obj):
        """Display colored status badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px; font-weight: bold;">'
                '✓ Active</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 10px; border-radius: 3px;">'
            '○ Inactive</span>'
        )
    
    @admin.display(description='Download')
    def download_link(self, obj):
        """Display download link for the file"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="color: #447e9b; font-weight: bold;">'
                '⬇ Download</a>',
                obj.file.url
            )
        return format_html('<span style="color: #999;">No file</span>')
    
    # ==================== Read-only Detail Fields ====================
    
    @admin.display(description='File Size (Detailed)')
    def file_size_display_detailed(self, obj):
        """Display detailed file size with both bytes and formatted size"""
        return format_html(
            '<strong>{}</strong> ({:,} bytes)',
            obj.get_file_size_display(),
            obj.file_size
        )
    
    @admin.display(description='Dataset Age')
    def age_display(self, obj):
        """Display how long ago the dataset was uploaded"""
        days = obj.age_in_days
        if days == 0:
            return "Uploaded today"
        elif days == 1:
            return "Uploaded yesterday"
        else:
            return f"Uploaded {days} days ago"
    
    @admin.display(description='Type Distribution')
    def type_distribution_display(self, obj):
        """Display formatted type distribution"""
        if not obj.type_distribution:
            return format_html('<em style="color: #999;">No data</em>')
        
        html_parts = ['<ul style="margin: 0; padding-left: 20px;">']
        for equipment_type, count in sorted(obj.type_distribution.items()):
            html_parts.append(
                f'<li><strong>{equipment_type}:</strong> {count} units</li>'
            )
        html_parts.append('</ul>')
        
        return mark_safe(''.join(html_parts))
    
    @admin.display(description='Analytics Summary')
    def analytics_summary(self, obj):
        """Display comprehensive analytics summary in a formatted box"""
        html = f'''
        <div style="background: #f8f9fa; border: 1px solid #dee2e6; 
                    border-radius: 5px; padding: 15px; margin: 10px 0;">
            <h4 style="margin-top: 0; color: #495057;">📈 Dataset Analytics</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #dee2e6;">
                        <strong>Total Equipment:</strong>
                    </td>
                    <td style="padding: 5px; border-bottom: 1px solid #dee2e6; text-align: right;">
                        {obj.total_equipment_count:,}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #dee2e6;">
                        <strong>Average Flowrate:</strong>
                    </td>
                    <td style="padding: 5px; border-bottom: 1px solid #dee2e6; text-align: right;">
                        {obj.avg_flowrate:.2f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 5px; border-bottom: 1px solid #dee2e6;">
                        <strong>Average Pressure:</strong>
                    </td>
                    <td style="padding: 5px; border-bottom: 1px solid #dee2e6; text-align: right;">
                        {obj.avg_pressure:.2f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 5px;">
                        <strong>Average Temperature:</strong>
                    </td>
                    <td style="padding: 5px; text-align: right;">
                        {obj.avg_temperature:.2f}
                    </td>
                </tr>
            </table>
        </div>
        '''
        return mark_safe(html)
    
    # ==================== Custom Actions ====================
    
    @admin.action(description='✓ Mark selected datasets as Active')
    def mark_as_active(self, request, queryset):
        """Bulk action to mark datasets as active"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Successfully marked {updated} dataset(s) as active.',
            level='SUCCESS'
        )
    
    @admin.action(description='○ Mark selected datasets as Inactive')
    def mark_as_inactive(self, request, queryset):
        """Bulk action to mark datasets as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Successfully marked {updated} dataset(s) as inactive.',
            level='WARNING'
        )
    
    @admin.action(description='📊 Export analytics to CSV')
    def export_analytics_csv(self, request, queryset):
        """Bulk action to export dataset analytics to CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="dataset_analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Dataset Name', 'User', 'Upload Date',
            'Total Equipment', 'Avg Flowrate', 'Avg Pressure',
            'Avg Temperature', 'File Size (bytes)', 'Status'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.dataset_name,
                obj.user.username,
                obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                obj.total_equipment_count,
                obj.avg_flowrate,
                obj.avg_pressure,
                obj.avg_temperature,
                obj.file_size,
                'Active' if obj.is_active else 'Inactive'
            ])
        
        self.message_user(
            request,
            f'Successfully exported {queryset.count()} dataset(s) to CSV.',
            level='SUCCESS'
        )
        
        return response
    
    # ==================== Override Methods ====================
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related for better performance.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    def has_delete_permission(self, request, obj=None):
        """
        Allow deletion only for superusers or staff with explicit permission.
        """
        return request.user.is_superuser or super().has_delete_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        """
        Custom save logic - could trigger history cleanup here if needed.
        """
        super().save_model(request, obj, form, change)
        
        # Optionally trigger history cleanup after save
        # from .services.history_manager import limit_dataset_history
        # limit_dataset_history(obj.user)
