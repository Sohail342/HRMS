# Generated by Django 5.1.2 on 2024-11-20 16:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0013_alter_branch_branch_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='HRIS_App.region'),
        ),
        migrations.AlterField(
            model_name='branch',
            name='branch_code',
            field=models.IntegerField(unique=True),
        ),
    ]
