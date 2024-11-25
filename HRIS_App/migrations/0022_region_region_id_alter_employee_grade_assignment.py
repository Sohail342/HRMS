# Generated by Django 5.1.2 on 2024-11-25 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HRIS_App', '0021_employee_grade_assignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='region_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='grade_assignment',
            field=models.CharField(blank=True, choices=[('A - Excellent', 'A - Excellent'), ('B - Very Good', 'B - Very Good'), ('C - Good', 'C - Good'), ('D - Needs Improvement', 'D - Needs Improvement'), ('E - Unsatisfactory', 'E - Unsatisfactory')], max_length=100, null=True),
        ),
    ]
