"""
CSV Parser Service

This module handles CSV file parsing and validation using Pandas.
"""

import pandas as pd
from typing import Dict, List, Tuple
from io import StringIO


class CSVParseError(Exception):
    """Custom exception for CSV parsing errors"""
    pass


class CSVParser:
    """
    Service class for parsing and validating equipment CSV files.
    """
    
    REQUIRED_COLUMNS = [
        'Equipment Name',
        'Type',
        'Flowrate',
        'Pressure',
        'Temperature'
    ]
    
    @staticmethod
    def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate if CSV has required columns and proper data types.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required columns
        missing_columns = set(CSVParser.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Check if dataframe is empty
        if df.empty:
            return False, "CSV file is empty"
        
        # Validate numeric columns
        numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
        for col in numeric_columns:
            try:
                pd.to_numeric(df[col], errors='raise')
            except (ValueError, TypeError):
                return False, f"Column '{col}' must contain numeric values"
        
        return True, ""
    
    @staticmethod
    def parse_csv_file(file) -> pd.DataFrame:
        """
        Parse uploaded CSV file into Pandas DataFrame.
        
        Args:
            file: Uploaded file object from Django request
            
        Returns:
            Pandas DataFrame with parsed data
            
        Raises:
            CSVParseError: If file cannot be parsed or validation fails
        """
        try:
            # Read CSV file
            content = file.read().decode('utf-8')
            df = pd.read_csv(StringIO(content))
            
            # Validate structure
            is_valid, error_message = CSVParser.validate_csv_structure(df)
            if not is_valid:
                raise CSVParseError(error_message)
            
            # Clean data
            df = df.dropna()  # Remove rows with missing values
            
            # Convert numeric columns to float
            df['Flowrate'] = pd.to_numeric(df['Flowrate'])
            df['Pressure'] = pd.to_numeric(df['Pressure'])
            df['Temperature'] = pd.to_numeric(df['Temperature'])
            
            # Strip whitespace from string columns
            df['Equipment Name'] = df['Equipment Name'].astype(str).str.strip()
            df['Type'] = df['Type'].astype(str).str.strip()
            
            return df
            
        except UnicodeDecodeError:
            raise CSVParseError("Invalid file encoding. Please upload a valid CSV file.")
        except pd.errors.EmptyDataError:
            raise CSVParseError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise CSVParseError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            raise CSVParseError(f"Unexpected error parsing CSV: {str(e)}")
    
    @staticmethod
    def dataframe_to_dict_list(df: pd.DataFrame) -> List[Dict]:
        """
        Convert DataFrame to list of dictionaries for API response.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of dictionaries
        """
        return df.to_dict('records')
