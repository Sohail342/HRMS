# Generated by Django 5.1.2 on 2024-11-19 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0003_alter_employee_options_employee_admin_signuture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='division',
            old_name='name',
            new_name='division_name',
        ),
    ]
