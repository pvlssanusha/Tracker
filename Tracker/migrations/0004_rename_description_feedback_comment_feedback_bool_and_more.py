# Generated by Django 5.0.6 on 2024-06-15 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tracker', '0003_remove_supportquery_user_hiring_support_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='description',
            new_name='comment',
        ),
        migrations.AddField(
            model_name='feedback',
            name='bool',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='feedback',
            name='options',
            field=models.CharField(choices=[('option1', 'option1'), ('option2', 'option2'), ('option3', 'option3')], default=1, max_length=100),
            preserve_default=False,
        ),
    ]
