from datetime import datetime, timezone
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


class EventVersion(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    data = models.JSONField()
    created_at = models.DateTimeField(default=datetime.now())

    class Meta:
        unique_together = ('event', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"Version {self.version_number} of Event {self.event.title}"

    @classmethod
    def create_version(cls, event_instance, updated_at):
        last_version = cls.objects.filter(event=event_instance).order_by('-version_number').first()
        new_version_number = 1 if not last_version else last_version.version_number + 1

        snapshot = {
            'title': event_instance.title,
            'description': event_instance.description,
            'start_time': event_instance.start_time.isoformat(),
            'end_time': event_instance.end_time.isoformat(),
            'location': event_instance.location,
            'is_recurring': event_instance.is_recurring,
            'recurrence': event_instance.recurrence,
            'created_by_id': event_instance.created_by_id,
            'created_at': event_instance.created_at.isoformat(),
            'updated_at': updated_at.isoformat() if updated_at else datetime.now().isoformat(),
        }

        return cls.objects.create(
            event=event_instance,
            version_number=new_version_number,
            data=snapshot,
            created_at=datetime.now()
        )