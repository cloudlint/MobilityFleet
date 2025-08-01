# Generated by Django 5.2 on 2025-05-22 21:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_scooter_category'),
        ('service', '0003_jobcard_previous_scooter_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobcard',
            name='store',
            field=models.ForeignKey(blank=True, help_text='Store where the service is being performed', null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.store'),
        ),
    ]
