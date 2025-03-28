# Generated by Django 5.1.2 on 2025-01-06 20:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee_attendance', '0009_educationaldocument_nicrequest_stationaryrequest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NonInvolvementCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_name', models.CharField(max_length=100)),
                ('request_date', models.DateField()),
                ('reason', models.TextField()),
                ('supporting_docs', models.FileField(blank=True, null=True, upload_to='non_involvement_certificates/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='non_involvement_certificates', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='NICRequest',
        ),
    ]
