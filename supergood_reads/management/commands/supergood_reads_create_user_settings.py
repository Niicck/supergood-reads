from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from supergood_reads.models import UserSettings


class Command(BaseCommand):
    help = "Create UserSettings for existing users"

    def handle(self, *args, **kwargs):
        user_model = get_user_model()

        user_ids_with_settings = UserSettings.objects.values_list("user_id", flat=True)
        users_without_settings = user_model.objects.exclude(
            id__in=user_ids_with_settings
        )

        new_user_settings = []
        for user in users_without_settings:
            new_user_settings.append(UserSettings(user=user))
        UserSettings.objects.bulk_create(new_user_settings)

        created_count = len(new_user_settings)
        self.stdout.write(
            self.style.SUCCESS(f"Total UserSettings created: {created_count}")
        )
