# Generated by Django 5.1.2 on 2025-01-07 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee_attendance', '0011_remove_noninvolvementcertificate_employee_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractrenewal',
            old_name='renewal_date',
            new_name='Contract_expiry_date',
        ),
    ]
