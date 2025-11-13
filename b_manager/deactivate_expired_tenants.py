from django.core.management.base import BaseCommand
from b_manager.models import Client
from datetime import date


class Command(BaseCommand):
    help = 'Deactivate tenants whose trial and paid period have expired'


def handle(self, *args, **options):
    today = date.today()
    count = 0
    for client in Client.objects.all():
        if not client.is_valid():
            if client.is_active:
                client.is_active = False
                client.save()
                count += 1
    self.stdout.write(self.style.SUCCESS(f'Deactivated {count} tenants'))