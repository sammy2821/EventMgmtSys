from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .views import *

urlpatterns = [
    
    # AUTH
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # EVENTS
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>', EventDetailView.as_view(), name='event-detail'),
    path('events/batch', EventBatchCreateView.as_view(), name='event-batch-create'),
    path('events/<int:pk>/share/', ShareEventView.as_view(), name='share-event'),
    
    # PERMISSIONS
    path('events/<int:pk>/share/', ShareEventView.as_view(), name='share-event'),
    path('events/<int:pk>/permissions/', EventPermissionListView.as_view(), name='list-permissions'),
    path('events/<int:pk>/permissions/<int:user_id>/', EventPermissionUpdateView.as_view(), name='update-permission'),
    path('events/<int:pk>/permissions/<int:user_id>/', EventPermissionDeleteView.as_view(), name='remove-permission'),
]
