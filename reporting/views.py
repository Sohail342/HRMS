from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils import timezone
from group_head.decorators import is_letter_template_admin_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
import cloudinary
import json
import base64
from datetime import datetime, timedelta, date
from .models import Signature, LetterTemplates, HospitalName, PermenantLetterTemplates, Purpose, PulicHolidays
from django.views.generic import DetailView, ListView
from HRIS_App.models import Employee
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from employee_attendance.models import LeaveApplication
from employee_attendance.models_leave_management import EmployeeLeaveBalance, LeaveType


@csrf_exempt
def save_pdf_to_cloudinary(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pdf_data = data.get('pdf_data')
            sap_id = data.get('sap_id')
            
            # Validate the data
            if not pdf_data or not sap_id:
                return JsonResponse({'success': False, 'error': 'Missing required data'}, status=400)
            
            # Get the employee object
            employee = get_object_or_404(Employee, SAP_ID=sap_id)
            
            # Convert base64 to file
            pdf_data = pdf_data.split(',')[1] if ',' in pdf_data else pdf_data
            pdf_bytes = base64.b64decode(pdf_data)
            
            # Upload PDF to Cloudinary
            upload_result = cloudinary.uploader.upload(
                pdf_bytes, 
                resource_type="raw", 
            )
            
            template_url = upload_result['secure_url']
            
            # Save template record
            template_upload = LetterTemplates(employee=employee, template_saved_url=template_url)
            template_upload.save()
            
            return JsonResponse({'success': True, 'url': template_url})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def get_employee(request):
    sap_id = request.GET.get('sap_id')
    employee = get_object_or_404(Employee, SAP_ID=sap_id)
    

    data = {
        'employee_name': employee.name,
        'employee_type': str(employee.employee_type) if employee.employee_type else "",
        'employee_cnic':employee.cnic_no,
        'designation': employee.designation_id,
        'sap_id': str(employee.SAP_ID) if employee.SAP_ID else "", 
        'employee_grade': str(employee.employee_grade),
        'employee_salutation': str(employee.employee_salutation),
    }
    return JsonResponse(data)



#  AJAX request
def get_employee_data(request):
    sap_id = request.GET.get('sap_id')
    employee = get_object_or_404(Signature, SAP_ID=sap_id)

    
    data = {
        'employee_name': employee.employee_name if employee.employee_name else "",
        'designation': str(employee.designation) if employee.designation else "",
        'grade': str(employee.grade) if employee.grade else "",
        'department': str(employee.department) if employee.department else "",
        'wing': str(employee.wing) if employee.wing else "",
        'division': str(employee.division) if employee.division else "",
        'group': str(employee.group) if employee.group else "", 
    }

    return JsonResponse(data)



class MemorandumMixin:
    model = Employee
    context_object_name = 'employee'
    
    def get_object(self):
        sap_id = self.kwargs.get('sap_id') or self.request.GET.get('sap_id')
        if sap_id:
            return get_object_or_404(Employee, SAP_ID=sap_id)
        return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        return context
    
@method_decorator(is_letter_template_admin_required, name='dispatch')
class LeaveMemorandum(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_time = timezone.now()
        weekday = current_time.strftime('%A')

        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        context['admin_signuture'] = Signature.objects.all()
        context['current_time'] = current_time
        context['next_day'] = current_time + timedelta(days=1)
        context['next_next_day'] = current_time + timedelta(days=2)
        context['leave_types'] = LeaveType.objects.all()
        context['holidays'] = PulicHolidays.objects.all()
        context['is_friday'] = weekday == 'Friday',

        context['hospital_name'] = HospitalName.objects.all()
    
        return context
    
    def get_template_names(self):
        # Get the form_type from the session or use default
        form_type = self.request.session.get('form_type', 'leave_memorandum')
        
        # Choose template based on form_type
        if form_type == 'leave_memorandum_2':
            return ['reporting/letter_templates/leave_memorandum_2.html']
        else:
            return ['reporting/letter_templates/leave_memorandum.html']
    
    def dispatch(self, request, *args, **kwargs):
        # Store form_type in session if it's in the request
        form_type = request.GET.get('form_type')
        if form_type:
            request.session['form_type'] = form_type
        return super().dispatch(request, *args, **kwargs)
    # template_name is removed as we're using get_template_names() method


@method_decorator(is_letter_template_admin_required, name='dispatch')
class Hospitilization(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        context['admin_signuture'] = Signature.objects.all()
        context['hospital_name'] = HospitalName.objects.all()
        context['purposes'] = Purpose.objects.all()

        employee_type = str(context['employee'].employee_type)
        context['employee_type'] = employee_type
        return context
    template_name = 'reporting/letter_templates/hospitalization.html'



@method_decorator(is_letter_template_admin_required, name='dispatch')
class RequestForIssuanceOfficeMemorandum(MemorandumMixin, DetailView):
  template_name = 'reporting/letter_templates/request_for_issuance.html' 




@is_letter_template_admin_required
def template_search(request):
    templates = None
    
    if request.method == 'POST':
        sap_id = request.POST.get('sap_id', '')
        
        # Get the employee object
        try:
            employee = Employee.objects.get(SAP_ID=sap_id)
            # Get all templates for this employee
            template_list = LetterTemplates.objects.filter(employee=employee).order_by('-created_at')
            
            # Pagination
            paginator = Paginator(template_list, 10)
            page = request.GET.get('page', 1)
            templates = paginator.get_page(page)
            
        except Exception as e:
            # No employee found with this SAP ID
            templates = []
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'reporting/template_search.html', context)



@is_letter_template_admin_required
def search_permanent_saved_templates(request):
    templates = None
    if request.method == 'POST':
        sap_id = request.POST.get('sap_id', '')
         
        # Get the employee object with select_related to optimize queries
        try:
            # Force a fresh database query by using .all() and not caching the queryset
            employee = Employee.objects.filter(SAP_ID=sap_id).first()
            
            if employee:
                # Get all templates for this employee with optimized query
                template_list = PermenantLetterTemplates.objects.filter(
                    employee=employee
                ).select_related('employee').order_by('-created_at').all()
                
                # Pagination with proper default page (1 instead of 10)
                items_per_page = 10
                paginator = Paginator(template_list, items_per_page)
                page = request.GET.get('page', 1)
                
                try:
                    # Convert page to integer and handle invalid page numbers
                    page_number = int(page)
                    templates = paginator.get_page(page_number)
                except ValueError:
                    # If page is not an integer, deliver first page
                    templates = paginator.get_page(1)
            else:
                templates = []
                
        except Exception as e:
            # No employee found with this SAP ID
            templates = []

    context = {
        'templates': templates,
    }
    
    return render(request, 'reporting/search_permanant.html', context)



class LetterForm(LoginRequiredMixin, ListView):
    
    model = Employee
    context_object_name = 'employees'
    template_name = 'reporting/letter_form.html'
    login_url = 'account:login'
    
    FORM_TYPE_MAPPING = {
        'leave_memorandum': 'reporting:leave_memorandum',
        'leave_memorandum_2': 'reporting:leave_memorandum',  
        'privilege_leave_memorandum': 'reporting:privilege_leave_memorandum',
        'joining_memorandum': 'reporting:joining_memorandum',
        'order_office_memorandun': 'reporting:order_office_memorandun',
        'hospitalization': 'reporting:hospitalization',
        'maternity_Leave': 'reporting:maternity_Leave',
        'request_for_issuance': 'reporting:request_for_issuance',
        'payment_of_bill': 'reporting:payment_of_bill',
        'grant_of_extension': 'reporting:grant_of_extension',
        'reimbursement': 'reporting:reimbursement',
        'reimbursement_against_purchase': 'reporting:reimbursement_against_purchase',
        'relieving_order': 'reporting:relieving_order',
    }



    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')
        sap_id = request.POST.get('sap_id', '')
        description = request.POST.get('description')
        sap_id_for_template_upload = request.POST.get('sap_id_for_template_upload')

        if 'pdf_file' in request.FILES:
            uploaded_file = request.FILES['pdf_file']

            # Validate the file type (only allow PDF)
            if not uploaded_file.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed.")
                return redirect('reporting:lettername')


            # Validate SAP ID for template upload
            if not sap_id_for_template_upload or sap_id_for_template_upload.strip() == '':
                messages.error(request, "Please enter a valid SAP ID for template upload.")
                return redirect('reporting:lettername')
                
            try:
                # Convert to integer
                sap_id_for_template_upload = int(sap_id_for_template_upload)
                
                # Get the employee object
                employee = get_object_or_404(Employee, SAP_ID=sap_id_for_template_upload)

                # Upload PDF to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    uploaded_file, resource_type="raw"
                )   
                template_url = upload_result['secure_url']

                # Save template record
                template_upload = PermenantLetterTemplates(employee=employee, template_saved_url=template_url, description=description)
                template_upload.save()

                messages.success(request, "Template uploaded successfully.")
                return redirect('reporting:lettername')
            except ValueError:
                messages.error(request, "SAP ID must be a valid number.")
                return redirect('reporting:lettername')

            except ValidationError as e:
                messages.error(request, f"Error uploading file: {e}")

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('reporting:lettername')

        # Special handling for leave_memorandum and privilege_leave_memorandum which don't require SAP ID
        if form_type in ['leave_memorandum', 'privilege_leave_memorandum']:
            # For these form types, we don't need SAP ID
            redirect_view = self.FORM_TYPE_MAPPING.get(form_type)
            if redirect_view:
                # If SAP ID is provided and valid, include it in the URL
                if sap_id and sap_id.strip() != '':
                    try:
                        sap_id = int(sap_id)
                        url = f"{reverse(redirect_view)}?sap_id={sap_id}"
                        return redirect(url)
                    except ValueError:
                        # If SAP ID is invalid, just redirect without it
                        return redirect(reverse(redirect_view))
                else:
                    return redirect(reverse(redirect_view))
            else:
                errors = "Invalid form type."
                return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})
        
        # Validate SAP ID for other form types
        if not sap_id or sap_id.strip() == '':
            errors = "Please enter a valid SAP ID."
            return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})
            
        try:
            sap_id = int(sap_id)  # Convert to integer
            verify_sap_id = Employee.objects.get(SAP_ID=sap_id)
        except ValueError:
            errors = "SAP ID must be a valid number."
            return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})
        except Employee.DoesNotExist:
            errors = "SAP ID is not registered."
            return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})
        
        # Redirect based on the form type
        redirect_view = self.FORM_TYPE_MAPPING.get(form_type)
        if redirect_view:
            # For other views that require sap_id in the URL
            return redirect(redirect_view, sap_id=sap_id)
        
        # If no valid form type, render the same page with error
        errors = "Invalid form type."
        return render(request, self.template_name, {'errors': errors, 'employees': self.get_queryset()})



