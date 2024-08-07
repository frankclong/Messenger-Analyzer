# Generated by Django 4.2.13 on 2024-06-23 22:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_handler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('folder_id', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ConversationMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.TextField()),
                ('content', models.TextField()),
                ('timestamp_ms', models.BigIntegerField()),
                ('sent_time', models.DateTimeField()),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_handler.contact')),
            ],
        ),
    ]
