"""
Django REST Framework Serializers

This module handles serialization/deserialization of model instances.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, Equipment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        """Validate password confirmation"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data
    
    def create(self, validated_data):
        """Create new user with encrypted password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model"""
    
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'type', 'flowrate', 'pressure', 'temperature']
        read_only_fields = ['id']


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model with equipment details"""
    equipments = EquipmentSerializer(many=True, read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'uploaded_by', 'uploaded_at',
            'total_equipment', 'avg_flowrate', 'avg_pressure', 
            'avg_temperature', 'equipments', 'equipment_count'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def get_equipment_count(self, obj):
        """Get count of equipment in dataset"""
        return obj.equipments.count()


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset listing"""
    uploaded_by = serializers.StringRelatedField()
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'filename', 'uploaded_by', 'uploaded_at',
            'equipment_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature'
        ]
        read_only_fields = fields
    
    def get_equipment_count(self, obj):
        """Get count of equipment in dataset"""
        return obj.equipments.count()
