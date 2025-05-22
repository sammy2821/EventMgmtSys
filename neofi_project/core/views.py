from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from .serializers import *
from .models import Event, EventPermission
from .utils import has_conflict
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        if has_conflict(self.request.user, serializer.validated_data['start_time'], serializer.validated_data['end_time']):
            raise ValidationError("Event conflicts with existing event.")
        event = serializer.save(created_by=self.request.user)
        EventPermission.objects.create(user=self.request.user, event=event, role='OWNER')
    

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)

    def perform_update(self, serializer):
        if has_conflict(self.request.user, serializer.validated_data['start_time'], serializer.validated_data['end_time'], self.get_object().id):
            raise ValidationError("Event conflicts with existing event.")
        serializer.save()

class EventBatchCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EventSerializer(data=request.data, many=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            for data in validated_data:
                if has_conflict(request.user, data['start_time'], data['end_time']):
                    return Response({'detail': 'One or more events conflict with existing ones.'}, status=400)
            Event.objects.bulk_create([Event(**data, created_by=request.user) for data in validated_data])
            return Response({'detail': 'Batch created successfully'}, status=201)
        return Response(serializer.errors, status=400)
    
class ShareEventView(generics.GenericAPIView):
    serializer_class = EventShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to share (must be owner)
        try:
            permission = EventPermission.objects.get(user=request.user, event=event)
            if permission.role != 'OWNER':
                return Response({"detail": "Only owners can share this event."}, status=status.HTTP_403_FORBIDDEN)
        except EventPermission.DoesNotExist:
            return Response({"detail": "You don't have access to this event."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'event': event})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "Event shared successfully."}, status=status.HTTP_200_OK)

class EventPermissionListView(generics.ListAPIView):
    serializer_class = EventPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event_id = self.kwargs['pk']
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return EventPermission.objects.none()

        # Only users with any role on the event can view permissions
        if not EventPermission.objects.filter(user=self.request.user, event=event).exists():
            return EventPermission.objects.none()

        return EventPermission.objects.filter(event=event)
    
class EventPermissionUpdateView(generics.UpdateAPIView):
    serializer_class = EventShareSerializer  # same as share
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        event_id = self.kwargs['pk']
        user_id = self.kwargs['user_id']

        event = get_object_or_404(Event, pk=event_id)

        # Only Owner can update roles
        if not EventPermission.objects.filter(user=self.request.user, event=event, role='OWNER').exists():
            raise ValidationError("Only owners can update permissions.")

        return get_object_or_404(EventPermission, user_id=user_id, event=event)

class EventPermissionDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        event_id = self.kwargs['pk']
        user_id = self.kwargs['user_id']

        event = get_object_or_404(Event, pk=event_id)

        # Only Owner can remove users
        if not EventPermission.objects.filter(user=self.request.user, event=event, role='OWNER').exists():
            raise ValidationError("Only owners can remove users.")

        return get_object_or_404(EventPermission, user_id=user_id, event=event)