from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    header = 'Create default roles'

    def handle(self, *args, **kwargs):
        roles = ['Owner', 'Editor', 'Viewer']
        for role in roles:
            Group.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS('Default roles created.'))
