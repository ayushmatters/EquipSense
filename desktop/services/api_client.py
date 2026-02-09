"""
API Client for Desktop Application

Handles all HTTP requests to the Django backend API.
"""

import requests
import json


class APIClient:
    """Client for interacting with the Django REST API"""
    
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.token = None
        self.user = None
    
    def set_token(self, token):
        """Set authentication token"""
        self.token = token
    
    def get_headers(self):
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def login(self, username, password):
        """
        Login user and store token
        
        Args:
            username: Username
            password: Password
            
        Returns:
            dict: Response data with user info and tokens
        """
        url = f"{self.base_url}/auth/login"
        data = {
            'username': username,
            'password': password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result['tokens']['access']
        self.user = result['user']
        
        return result
    
    def register(self, username, email, password, password_confirm, first_name='', last_name=''):
        """
        Register new user
        
        Args:
            username: Username
            email: Email address
            password: Password
            password_confirm: Password confirmation
            first_name: First name (optional)
            last_name: Last name (optional)
            
        Returns:
            dict: Response data with user info and tokens
        """
        url = f"{self.base_url}/auth/register"
        data = {
            'username': username,
            'email': email,
            'password': password,
            'password_confirm': password_confirm,
            'first_name': first_name,
            'last_name': last_name
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result['tokens']['access']
        self.user = result['user']
        
        return result
    
    def upload_csv(self, file_path):
        """
        Upload CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            dict: Response data with dataset info and statistics
        """
        url = f"{self.base_url}/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
            
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
        
        return response.json()
    
    def get_summary(self, dataset_id=None):
        """
        Get summary statistics
        
        Args:
            dataset_id: Optional dataset ID
            
        Returns:
            dict: Summary data with statistics and equipment list
        """
        url = f"{self.base_url}/summary"
        if dataset_id:
            url += f"?dataset_id={dataset_id}"
        
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_history(self):
        """
        Get upload history
        
        Returns:
            dict: History data with dataset list
        """
        url = f"{self.base_url}/history"
        
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def get_type_distribution(self, dataset_id=None):
        """
        Get equipment type distribution
        
        Args:
            dataset_id: Optional dataset ID
            
        Returns:
            dict: Type distribution data
        """
        url = f"{self.base_url}/type-distribution"
        if dataset_id:
            url += f"?dataset_id={dataset_id}"
        
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        
        return response.json()
    
    def download_report(self, dataset_id, save_path):
        """
        Download PDF report
        
        Args:
            dataset_id: Dataset ID
            save_path: Path to save PDF file
        """
        url = f"{self.base_url}/report?dataset_id={dataset_id}"
        
        response = requests.get(url, headers=self.get_headers(), stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
