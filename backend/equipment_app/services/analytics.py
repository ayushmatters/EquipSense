"""
Analytics Service

This module provides data analytics calculations using Pandas.
"""

import pandas as pd
from typing import Dict, List
from ..models import Dataset, Equipment


class AnalyticsService:
    """
    Service class for generating analytics and statistics from equipment data.
    """
    
    @staticmethod
    def calculate_summary_statistics(df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics from equipment DataFrame.
        
        Args:
            df: Pandas DataFrame with equipment data
            
        Returns:
            Dictionary containing summary statistics
        """
        return {
            'total_equipment': len(df),
            'avg_flowrate': float(df['Flowrate'].mean()),
            'avg_pressure': float(df['Pressure'].mean()),
            'avg_temperature': float(df['Temperature'].mean()),
            'max_flowrate': float(df['Flowrate'].max()),
            'min_flowrate': float(df['Flowrate'].min()),
            'max_pressure': float(df['Pressure'].max()),
            'min_pressure': float(df['Pressure'].min()),
            'max_temperature': float(df['Temperature'].max()),
            'min_temperature': float(df['Temperature'].min()),
        }
    
    @staticmethod
    def get_equipment_type_distribution(df: pd.DataFrame) -> Dict[str, int]:
        """
        Get distribution of equipment by type.
        
        Args:
            df: Pandas DataFrame with equipment data
            
        Returns:
            Dictionary mapping equipment type to count
        """
        type_counts = df['Type'].value_counts().to_dict()
        return type_counts
    
    @staticmethod
    def get_dataset_summary(dataset_id: int) -> Dict:
        """
        Get comprehensive summary for a specific dataset.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dictionary containing dataset summary
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            equipments = Equipment.objects.filter(dataset=dataset)
            
            # Convert to DataFrame
            data = list(equipments.values('name', 'type', 'flowrate', 'pressure', 'temperature'))
            df = pd.DataFrame(data)
            df.columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            
            # Calculate statistics
            summary_stats = AnalyticsService.calculate_summary_statistics(df)
            type_distribution = AnalyticsService.get_equipment_type_distribution(df)
            
            return {
                'dataset_info': {
                    'id': dataset.id,
                    'filename': dataset.filename,
                    'uploaded_at': dataset.uploaded_at.isoformat(),
                    'uploaded_by': dataset.uploaded_by.username,
                },
                'statistics': summary_stats,
                'type_distribution': type_distribution,
                'equipment_list': df.to_dict('records')
            }
            
        except Dataset.DoesNotExist:
            raise ValueError(f"Dataset with ID {dataset_id} not found")
    
    @staticmethod
    def get_latest_summary(user) -> Dict:
        """
        Get summary for the most recent dataset uploaded by user.
        
        Args:
            user: Django User object
            
        Returns:
            Dictionary containing latest dataset summary
        """
        latest_dataset = Dataset.objects.filter(uploaded_by=user).first()
        
        if not latest_dataset:
            return {
                'error': 'No datasets found for this user',
                'statistics': {
                    'total_equipment': 0,
                    'avg_flowrate': 0,
                    'avg_pressure': 0,
                    'avg_temperature': 0,
                },
                'type_distribution': {},
                'equipment_list': []
            }
        
        return AnalyticsService.get_dataset_summary(latest_dataset.id)
    
    @staticmethod
    def calculate_parameter_averages(equipment_type: str = None) -> Dict:
        """
        Calculate average parameters, optionally filtered by equipment type.
        
        Args:
            equipment_type: Optional equipment type filter
            
        Returns:
            Dictionary with average values
        """
        queryset = Equipment.objects.all()
        
        if equipment_type:
            queryset = queryset.filter(type=equipment_type)
        
        data = list(queryset.values('flowrate', 'pressure', 'temperature'))
        
        if not data:
            return {
                'avg_flowrate': 0,
                'avg_pressure': 0,
                'avg_temperature': 0,
                'count': 0
            }
        
        df = pd.DataFrame(data)
        
        return {
            'avg_flowrate': float(df['flowrate'].mean()),
            'avg_pressure': float(df['pressure'].mean()),
            'avg_temperature': float(df['temperature'].mean()),
            'count': len(df)
        }
