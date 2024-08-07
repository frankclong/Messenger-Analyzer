# Generated by Django 4.2.13 on 2024-07-28 02:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_handler', '0004_contact_user_conversationmessage_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='folder_id',
            field=models.TextField(),
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together={('user', 'folder_id')},
        ),
        migrations.AlterUniqueTogether(
            name='conversationmessage',
            unique_together={('user', 'contact', 'content', 'sender_name', 'timestamp_ms')},
        ),
    ]
