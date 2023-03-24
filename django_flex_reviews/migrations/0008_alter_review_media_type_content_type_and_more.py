# Generated by Django 4.1.7 on 2023-03-24 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        (
            "django_flex_reviews",
            "0007_book_created_at_book_updated_at_film_created_at_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="media_type_content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="media_type_review_set",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="strategy_content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="strategy_review_set",
                to="contenttypes.contenttype",
            ),
        ),
    ]
