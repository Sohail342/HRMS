from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from cloudinary.uploader import upload, destroy

from .models import EmployeeFile, FileStatus, FileType
from apps.HRIS_App.models import Employee, Branch, Region, Division
from .forms import EmployeeFileForm, FileFilterForm

# Helper functions
def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def file_management_dashboard(request):
    """Main file management dashboard view"""
    try:
        # Initialize filter form
        filter_form = FileFilterForm(request.GET or None)
        
        # Base queryset with optimized joins
        files_queryset = EmployeeFile.objects.select_related(
            'employee', 'employee__designation', 'employee__branch', 
            'employee__region', 'employee__division', 'file_type', 'file_status'
        )
        
        # Apply filters if form is valid
        if filter_form.is_valid():
            filters = {}
            data = filter_form.cleaned_data
            
            # Employee filters
            if data.get('employee_name'):
                files_queryset = files_queryset.filter(employee__name__icontains=data['employee_name'])
            
            if data.get('employee_id'):
                files_queryset = files_queryset.filter(employee__SAP_ID=data['employee_id'])
            
            if data.get('designation'):
                files_queryset = files_queryset.filter(employee__designation=data['designation'])
            
            if data.get('department'):
                files_queryset = files_queryset.filter(employee__division=data['department'])
                
            if data.get('division'):
                files_queryset = files_queryset.filter(employee__division=data['division'])
            
            if data.get('branch_name'):
                files_queryset = files_queryset.filter(employee__branch=data['branch_name'])
            
            if data.get('region'):
                files_queryset = files_queryset.filter(employee__region=data['region'])
            
            if data.get('employment_type'):
                files_queryset = files_queryset.filter(employee__employee_type=data['employment_type'])
            
            # File filters
            if data.get('file_status'):
                files_queryset = files_queryset.filter(file_status=data['file_status'])
            
            if data.get('upload_date_start') and data.get('upload_date_end'):
                files_queryset = files_queryset.filter(
                    upload_timestamp__gte=data['upload_date_start'],
                    upload_timestamp__lte=data['upload_date_end']
                )
        
        # Pagination
        paginator = Paginator(files_queryset.order_by('-upload_timestamp'), 20)
        page = request.GET.get('page', 1)
        
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)
        
        # Context data
        context = {
            'files': files,
            'filter_form': filter_form,
            'file_statuses': FileStatus.objects.filter(is_active=True),
            'file_types': FileType.objects.filter(is_active=True),
        }
        
        return render(request, 'filemanagement/dashboard.html', context)
    except Exception as e:
        return render(request, 'filemanagement/error.html', {
            'error_title': 'Dashboard Error',
            'error_message': 'There was a problem loading the file management dashboard.',
            'error_details': str(e),
            'back_url': reverse('filemanagement:dashboard'),
            'back_text': 'Try Again'
        })

@login_required
@user_passes_test(is_admin)
def upload_file(request):
    """View for uploading new files"""
    try:
        if request.method == 'POST':
            form = EmployeeFileForm(request.POST, request.FILES)
            if form.is_valid():
                file_instance = form.save(commit=False)
                file_instance.created_by = request.user
                
                # Handle file upload to Cloudinary if file is provided
                if 'file' in request.FILES:
                    uploaded_file = request.FILES['file']
                    result = upload(uploaded_file)
                    file_instance.file = result['public_id']
                    file_instance.file_path = result['secure_url']
                
                file_instance.save()
                messages.success(request, 'File uploaded successfully!')
                return redirect('filemanagement:dashboard')
            else:
                messages.error(request, 'Error uploading file. Please check the form.')
        else:
            form = EmployeeFileForm()
        
        context = {
            'form': form,
            'employees': Employee.objects.filter(is_active=True).order_by('name'),
            'file_types': FileType.objects.filter(is_active=True),
            'file_statuses': FileStatus.objects.filter(is_active=True),
        }
        
        return render(request, 'filemanagement/upload_file.html', context)
    except Exception as e:
        return render(request, 'filemanagement/error.html', {
            'error_title': 'File Upload Error',
            'error_message': 'There was a problem uploading the file.',
            'error_details': str(e),
            'back_url': request.META.get('HTTP_REFERER'),
            'back_text': 'Try Again'
        })

@login_required
@user_passes_test(is_admin)
def delete_file(request, file_id):
    """Delete a file with confirmation"""
    file_instance = get_object_or_404(EmployeeFile, id=file_id)
    
    if request.method == 'POST':
        # Delete from Cloudinary if file exists
        if file_instance.file:
            destroy(file_instance.file)
        
        # Delete the file record from the database
        file_instance.delete()
        messages.success(request, 'File deleted successfully!')
        return redirect('filemanagement:dashboard')
    
    # Show confirmation page
    return render(request, 'filemanagement/confirm_delete.html', {'file': file_instance})

@login_required
@user_passes_test(is_admin)
def preview_file(request, file_id):
    """View for previewing files"""
    try:
        file_instance = get_object_or_404(EmployeeFile, id=file_id)
        
        context = {
            'file': file_instance,
        }
        
        return render(request, 'filemanagement/preview_file.html', context)
    except Exception as e:
        return render(request, 'filemanagement/error.html', {
            'error_title': 'Preview Error',
            'error_message': 'There was a problem previewing the file.',
            'error_details': str(e),
            'back_url': request.META.get('HTTP_REFERER') or reverse('filemanagement:dashboard'),
            'back_text': 'Go Back'
        })

@login_required
@user_passes_test(is_admin)
def download_file(request, file_id):
    """Download a file"""
    try:
        file = get_object_or_404(EmployeeFile, id=file_id)
        
        # If file is stored in Cloudinary, redirect to the file URL
        if file.file_path:
            return redirect(file.file_path)
        
        # If file is not available, show an error message
        return render(request, 'filemanagement/error.html', {
            'error_title': 'File Not Available',
            'error_message': 'The requested file is not available for download.',
            'back_url': request.META.get('HTTP_REFERER') or reverse('filemanagement:dashboard'),
            'back_text': 'Go Back'
        })
    except Exception as e:
        return render(request, 'filemanagement/error.html', {
            'error_title': 'Download Error',
            'error_message': 'There was a problem downloading the file.',
            'error_details': str(e),
            'back_url': request.META.get('HTTP_REFERER') or reverse('filemanagement:dashboard'),
            'back_text': 'Go Back'
        })

@login_required
@user_passes_test(is_admin)
def send_file(request, file_id):
    """Send a file via email"""
    try:
        file = get_object_or_404(EmployeeFile, id=file_id)
        
        if request.method == 'POST':
            # Get email details from the form
            receiver_email = request.POST.get('receiver_email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            update_status = request.POST.get('update_status') == 'on'
            
            # Send email logic would go here
            # For now, we'll just update the file status and receiver email
            
            file.receiver_email = receiver_email
            if update_status:
                # Assuming 'Sent' is a valid FileStatus
                sent_status = FileStatus.objects.filter(name='Sent').first()
                if sent_status:
                    file.file_status = sent_status
            
            file.save()
            
            messages.success(request, f"File sent to {receiver_email} successfully.")
            return redirect('filemanagement:dashboard')
        
        return render(request, 'filemanagement/send_file.html', {'file': file})
    except Exception as e:
        return render(request, 'filemanagement/error.html', {
            'error_title': 'Send File Error',
            'error_message': 'There was a problem sending the file.',
            'error_details': str(e),
            'back_url': request.META.get('HTTP_REFERER') or reverse('filemanagement:dashboard'),
            'back_text': 'Go Back'
        })