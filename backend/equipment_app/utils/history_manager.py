"""
Dataset History Manager

This module manages the dataset upload history, maintaining only the last 5 uploads per user.
"""

from django.conf import settings
from ..models import Dataset


class HistoryManager:
    """
    Service class for managing dataset upload history.
    Automatically maintains only the last N datasets per user.
    """
    
    @staticmethod
    def get_history_limit():
        """Get the history limit from settings"""
        return getattr(settings, 'DATASET_HISTORY_LIMIT', 5)
    
    @staticmethod
    def cleanup_old_datasets(user):
        """
        Remove oldest datasets beyond the history limit for a specific user.
        
        Args:
            user: Django User object
        """
        limit = HistoryManager.get_history_limit()
        
        # Get all datasets for user, ordered by upload date (newest first)
        datasets = Dataset.objects.filter(uploaded_by=user).order_by('-uploaded_at')
        
        # If count exceeds limit, delete the oldest ones
        if datasets.count() > limit:
            datasets_to_delete = datasets[limit:]
            for dataset in datasets_to_delete:
                dataset.delete()  # This will cascade delete related Equipment objects
    
    @staticmethod
    def get_user_history(user, limit=None):
        """
        Get upload history for a specific user.
        
        Args:
            user: Django User object
            limit: Optional limit override
            
        Returns:
            QuerySet of Dataset objects
        """
        if limit is None:
            limit = HistoryManager.get_history_limit()
        
        return Dataset.objects.filter(uploaded_by=user).order_by('-uploaded_at')[:limit]
    
    @staticmethod
    def get_dataset_count(user):
        """
        Get total number of datasets uploaded by user.
        
        Args:
            user: Django User object
            
        Returns:
            Integer count
        """
        return Dataset.objects.filter(uploaded_by=user).count()
    
    @staticmethod
    def add_dataset_with_cleanup(user, dataset):
        """
        Add a new dataset and automatically cleanup old ones.
        
        Args:
            user: Django User object
            dataset: Dataset object to add
        """
        # Dataset is already saved, just cleanup old ones
        HistoryManager.cleanup_old_datasets(user)
