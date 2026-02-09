from django.contrib import admin
from .models import Dataset, Equipment

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'uploaded_by', 'uploaded_at', 'equipment_count']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['filename', 'uploaded_by__username']
    readonly_fields = ['uploaded_at']
    
    def equipment_count(self, obj):
        return obj.equipments.count()
    equipment_count.short_description = 'Equipment Count'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['type', 'dataset']
    search_fields = ['name', 'type']
