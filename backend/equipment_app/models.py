"""
Database Models for Chemical Equipment Visualizer

This module defines the data structure for storing equipment data and dataset history.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Dataset(models.Model):
    """
    Model to store metadata about uploaded CSV datasets.
    Maintains history of last 5 uploads per user.
    """
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    uploaded_at = models.DateTimeField(default=timezone.now)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Analytics Summary (stored for quick access)
    total_equipment = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temperature = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class Equipment(models.Model):
    """
    Model to store individual equipment data from CSV uploads.
    Each equipment record belongs to a dataset.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipments')
    name = models.CharField(max_length=255, help_text="Equipment Name")
    type = models.CharField(max_length=100, help_text="Equipment Type")
    flowrate = models.FloatField(help_text="Flowrate value")
    pressure = models.FloatField(help_text="Pressure value")
    temperature = models.FloatField(help_text="Temperature value")
    
    class Meta:
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['dataset']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.type})"
