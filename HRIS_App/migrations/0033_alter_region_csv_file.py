# Generated by Django 5.1.2 on 2024-12-13 15:27

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0032_region_csv_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='csv_file',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='csv_file'),
        ),
    ]
