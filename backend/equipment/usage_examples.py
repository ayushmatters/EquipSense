"""
Example Usage Scripts for Equipment Dataset History Management

This module demonstrates practical usage of the DatasetHistory model
and history management services.

Run examples:
    python manage.py shell < equipment/examples/usage_examples.py

Author: Senior Django Backend Architect
Date: February 6, 2026
"""

# ============================================================
# EXAMPLE 1: Create Dataset with Auto-History Management
# ============================================================

def example_create_dataset_with_history():
    """
    Demonstrate creating a dataset and automatically managing history.
    """
    from django.contrib.auth.models import User
    from equipment.models import DatasetHistory
    from equipment.services.history_manager import limit_dataset_history
    from django.core.files.base import ContentFile
    import json
    
    print("\n" + "="*60)
    print("EXAMPLE 1: Create Dataset with Auto-History Management")
    print("="*60 + "\n")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='engineer_john',
        defaults={
            'email': 'john@chemicalplant.com',
            'first_name': 'John',
            'last_name': 'Engineer'
        }
    )
    
    if created:
        user.set_password('secure_password_123')
        user.save()
        print(f"✓ Created user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # Simulate CSV file content
    csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,45.5,120.3,25.7
Valve-002,Valve,32.1,98.2,22.5
Reactor-003,Reactor,67.8,145.0,30.2
Heat Exchanger-004,Heat Exchanger,54.3,110.5,28.9
Pump-005,Pump,49.2,125.8,26.4
"""
    
    # Create dataset
    dataset = DatasetHistory(
        user=user,
        dataset_name='Plant Equipment Survey 2024-Q1',
        total_equipment_count=5,
        avg_flowrate=49.78,
        avg_pressure=119.96,
        avg_temperature=26.74,
        type_distribution={
            'Pump': 2,
            'Valve': 1,
            'Reactor': 1,
            'Heat Exchanger': 1
        },
        file_size=len(csv_content.encode('utf-8')),
        is_active=True
    )
    
    # Create a mock file
    dataset.file.save('plant_survey_q1.csv', ContentFile(csv_content.encode('utf-8')))
    dataset.save()
    
    print(f"✓ Created dataset: {dataset.dataset_name}")
    print(f"  - ID: {dataset.id}")
    print(f"  - Equipment Count: {dataset.total_equipment_count}")
    print(f"  - File Size: {dataset.get_file_size_display()}")
    print(f"  - Uploaded: {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Apply history limit (keep only last 5)
    print("\n📊 Applying history limit (max 5 datasets)...")
    result = limit_dataset_history(user, max_datasets=5)
    
    print(f"  - Deleted: {result['deleted_count']} old dataset(s)")
    print(f"  - Remaining: {result['remaining_count']} dataset(s)")
    print(f"  - Status: {result['message']}")
    
    return dataset


# ============================================================
# EXAMPLE 2: Query and Display Dataset Analytics
# ============================================================

def example_query_analytics():
    """
    Demonstrate querying dataset analytics and statistics.
    """
    from equipment.models import DatasetHistory
    from equipment.services.history_manager import get_dataset_statistics
    from django.contrib.auth.models import User
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Query Dataset Analytics")
    print("="*60 + "\n")
    
    # Get user
    try:
        user = User.objects.get(username='engineer_john')
    except User.DoesNotExist:
        print("❌ User not found. Run Example 1 first.")
        return
    
    # Get user statistics
    print(f"📈 Statistics for {user.username}:")
    stats = get_dataset_statistics(user)
    
    print(f"  Total Datasets: {stats['total_datasets']}")
    print(f"  Total Storage: {stats['total_storage_mb']:.2f} MB")
    print(f"  Avg Equipment/Dataset: {stats['avg_equipment_per_dataset']:.0f}")
    print(f"  Avg File Size: {stats['avg_file_size_mb']:.2f} MB")
    print(f"  Remaining Slots: {stats['remaining_slots']}/{stats['limit']}")
    
    # List all datasets
    print(f"\n📋 User's Datasets:")
    datasets = DatasetHistory.objects.filter(user=user, is_active=True).order_by('-uploaded_at')
    
    for i, ds in enumerate(datasets, 1):
        print(f"\n  {i}. {ds.dataset_name}")
        print(f"     - Equipment: {ds.total_equipment_count} units")
        print(f"     - Avg Flowrate: {ds.avg_flowrate:.2f}")
        print(f"     - Avg Pressure: {ds.avg_pressure:.2f}")
        print(f"     - Avg Temperature: {ds.avg_temperature:.2f}°C")
        print(f"     - Type Distribution: {ds.get_type_distribution_display()}")
        print(f"     - Uploaded: {ds.age_in_days} days ago")


# ============================================================
# EXAMPLE 3: Bulk Dataset Creation (Simulate Multiple Uploads)
# ============================================================

def example_bulk_dataset_creation():
    """
    Simulate uploading multiple datasets to test history limit.
    """
    from django.contrib.auth.models import User
    from equipment.models import DatasetHistory
    from equipment.services.history_manager import limit_dataset_history
    from django.core.files.base import ContentFile
    from datetime import timedelta
    from django.utils import timezone
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Bulk Dataset Creation (Test History Limit)")
    print("="*60 + "\n")
    
    user = User.objects.get(username='engineer_john')
    
    print(f"Creating 8 datasets for {user.username}...")
    print("(This should trigger automatic cleanup, keeping only last 5)\n")
    
    # Create 8 datasets
    for i in range(1, 9):
        csv_content = f"Equipment Name,Type,Flowrate,Pressure,Temperature\nTest-{i},Pump,50.0,100.0,25.0\n"
        
        dataset = DatasetHistory(
            user=user,
            dataset_name=f'Dataset-{i:02d}-2024',
            total_equipment_count=10 * i,
            avg_flowrate=45.0 + i,
            avg_pressure=100.0 + i * 5,
            avg_temperature=25.0 + i * 0.5,
            type_distribution={'Pump': 10 * i},
            file_size=len(csv_content.encode('utf-8')),
            is_active=True
        )
        
        dataset.file.save(f'dataset_{i:02d}.csv', ContentFile(csv_content.encode('utf-8')))
        dataset.save()
        
        # Simulate different upload times
        dataset.uploaded_at = timezone.now() - timedelta(days=8-i)
        dataset.save(update_fields=['uploaded_at'])
        
        print(f"  ✓ Created: {dataset.dataset_name} (uploaded {dataset.age_in_days} days ago)")
        
        # Apply history limit after each upload
        if i >= 5:
            result = limit_dataset_history(user, max_datasets=5)
            if result['deleted_count'] > 0:
                print(f"    → Cleaned up {result['deleted_count']} old dataset(s)")
    
    # Final count
    final_count = DatasetHistory.objects.filter(user=user, is_active=True).count()
    print(f"\n✅ Final count: {final_count} active datasets (should be 5)")


# ============================================================
# EXAMPLE 4: Archive Old Datasets
# ============================================================

def example_archive_datasets():
    """
    Demonstrate archiving datasets older than a threshold.
    """
    from django.contrib.auth.models import User
    from equipment.services.history_manager import archive_old_datasets
    
    print("\n" + "="*60)
    print("EXAMPLE 4: Archive Old Datasets")
    print("="*60 + "\n")
    
    user = User.objects.get(username='engineer_john')
    
    # Archive datasets older than 7 days
    print(f"Archiving datasets older than 7 days for {user.username}...")
    result = archive_old_datasets(user, days_threshold=7)
    
    print(f"  - Archived: {result['archived_count']} dataset(s)")
    print(f"  - Status: {result['message']}")
    
    if result['archived_ids']:
        print(f"  - Archived IDs: {result['archived_ids']}")


# ============================================================
# EXAMPLE 5: Admin-Style Dataset Report
# ============================================================

def example_admin_report():
    """
    Generate an admin-style report of all datasets.
    """
    from equipment.models import DatasetHistory
    from django.db.models import Count, Sum, Avg
    
    print("\n" + "="*60)
    print("EXAMPLE 5: Admin Dataset Report")
    print("="*60 + "\n")
    
    # Overall statistics
    overall_stats = DatasetHistory.objects.aggregate(
        total_datasets=Count('id'),
        total_storage=Sum('file_size'),
        avg_equipment=Avg('total_equipment_count'),
        total_equipment=Sum('total_equipment_count')
    )
    
    print("📊 System-Wide Statistics:")
    print(f"  Total Datasets: {overall_stats['total_datasets']}")
    print(f"  Total Storage: {(overall_stats['total_storage'] or 0) / 1024 / 1024:.2f} MB")
    print(f"  Total Equipment Records: {overall_stats['total_equipment'] or 0}")
    print(f"  Avg Equipment/Dataset: {overall_stats['avg_equipment'] or 0:.1f}")
    
    # Per-user statistics
    print("\n👥 Per-User Breakdown:")
    user_stats = DatasetHistory.objects.values(
        'user__username', 'user__email'
    ).annotate(
        dataset_count=Count('id'),
        total_storage=Sum('file_size'),
        total_equipment=Sum('total_equipment_count')
    ).order_by('-dataset_count')
    
    for stat in user_stats:
        print(f"\n  User: {stat['user__username']} ({stat['user__email']})")
        print(f"    - Datasets: {stat['dataset_count']}")
        print(f"    - Storage: {stat['total_storage'] / 1024:.2f} KB")
        print(f"    - Equipment: {stat['total_equipment']} records")
    
    # Recent uploads
    print("\n📅 Recent Uploads (Last 5):")
    recent = DatasetHistory.objects.select_related('user').order_by('-uploaded_at')[:5]
    
    for ds in recent:
        print(f"\n  {ds.dataset_name}")
        print(f"    User: {ds.user.username}")
        print(f"    Date: {ds.uploaded_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Status: {'Active' if ds.is_active else 'Archived'}")
        print(f"    Equipment: {ds.total_equipment_count}")


# ============================================================
# MAIN EXECUTION
# ============================================================

def run_all_examples():
    """
    Run all example functions in sequence.
    """
    print("\n" + "="*70)
    print(" 🚀 Chemical Equipment Parameter Visualizer - Usage Examples")
    print("="*70)
    
    try:
        # Example 1: Create dataset
        dataset = example_create_dataset_with_history()
        
        # Example 2: Query analytics
        example_query_analytics()
        
        # Example 3: Bulk creation
        example_bulk_dataset_creation()
        
        # Example 4: Archive old datasets
        example_archive_datasets()
        
        # Example 5: Admin report
        example_admin_report()
        
        print("\n" + "="*70)
        print(" ✅ All examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# QUICK TEST FUNCTION
# ============================================================

def quick_test():
    """
    Quick test to verify everything is working.
    """
    from django.contrib.auth.models import User
    from equipment.models import DatasetHistory
    from equipment.services.history_manager import limit_dataset_history, get_dataset_statistics
    
    print("\n🧪 Quick System Test\n")
    
    # Test 1: Model import
    print("✓ DatasetHistory model imported")
    
    # Test 2: Service functions
    print("✓ History manager services imported")
    
    # Test 3: Create test user if needed
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    print(f"✓ Test user: {user.username}")
    
    # Test 4: Get statistics
    stats = get_dataset_statistics(user)
    print(f"✓ User has {stats['total_datasets']} dataset(s)")
    
    # Test 5: Query datasets
    count = DatasetHistory.objects.filter(user=user).count()
    print(f"✓ Database query successful: {count} total datasets")
    
    print("\n✅ All systems operational!\n")


# Run when imported in Django shell
if __name__ == '__main__':
    print("Run this in Django shell:")
    print("  python manage.py shell")
    print("  >>> exec(open('equipment/examples/usage_examples.py').read())")
    print("  >>> run_all_examples()")
else:
    # Auto-run quick test when imported
    quick_test()
