from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import serializers
from .models import *

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
            
class EventShareSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=EventPermission.ROLE_CHOICES)

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise ValidationError("User with this ID does not exist.")
        return value

    def create(self, validated_data):
        event = self.context['event']
        user = User.objects.get(id=validated_data['user_id'])

        permission, created = EventPermission.objects.update_or_create(
            user=user,
            event=event,
            defaults={'role': validated_data['role']}
        )
        return permission
    
class EventPermissionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EventPermission
        fields = ['user_id', 'username', 'role']
    
class EventVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVersion
        fields = ['id', 'version_number', 'data', 'created_at']


class EventRollbackSerializer(serializers.Serializer):
    version_id = serializers.IntegerField()

    def validate_version_id(self, value):
        event = self.context.get('event')
        if not EventVersion.objects.filter(event=event, id=value).exists():
            raise serializers.ValidationError("Version does not exist for this event.")
        return value