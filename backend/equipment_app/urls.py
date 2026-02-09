"""
URL Configuration for Equipment App

This module defines all API endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register', views.register_user, name='register'),
    path('auth/login', views.login_user, name='login'),
    
    # Dataset operations
    path('upload', views.upload_csv, name='upload-csv'),
    path('summary', views.get_summary, name='get-summary'),
    path('history', views.get_history, name='get-history'),
    path('report', views.generate_report, name='generate-report'),
    
    # Dataset detail
    path('dataset/<int:dataset_id>', views.get_dataset_detail, name='dataset-detail'),
    
    # Analytics
    path('type-distribution', views.get_type_distribution, name='type-distribution'),
]
