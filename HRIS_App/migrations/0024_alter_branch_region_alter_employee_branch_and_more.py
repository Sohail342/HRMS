# Generated by Django 5.1.2 on 2024-11-25 20:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0023_remove_branch_branch_region_branch_region_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='HRIS_App.region', to_field='name'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='HRIS_App.branch', to_field='branch_code'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='HRIS_App.region', to_field='name'),
        ),
    ]