from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .views import RegisterView, EventListCreateView, EventDetailView, EventBatchCreateView

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
    
]
