# Generated by Django 5.1.2 on 2024-11-19 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0004_rename_name_division_division_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='date_of_retirement',
            new_name='date_of_joining',
        ),
    ]