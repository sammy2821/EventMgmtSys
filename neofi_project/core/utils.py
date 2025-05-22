from .models import *

def has_conflict(user, start, end, exclude_event_id=None):
    qs = Event.objects.filter(
        created_by=user,
        start_time__lt=end,
        end_time__gt=start,
    )
    if exclude_event_id:
        qs = qs.exclude(id=exclude_event_id)
    return qs.exists()

def has_event_permission(user, event, required_roles):
    if not user.is_authenticated:
        return False

    # Owner has all permissions by default
    try:
        perm = EventPermission.objects.get(user=user, event=event)
        return perm.role in required_roles
    except EventPermission.DoesNotExist:
        return False

def compute_diff(data1, data2):
    diff = {}
    all_keys = set(data1.keys()) | set(data2.keys())
    for key in all_keys:
        val1 = data1.get(key)
        val2 = data2.get(key)
        if val1 != val2:
            diff[key] = {"old": val1, "new": val2}
    return diff
