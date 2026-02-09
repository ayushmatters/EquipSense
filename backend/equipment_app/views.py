"""
API Views for Chemical Equipment Visualizer

This module contains all API endpoints for the application.
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db import transaction

from .models import Dataset, Equipment
from .serializers import (
    UserRegistrationSerializer,
    DatasetSerializer,
    DatasetSummarySerializer,
    EquipmentSerializer
)
from .services.csv_parser import CSVParser, CSVParseError
from .services.analytics import AnalyticsService
from .services.pdf_generator import PDFReportGenerator
from .utils.history_manager import HistoryManager


# ==================== Authentication Views ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user.
    
    POST /api/auth/register
    Body: {username, email, password, password_confirm, first_name, last_name}
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and return JWT tokens.
    
    POST /api/auth/login
    Body: {username, password}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


# ==================== CSV Upload View ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    Upload and process CSV file containing equipment data.
    
    POST /api/upload
    Body: multipart/form-data with 'file' field
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    csv_file = request.FILES['file']
    
    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'File must be a CSV'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Parse CSV file
        df = CSVParser.parse_csv_file(csv_file)
        
        # Calculate statistics
        stats = AnalyticsService.calculate_summary_statistics(df)
        
        # Create dataset with transaction
        with transaction.atomic():
            # Create Dataset record
            dataset = Dataset.objects.create(
                filename=csv_file.name,
                uploaded_by=request.user,
                total_equipment=stats['total_equipment'],
                avg_flowrate=stats['avg_flowrate'],
                avg_pressure=stats['avg_pressure'],
                avg_temperature=stats['avg_temperature']
            )
            
            # Create Equipment records in bulk
            equipment_list = []
            for _, row in df.iterrows():
                equipment = Equipment(
                    dataset=dataset,
                    name=row['Equipment Name'],
                    type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                )
                equipment_list.append(equipment)
            
            Equipment.objects.bulk_create(equipment_list)
        
        # Cleanup old datasets (keep only last 5)
        HistoryManager.cleanup_old_datasets(request.user)
        
        # Serialize response
        serializer = DatasetSerializer(dataset)
        
        return Response({
            'message': 'File uploaded successfully',
            'dataset': serializer.data,
            'statistics': stats
        }, status=status.HTTP_201_CREATED)
        
    except CSVParseError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Summary View ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary(request):
    """
    Get summary statistics for the latest dataset.
    
    GET /api/summary
    Optional Query Params: dataset_id
    """
    dataset_id = request.query_params.get('dataset_id')
    
    try:
        if dataset_id:
            summary = AnalyticsService.get_dataset_summary(int(dataset_id))
        else:
            summary = AnalyticsService.get_latest_summary(request.user)
        
        return Response(summary, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== History View ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    """
    Get upload history for the current user.
    
    GET /api/history
    """
    try:
        datasets = HistoryManager.get_user_history(request.user)
        serializer = DatasetSummarySerializer(datasets, many=True)
        
        return Response({
            'count': len(serializer.data),
            'datasets': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== PDF Report View ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    Generate and download PDF report for a dataset.
    
    GET /api/report?dataset_id=<id>
    """
    dataset_id = request.query_params.get('dataset_id')
    
    if not dataset_id:
        return Response(
            {'error': 'dataset_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get dataset summary
        summary = AnalyticsService.get_dataset_summary(int(dataset_id))
        
        # Generate PDF
        pdf_generator = PDFReportGenerator()
        pdf_buffer = pdf_generator.generate_report(summary)
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        filename = f"equipment_report_{dataset_id}_{summary['dataset_info']['filename']}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Dataset Detail View ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dataset_detail(request, dataset_id):
    """
    Get detailed information about a specific dataset.
    
    GET /api/dataset/<id>
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id, uploaded_by=request.user)
        serializer = DatasetSerializer(dataset)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== Equipment Type Distribution View ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_type_distribution(request):
    """
    Get equipment type distribution for the latest dataset.
    
    GET /api/type-distribution
    Optional Query Params: dataset_id
    """
    dataset_id = request.query_params.get('dataset_id')
    
    try:
        if dataset_id:
            summary = AnalyticsService.get_dataset_summary(int(dataset_id))
        else:
            summary = AnalyticsService.get_latest_summary(request.user)
        
        return Response({
            'type_distribution': summary.get('type_distribution', {})
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
