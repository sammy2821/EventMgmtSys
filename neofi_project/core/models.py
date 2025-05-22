from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Event(models.Model):
    RECUR_CHOICES = [
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BI-WEEKLY', 'Bi-Weekly'),
        ('MONTHLY', 'Monthly'),
        ('BI-MONTHLY', 'Bi-Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('SEMI-ANNUALLY', 'Semi-Annually'),
        ('ANNUALLY', 'Annually'),
    ]

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=250, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence = models.CharField(max_length=15, choices=RECUR_CHOICES, default='NONE')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.start_time} - {self.created_by.username}"
    

class EventPermission(models.Model):
    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('EDITOR', 'Editor'),
        ('VIEWER', 'Viewer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_permissions')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='permissions')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title} - {self.role}"