@is_letter_template_admin_required
def application_leave(request, sap_id):
    if request.method == 'POST':

        leave_type = request.POST.get('leave_type_option')
        leave_days = request.POST.get('granted_leaves') 
        from_date_str = request.POST.get('effect_from')
        reason = request.POST.get('purpose')

        # Convert string date to datetime object first
        date_format = "%Y-%m-%d"
        from_date = datetime.strptime(from_date_str, date_format).date()
        
        # Calculate to_date using the datetime object
        to_date = from_date + timezone.timedelta(days=(int(leave_days) - 1) + 1 )

        # Calculate availed leave
        availed_leave = (to_date - from_date).days + 1
        
        # Convert Leave type to Full form
        if leave_type == 'CL':
            leave_type = 'Casual'
        elif leave_type == 'ML':
            leave_type = 'Mandatory'
        elif leave_type == 'SL':
            leave_type = 'Sick'
        elif leave_type == 'PL':
            leave_type = 'Privilege'
        elif leave_type == 'Ex-Pak':
            leave_type = 'Ex-Pakistan'


        # Validate the data
        if not sap_id or not leave_type or not from_date or not reason:
            messages.error(request, "All fields are required.")
            return redirect(f"{reverse('reporting:leave_memorandum')}?sap_id={sap_id}")

        # Get the employee object
        employee = get_object_or_404(Employee, SAP_ID=sap_id)

        # Save the leave application
        try:
            leave_application = LeaveApplication(
                employee=employee,
                application_type=leave_type,
                leave_date=datetime.now().date(),
                from_date=from_date,
                to_date=to_date,
                reason=reason,
                availed_leaves=int(leave_days)
            )
            leave_application.save()

        except Exception as e:
            messages.error(request, f"Error saving leave application: {e}")
            return redirect(f"{reverse('reporting:leave_memorandum')}?sap_id={sap_id}")

        messages.success(request, "Leave application submitted successfully.")
        return redirect(f"{reverse('reporting:leave_memorandum')}?sap_id={sap_id}")

    return render(request, 'reporting/leave_memorandum.html', sap_id=sap_id)
    







    

