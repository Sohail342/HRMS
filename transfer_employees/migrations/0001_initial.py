# Generated by Django 5.1.2 on 2024-11-21 15:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pending_inquiry', models.BooleanField(default=False)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('transferred_status', models.CharField(choices=[('within_group', 'Transferred Within Group'), ('outside_group', 'Transferred Outside Group')], default='within_group', max_length=20)),
                ('admin_action', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=100)),
                ('action_taken_on', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
