# Generated by Django 4.2.3 on 2023-09-16 00:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("supergood_reads", "0002_create_user_settings"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ebertstrategy",
            old_name="great_film",
            new_name="goat",
        ),
    ]