# Generated by Django 5.0.6 on 2024-06-15 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Tracker', '0003_remove_supportquery_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SupportQuery',
        ),
    ]
