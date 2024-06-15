# Generated by Django 5.0.6 on 2024-06-15 09:53

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tracker', '0004_delete_supportquery'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportQuery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('query', 'Query'), ('feedback', 'Feedback'), ('technical_issue', 'Technical Issue')], max_length=20)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
