# Generated by Django 5.1.2 on 2024-12-26 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0037_rename_csv_file_employee_pdf_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='first_appraiser',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='review_period',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='second_appraiser',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
