# Generated by Django 5.1.2 on 2025-01-31 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_attendance', '0022_leaveapplication_leave_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplication',
            name='backup_employee1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='leaveapplication',
            name='backup_employee2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
