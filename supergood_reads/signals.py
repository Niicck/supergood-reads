from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from supergood_reads.models import UserSettings


@receiver(post_save, sender=get_user_model())
def create_user_settings(sender, instance, created, **kwargs):
    """Create UserSettings whenever a User is created."""
    if created:
        UserSettings.objects.create(user=instance)
