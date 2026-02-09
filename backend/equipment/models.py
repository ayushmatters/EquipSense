"""
Production-Quality Database Models for Chemical Equipment Parameter Visualizer

This module implements a robust database structure for managing equipment datasets
with automatic history management and analytics storage.

Author: Senior Django Backend Architect
Date: February 6, 2026
"""

import os
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class DatasetHistory(models.Model):
    """
    Store metadata about uploaded CSV datasets and analytics summary.
    
    Implements automatic history management to maintain only the last 5 datasets
    per user. Tracks comprehensive analytics and file metadata for efficient
    retrieval and reporting.
    
    Attributes:
        user: Link to Django User model (creator of dataset)
        dataset_name: Human-readable name for the dataset
        file: FileField storing the actual CSV file
        uploaded_at: Timestamp of upload (auto-generated)
        total_equipment_count: Total number of equipment records in dataset
        avg_flowrate: Average flowrate across all equipment
        avg_pressure: Average pressure across all equipment
        avg_temperature: Average temperature across all equipment
        type_distribution: JSON structure storing equipment type counts
        file_size: Size of uploaded file in bytes
        is_active: Flag for soft deletion (inactive datasets can be archived)
    """
    
    # User relationship - CASCADE ensures cleanup when user is deleted
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='equipment_datasets',
        db_index=True,
        help_text="User who uploaded this dataset"
    )
    
    # Dataset identification and file storage
    dataset_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Name of the dataset (typically filename without extension)"
    )
    
    file = models.FileField(
        upload_to='datasets/%Y/%m/%d/',  # Organized by date for better file management
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        help_text="CSV file containing equipment data"
    )
    
    # Temporal tracking
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when dataset was uploaded"
    )
    
    # Analytics summary fields for quick dashboard access
    total_equipment_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total number of equipment records in this dataset"
    )
    
    avg_flowrate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Average flowrate across all equipment in dataset"
    )
    
    avg_pressure = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Average pressure across all equipment in dataset"
    )
    
    avg_temperature = models.FloatField(
        default=0.0,
        help_text="Average temperature across all equipment in dataset"
    )
    
    # JSON field for flexible type distribution storage
    type_distribution = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dictionary mapping equipment types to their counts"
    )
    
    # File metadata
    file_size = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="File size in bytes"
    )
    
    # Status management
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Active status - False indicates archived dataset"
    )
    
    class Meta:
        """Metadata for DatasetHistory model"""
        ordering = ['-uploaded_at']  # Most recent first
        verbose_name = 'Dataset History'
        verbose_name_plural = 'Dataset Histories'
        indexes = [
            models.Index(fields=['-uploaded_at', 'user']),  # Composite index for user queries
            models.Index(fields=['is_active', 'user']),     # Active datasets per user
        ]
        
    def __str__(self):
        """String representation showing dataset name and upload date"""
        return f"{self.dataset_name} - {self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def clean(self):
        """
        Custom validation for DatasetHistory model.
        
        Validates:
        - Dataset name is not empty
        - File size is reasonable (max 10MB)
        - Analytics values are non-negative
        """
        super().clean()
        
        # Validate dataset name
        if not self.dataset_name or not self.dataset_name.strip():
            raise ValidationError({
                'dataset_name': 'Dataset name cannot be empty or whitespace only.'
            })
        
        # Validate file size (max 10MB for performance)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        if self.file_size > MAX_FILE_SIZE:
            raise ValidationError({
                'file_size': f'File size ({self.file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (10MB).'
            })
        
        # Validate analytics values
        if self.total_equipment_count < 0:
            raise ValidationError({
                'total_equipment_count': 'Total equipment count cannot be negative.'
            })
        
        if self.avg_flowrate < 0 or self.avg_pressure < 0:
            raise ValidationError(
                'Average flowrate and pressure must be non-negative values.'
            )
    
    def save(self, *args, **kwargs):
        """
        Override save to perform validation and set file size automatically.
        """
        # Calculate file size if not set
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (AttributeError, OSError):
                self.file_size = 0
        
        # Run full validation
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """
        Return human-readable file size.
        
        Returns:
            str: File size formatted as KB, MB, or GB
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def get_type_distribution_display(self):
        """
        Return formatted type distribution for display.
        
        Returns:
            str: Comma-separated list of types and counts
        """
        if not self.type_distribution:
            return "No data"
        
        return ", ".join([
            f"{type_name}: {count}" 
            for type_name, count in self.type_distribution.items()
        ])
    
    @property
    def age_in_days(self):
        """
        Calculate how many days ago the dataset was uploaded.
        
        Returns:
            int: Number of days since upload
        """
        return (timezone.now() - self.uploaded_at).days


@receiver(pre_delete, sender=DatasetHistory)
def delete_dataset_file(sender, instance, **kwargs):
    """
    Signal handler to automatically delete associated file when DatasetHistory is deleted.
    
    This ensures no orphaned files remain in the file system after dataset deletion.
    
    Args:
        sender: The model class (DatasetHistory)
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments
    """
    if instance.file:
        try:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
        except (ValueError, OSError) as e:
            # File doesn't exist or can't be deleted - log but don't raise
            print(f"Warning: Could not delete file {instance.file.name}: {e}")
