"""
Dataset History Management Service

This module provides production-grade services for managing dataset history,
implementing automatic cleanup to maintain only the last 5 datasets per user.

Features:
- Automatic cleanup of old datasets
- Transactional operations for data integrity
- File system cleanup alongside database deletion
- Comprehensive error handling and logging
- Optimized database queries

Author: Senior Django Backend Architect
Date: February 6, 2026
"""

import logging
from typing import Optional, List
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


# Configure module logger
logger = logging.getLogger(__name__)


# Configuration constant
MAX_DATASETS_PER_USER = 5


def get_user_dataset_count(user: User) -> int:
    """
    Get the total number of active datasets for a user.
    
    Args:
        user: Django User instance
        
    Returns:
        int: Count of active datasets for the user
        
    Example:
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.get(username='john')
        >>> count = get_user_dataset_count(user)
        >>> print(f"User has {count} datasets")
    """
    from equipment.models import DatasetHistory
    
    return DatasetHistory.objects.filter(
        user=user,
        is_active=True
    ).count()


def limit_dataset_history(user: User, max_datasets: int = MAX_DATASETS_PER_USER) -> dict:
    """
    Enforce dataset history limit by deleting oldest datasets when limit is exceeded.
    
    This function maintains only the most recent N datasets per user. When a new
    dataset is uploaded and the count exceeds the limit, the oldest datasets are
    automatically deleted from both the database and file system.
    
    The deletion process is wrapped in a database transaction to ensure atomicity.
    If any error occurs during deletion, all changes are rolled back.
    
    Args:
        user: Django User instance whose datasets should be limited
        max_datasets: Maximum number of datasets to keep (default: 5)
        
    Returns:
        dict: Summary of operation with keys:
            - deleted_count: Number of datasets deleted
            - remaining_count: Number of datasets remaining
            - deleted_ids: List of deleted dataset IDs
            - deleted_names: List of deleted dataset names
            - success: Boolean indicating operation success
            - message: Human-readable status message
            
    Raises:
        ValueError: If user is None or max_datasets < 1
        
    Example:
        >>> from django.contrib.auth.models import User
        >>> user = User.objects.get(username='john')
        >>> result = limit_dataset_history(user)
        >>> print(result['message'])
        'Deleted 2 old dataset(s). 5 datasets remaining.'
        
    Notes:
        - Operates only on active datasets (is_active=True)
        - Deletion cascade relationships handled by Django
        - Signal handlers automatically delete associated files
        - Uses transaction.atomic() for data integrity
        - Logs all operations for audit trail
    """
    from equipment.models import DatasetHistory
    
    # Input validation
    if user is None:
        raise ValueError("User cannot be None")
    
    if max_datasets < 1:
        raise ValueError("max_datasets must be at least 1")
    
    try:
        # Get all active datasets for user, ordered by most recent first
        user_datasets = DatasetHistory.objects.filter(
            user=user,
            is_active=True
        ).order_by('-uploaded_at')
        
        total_count = user_datasets.count()
        
        # Check if cleanup is needed
        if total_count <= max_datasets:
            logger.info(
                f"User {user.username} has {total_count} datasets. "
                f"No cleanup needed (limit: {max_datasets})"
            )
            return {
                'deleted_count': 0,
                'remaining_count': total_count,
                'deleted_ids': [],
                'deleted_names': [],
                'success': True,
                'message': f'No cleanup needed. {total_count} dataset(s) within limit.'
            }
        
        # Calculate how many datasets need to be deleted
        datasets_to_delete_count = total_count - max_datasets
        
        # Get the datasets that should be deleted (oldest ones)
        datasets_to_delete = list(
            user_datasets[max_datasets:]  # Skip first N (most recent)
        )
        
        # Track what will be deleted for return value
        deleted_ids = [ds.id for ds in datasets_to_delete]
        deleted_names = [ds.dataset_name for ds in datasets_to_delete]
        
        # Perform deletion in atomic transaction
        with transaction.atomic():
            # Delete datasets (signal handlers will clean up files)
            for dataset in datasets_to_delete:
                logger.info(
                    f"Deleting old dataset: ID={dataset.id}, "
                    f"Name={dataset.dataset_name}, "
                    f"Uploaded={dataset.uploaded_at}"
                )
                dataset.delete()
        
        remaining_count = max_datasets
        
        logger.info(
            f"Successfully cleaned up {datasets_to_delete_count} dataset(s) "
            f"for user {user.username}. {remaining_count} datasets remaining."
        )
        
        return {
            'deleted_count': datasets_to_delete_count,
            'remaining_count': remaining_count,
            'deleted_ids': deleted_ids,
            'deleted_names': deleted_names,
            'success': True,
            'message': (
                f'Deleted {datasets_to_delete_count} old dataset(s). '
                f'{remaining_count} datasets remaining.'
            )
        }
        
    except Exception as e:
        logger.error(
            f"Error during dataset history cleanup for user {user.username}: {e}",
            exc_info=True
        )
        return {
            'deleted_count': 0,
            'remaining_count': total_count if 'total_count' in locals() else 0,
            'deleted_ids': [],
            'deleted_names': [],
            'success': False,
            'message': f'Error during cleanup: {str(e)}'
        }


