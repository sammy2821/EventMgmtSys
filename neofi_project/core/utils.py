from .models import Event

def has_conflict(user, start, end, exclude_event_id=None):
    qs = Event.objects.filter(
        created_by=user,
        start_time__lt=end,
        end_time__gt=start,
    )
    if exclude_event_id:
        qs = qs.exclude(id=exclude_event_id)
    return qs.exists()
