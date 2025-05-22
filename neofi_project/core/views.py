from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, EventSerializer
from .models import Event
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
        serializer.save(created_by=self.request.user)

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