def get_user_datasets(
    user: User,
    active_only: bool = True,
    limit: Optional[int] = None
) -> List:
    """
    Retrieve datasets for a specific user.
    
    Args:
        user: Django User instance
        active_only: If True, return only active datasets (default: True)
        limit: Maximum number of datasets to return (None for all)
        
    Returns:
        List of DatasetHistory instances ordered by upload date (newest first)
        
    Example:
        >>> datasets = get_user_datasets(user, limit=5)
        >>> for ds in datasets:
        >>>     print(f"{ds.dataset_name}: {ds.total_equipment_count} items")
    """
    from equipment.models import DatasetHistory
    
    queryset = DatasetHistory.objects.filter(user=user)
    
    if active_only:
        queryset = queryset.filter(is_active=True)
    
    queryset = queryset.order_by('-uploaded_at')
    
    if limit:
        queryset = queryset[:limit]
    
    return list(queryset)


def archive_old_datasets(user: User, days_threshold: int = 30) -> dict:
    """
    Archive (mark as inactive) datasets older than specified days.
    
    This is a soft-delete operation that keeps the data but marks it as inactive.
    
    Args:
        user: Django User instance
        days_threshold: Number of days after which datasets should be archived
        
    Returns:
        dict: Summary with archived_count and archived_ids
        
    Example:
        >>> # Archive datasets older than 90 days
        >>> result = archive_old_datasets(user, days_threshold=90)
        >>> print(f"Archived {result['archived_count']} datasets")
    """
    from equipment.models import DatasetHistory
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days_threshold)
    
    old_datasets = DatasetHistory.objects.filter(
        user=user,
        is_active=True,
        uploaded_at__lt=cutoff_date
    )
    
    archived_ids = list(old_datasets.values_list('id', flat=True))
    archived_count = old_datasets.update(is_active=False)
    
    logger.info(
        f"Archived {archived_count} dataset(s) older than {days_threshold} days "
        f"for user {user.username}"
    )
    
    return {
        'archived_count': archived_count,
        'archived_ids': archived_ids,
        'success': True,
        'message': f'Archived {archived_count} old dataset(s).'
    }


def cleanup_inactive_datasets(user: User) -> dict:
    """
    Permanently delete all inactive datasets for a user.
    
    This is a hard-delete operation that removes data and files.
    
    Args:
        user: Django User instance
        
    Returns:
        dict: Summary with deleted_count
        
    Warning:
        This permanently deletes data. Use with caution.
        
    Example:
        >>> result = cleanup_inactive_datasets(user)
        >>> print(f"Permanently deleted {result['deleted_count']} datasets")
    """
    from equipment.models import DatasetHistory
    
    inactive_datasets = DatasetHistory.objects.filter(
        user=user,
        is_active=False
    )
    
    deleted_count = inactive_datasets.count()
    
    with transaction.atomic():
        inactive_datasets.delete()
    
    logger.info(
        f"Permanently deleted {deleted_count} inactive dataset(s) "
        f"for user {user.username}"
    )
    
    return {
        'deleted_count': deleted_count,
        'success': True,
        'message': f'Permanently deleted {deleted_count} inactive dataset(s).'
    }


def get_dataset_statistics(user: User) -> dict:
    """
    Get comprehensive statistics about user's datasets.
    
    Args:
        user: Django User instance
        
    Returns:
        dict: Statistics including counts, sizes, and averages
        
    Example:
        >>> stats = get_dataset_statistics(user)
        >>> print(f"Total datasets: {stats['total_datasets']}")
        >>> print(f"Total storage: {stats['total_storage_mb']:.2f} MB")
    """
    from equipment.models import DatasetHistory
    from django.db.models import Sum, Avg, Count
    
    datasets = DatasetHistory.objects.filter(user=user, is_active=True)
    
    aggregates = datasets.aggregate(
        total_datasets=Count('id'),
        total_storage=Sum('file_size'),
        avg_equipment_count=Avg('total_equipment_count'),
        avg_file_size=Avg('file_size'),
    )
    
    return {
        'total_datasets': aggregates['total_datasets'] or 0,
        'total_storage_bytes': aggregates['total_storage'] or 0,
        'total_storage_mb': (aggregates['total_storage'] or 0) / (1024 * 1024),
        'avg_equipment_per_dataset': aggregates['avg_equipment_count'] or 0,
        'avg_file_size_mb': (aggregates['avg_file_size'] or 0) / (1024 * 1024),
        'limit': MAX_DATASETS_PER_USER,
        'remaining_slots': max(0, MAX_DATASETS_PER_USER - (aggregates['total_datasets'] or 0))
    }
