# Generated by Django 5.0.6 on 2024-06-15 09:52

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tracker', '0002_hiringrequest_supportquery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportquery',
            name='user',
        ),
        migrations.CreateModel(
            name='Hiring',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField()),
                ('options', models.CharField(choices=[('option1', 'option1'), ('option2', 'option2'), ('option3', 'option3')], max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pinned', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('query', 'Query'), ('feedback', 'Feedback'), ('technical_issue', 'Technical Issue')], max_length=20)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='HiringRequest',
        ),
        migrations.DeleteModel(
            name='SupportQuery',
        ),
    ]
