"""
CSV Processor Module

Handles CSV file upload, parsing, validation, and data extraction
for the native analytics module.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os


class CSVProcessor:
    """
    Processes CSV files for analytics visualization.
    
    Features:
    - CSV file validation
    - Data parsing with Pandas
    - Statistical analysis
    - Data extraction for charts
    """
    
    def __init__(self):
        self.df = None
        self.file_path = None
        self.column_names = []
        self.numeric_columns = []
        
    def load_csv(self, file_path: str) -> Tuple[bool, str]:
        """
        Load and validate CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return False, "File not found"
            
            # Validate file extension
            if not file_path.lower().endswith('.csv'):
                return False, "File must be a CSV file"
            
            # Load CSV
            self.df = pd.read_csv(file_path)
            self.file_path = file_path
            
            # Validate not empty
            if self.df.empty:
                return False, "CSV file is empty"
            
            # Extract column information
            self.column_names = list(self.df.columns)
            self.numeric_columns = list(self.df.select_dtypes(include=[np.number]).columns)
            
            if len(self.numeric_columns) == 0:
                return False, "No numeric columns found for analysis"
            
            return True, f"Successfully loaded {len(self.df)} rows with {len(self.column_names)} columns"
            
        except pd.errors.EmptyDataError:
            return False, "CSV file is empty or invalid"
        except pd.errors.ParserError as e:
            return False, f"Error parsing CSV: {str(e)}"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    def get_summary_statistics(self) -> Dict[str, any]:
        """
        Generate summary statistics for the dataset.
        
        Returns:
            Dictionary containing statistical summary
        """
        if self.df is None:
            return {}
        
        try:
            stats = {
                'total_rows': len(self.df),
                'total_columns': len(self.column_names),
                'numeric_columns': len(self.numeric_columns),
                'missing_values': int(self.df.isnull().sum().sum()),
                'column_stats': {}
            }
            
            # Get statistics for each numeric column
            for col in self.numeric_columns:
                col_stats = {
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median()),
                    'std': float(self.df[col].std()),
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'count': int(self.df[col].count()),
                    'missing': int(self.df[col].isnull().sum())
                }
                stats['column_stats'][col] = col_stats
            
            return stats
            
        except Exception as e:
            print(f"Error generating statistics: {e}")
            return {}
    
    def get_column_data(self, column_name: str) -> Optional[List]:
        """
        Get data for a specific column.
        
        Args:
            column_name: Name of the column
            
        Returns:
            List of column values or None if error
        """
        if self.df is None or column_name not in self.column_names:
            return None
        
        try:
            return self.df[column_name].tolist()
        except Exception as e:
            print(f"Error getting column data: {e}")
            return None
    
    def get_numeric_columns_data(self) -> Dict[str, List]:
        """
        Get all numeric columns data for charts.
        
        Returns:
            Dictionary mapping column names to their data
        """
        if self.df is None:
            return {}
        
        result = {}
        for col in self.numeric_columns:
            try:
                # Remove NaN values
                data = self.df[col].dropna().tolist()
                result[col] = data
            except Exception as e:
                print(f"Error getting data for column {col}: {e}")
        
        return result
    
    def get_top_n_rows(self, n: int = 10) -> Optional[pd.DataFrame]:
        """
        Get top N rows of the dataset.
        
        Args:
            n: Number of rows to return
            
        Returns:
            DataFrame with top N rows or None
        """
        if self.df is None:
            return None
        
        return self.df.head(n)
    
    def get_correlation_matrix(self) -> Optional[pd.DataFrame]:
        """
        Calculate correlation matrix for numeric columns.
        
        Returns:
            Correlation matrix DataFrame or None
        """
        if self.df is None or len(self.numeric_columns) == 0:
            return None
        
        try:
            return self.df[self.numeric_columns].corr()
        except Exception as e:
            print(f"Error calculating correlation: {e}")
            return None
    
    def get_dataset_info(self) -> Dict[str, any]:
        """
        Get basic information about the loaded dataset.
        
        Returns:
            Dictionary with dataset information
        """
        if self.df is None:
            return {}
        
        return {
            'file_path': self.file_path,
            'file_name': os.path.basename(self.file_path) if self.file_path else 'Unknown',
            'rows': len(self.df),
            'columns': len(self.column_names),
            'column_names': self.column_names,
            'numeric_columns': self.numeric_columns,
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }
    
    def filter_data(self, column: str, min_val: float = None, max_val: float = None) -> bool:
        """
        Filter dataset based on column value range.
        
        Args:
            column: Column name to filter
            min_val: Minimum value (optional)
            max_val: Maximum value (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if self.df is None or column not in self.numeric_columns:
            return False
        
        try:
            mask = pd.Series([True] * len(self.df))
            
            if min_val is not None:
                mask &= self.df[column] >= min_val
            
            if max_val is not None:
                mask &= self.df[column] <= max_val
            
            self.df = self.df[mask]
            return True
            
        except Exception as e:
            print(f"Error filtering data: {e}")
            return False
    
    def reset_data(self):
        """Reset loaded data and clear cache."""
        self.df = None
        self.file_path = None
        self.column_names = []
        self.numeric_columns = []
