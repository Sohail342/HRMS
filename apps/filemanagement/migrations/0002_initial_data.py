from django.db import migrations

def create_initial_data(apps, schema_editor):
    # Get the models
    FileStatus = apps.get_model('filemanagement', 'FileStatus')
    FileType = apps.get_model('filemanagement', 'FileType')
    
    # Create file statuses
    statuses = [
        {'name': 'Pending', 'color_code': 'yellow-500', 'description': 'File is pending review or action'},
        {'name': 'Approved', 'color_code': 'green-500', 'description': 'File has been approved'},
        {'name': 'Rejected', 'color_code': 'red-500', 'description': 'File has been rejected'},
        {'name': 'Sent', 'color_code': 'blue-500', 'description': 'File has been sent to recipient'},
        {'name': 'Archived', 'color_code': 'gray-500', 'description': 'File has been archived'}
    ]
    
    for status_data in statuses:
        FileStatus.objects.create(**status_data)
    
    # Create file types
    file_types = [
        {'name': 'Document', 'allowed_extensions': '.doc,.docx,.pdf,.txt', 'description': 'Text documents and PDFs'},
        {'name': 'Image', 'allowed_extensions': '.jpg,.jpeg,.png,.gif', 'description': 'Image files'},
        {'name': 'Spreadsheet', 'allowed_extensions': '.xls,.xlsx,.csv', 'description': 'Excel and CSV files'},
        {'name': 'Presentation', 'allowed_extensions': '.ppt,.pptx', 'description': 'PowerPoint presentations'},
        {'name': 'Archive', 'allowed_extensions': '.zip,.rar,.7z', 'description': 'Compressed archive files'}
    ]
    
    for type_data in file_types:
        FileType.objects.create(**type_data)

class Migration(migrations.Migration):

    dependencies = [
        ('filemanagement', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]