# Add a new view function to get letter templates for dropdown
def get_letter_templates(request):
    """View function to provide letter templates data for dropdown"""
    try:
        templates = [
            {'id': 'leave_memorandum', 'name': 'Leave Memorandum'},
            {'id': 'privilege_leave_memorandum', 'name': 'Privilege Leave Memorandum'},
            {'id': 'request_for_issuance', 'name': 'Request For Issuance'},
            {'id': 'hospitalization', 'name': 'Hospitalization'}
        ]
        return JsonResponse({'templates': templates})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_letter_templates: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def get_employee_leave_balance(request):
    """API endpoint to get employee leave balance by SAP ID and leave type"""
    sap_id = request.GET.get('sap_id')
    leave_type_id = request.GET.get('leave_type_id')
    
    if not sap_id:
        return JsonResponse({'error': 'SAP ID is required'}, status=400)
    
    try:
        # Get the employee
        employee = get_object_or_404(Employee, SAP_ID=sap_id)
        
        # Get current year
        current_year = date.today().year
        
        # Filter query based on whether leave_type_id is provided
        if leave_type_id:
            try:
                leave_type = LeaveType.objects.get(id=leave_type_id)
                balances = EmployeeLeaveBalance.objects.filter(
                    employee=employee,
                    leave_type=leave_type,
                    year=current_year
                )
            except LeaveType.DoesNotExist:
                return JsonResponse({'error': 'Leave type not found'}, status=404)
        else:
            # Get all leave balances for this employee
            balances = EmployeeLeaveBalance.objects.filter(
                employee=employee,
                year=current_year
            )
        
        # Format the response
        balance_data = []
        for balance in balances:
            balance_data.append({
                'leave_type_id': balance.leave_type.id,
                'leave_type_name': balance.leave_type.get_name_display(),
                'entitled_leaves': balance.entitled_leaves,
                'carried_forward_leaves': balance.carried_forward_leaves,
                'used_leaves': balance.used_leaves,
                'frozen_leaves': balance.frozen_leaves,
                'available_leaves': balance.available_leaves,
                'total_balance': balance.total_balance,
                'year': balance.year
            })
        
        return JsonResponse({
            'employee_name': employee.name,
            'sap_id': employee.SAP_ID,
            'leave_balances': balance_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    







    

@method_decorator(is_letter_template_admin_required, name='dispatch')
class PrivilegeLeaveMemorandum(MemorandumMixin, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_time = timezone.now()
        weekday = current_time.strftime('%A')

        context['employees'] = Employee.objects.all()
        context['current_time'] = timezone.now()
        context['admin_signuture'] = Signature.objects.all()
        context['current_time'] = current_time
        context['next_day'] = current_time + timedelta(days=1)
        context['next_next_day'] = current_time + timedelta(days=2)
        context['holidays'] = PulicHolidays.objects.all()
        context['is_friday'] = weekday == 'Friday',

        context['hospital_name'] = HospitalName.objects.all()
    
        return context
    
    template_name = 'reporting/letter_templates/leave_memorandum_2.html'
    







    

