# Generated by Django 5.1.2 on 2024-11-22 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0018_alter_employee_transferred_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='branch',
            options={'verbose_name': 'Branch', 'verbose_name_plural': ' Branches'},
        ),
        migrations.AlterModelOptions(
            name='division',
            options={'verbose_name': 'Division', 'verbose_name_plural': ' Division'},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'verbose_name': 'Employee', 'verbose_name_plural': ' Employees'},
        ),
        migrations.AlterModelOptions(
            name='employeegrade',
            options={'verbose_name': 'Employee Grade', 'verbose_name_plural': ' Employee Grades'},
        ),
        migrations.AlterModelOptions(
            name='employeetype',
            options={'verbose_name': 'Employee Type', 'verbose_name_plural': ' Employee Types'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Group', 'verbose_name_plural': '  Groups'},
        ),
        migrations.AlterModelOptions(
            name='region',
            options={'verbose_name': 'Region', 'verbose_name_plural': '  Regions'},
        ),
        migrations.AddField(
            model_name='employee',
            name='transfer_remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]