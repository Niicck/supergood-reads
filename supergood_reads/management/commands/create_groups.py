from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set up default groups and permissions"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        # Create Reviewer group
        group, created = Group.objects.get_or_create(name="supergood_reads.Reviewer")

        # Assign permissions to Reviewer group
        permission = Permission.objects.get(
            codename="add_review", content_type__app_label="supergood_reads"
        )
        group.permissions.add(permission)
