from django.shortcuts import render, redirect
from group_head.decorators import employee_user_required 
from .models import ContractualLeaveRecord, ContractRenewal, LeaveRecordPremanent
from django.contrib import messages
from django.http import Http404
from .forms import EducationalDocumentForm, NonInvolvementCertificateForm, StationaryRequestForm, ContractualLeaveApplicationForm
from .forms import PermanentLeaveApplicationForm, ContractualLeaveApplicationForm, PermanentLeaveApplicationForm
from django.shortcuts import get_object_or_404
from django.db import models
from datetime import datetime


#------------- Non-Involvement Certificate Request -------------

def nicrequests(request):
    # Fetch employee info
    employee_name = request.user.name
    employee_id = request.user.SAP_ID 

    if request.method == "POST":
        form = NonInvolvementCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data
            certificate = form.save(commit=False)
            certificate.employee = request.user
            certificate.save()

            # Show success message
            messages.success(request, 'Your non-involvement certificate application has been submitted successfully.')
            return redirect('employee_attendance:nicrequests')

    else:
        form = NonInvolvementCertificateForm()

    return render(
        request, 
        'employee_attendance/n_i_c_request.html', 
        {
            'form': form, 
            'employee_name': employee_name,
            'employee_id': employee_id
        }
    )




def upload_education_documents(request):
    if request.method == "POST":
        form = EducationalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Set the employee (logged-in user)
            educational_document = form.save(commit=False) 
            educational_document.employee = request.user  
            educational_document.save() 
            from icecream import ic
            ic(educational_document)
                       
            messages.success(request, 'Your educational document has been uploaded successfully.')
            return redirect('employee_attendance:upload_education_documents') 
            
    else:
        form = EducationalDocumentForm()

    return render(request, 'employee_attendance/renewal_documents.html', {'form': form})




#------------- Contract Renewal Request -------------

@employee_user_required
def contractrenewal(request):
    
    employee_name = request.user.name
    employee_id = request.user.SAP_ID
    employee_position = request.user.employee_grade
    
    # Check if the employee is contractual
    if str(request.user.employee_type) != "Contractual":
        raise Http404("Page not found")
    
    if request.method == "POST":
        position = request.POST.get('position')
        reason = request.POST.get('reason')
        contract_expiry_date = request.POST.get('contract_expiry')
        supporting_docs = request.FILES.get('supporting_docs')

        # Create a new contract renewal request 
        contract_renewal = ContractRenewal(
            employee=request.user,
            position=position,
            reason=reason,
            renewal_document=supporting_docs,
            contract_expiry_date=contract_expiry_date  # Fixed variable name
        )
        contract_renewal.save()

        # Show success message
        messages.success(request, 'Your contract renewal request has been submitted successfully.')
        
        return redirect('employee_attendance:contractrenewal')


    return render(request, 'employee_attendance/contract_renewal.html',{
            'employee_name': employee_name,
            'employee_id': employee_id,
            'employee_position': employee_position
            
        })


#------------- Stationary Request -------------

def stationaryrequests(request):
    if not request.user.is_authenticated:
        raise Http404("Page not found")

    if request.method == "POST":
        form = StationaryRequestForm(request.POST)
        if form.is_valid():
            # Save the form data into the database
            stationary_request = form.save(commit=False)
            stationary_request.employee = request.user  # Set the current user as the employee
            stationary_request.save()

            # Show success message
            messages.success(request, 'Your stationary request has been submitted successfully.')
            return redirect('employee_attendance:stationaryrequests')  # Redirect to the same page or a success page

    else:
        form = StationaryRequestForm()  # Create an empty form instance

    return render(request, 'employee_attendance/stationary_request.html', {'form': form})



#---------------------- Leave Application -----------------------
    
# def permanent_leave_dashboard(request):
#     if request.method == 'POST':
#         form = PermanentLeaveApplicationForm(request.POST)
#         if form.is_valid():
#             leave_application = form.save(commit=False)
#             leave_application.employee = request.user  # Assuming the logged-in user is the employee
#             leave_application.save()
#             return redirect('leave_application_success')
#     else:
#         form = PermanentLeaveApplicationForm()

#     return render(request, 'employee_attendance/permanent_leave_dashboard.html', {'form': form,})
    
# def contractual_leave_dashboard(request):
#     casual_leave_record = ContractualLeaveRecord.objects.filter(
#         employee=request.user, leave_type__name="Casual"
#     ).first()
#     sick_leave_record = ContractualLeaveRecord.objects.filter(
#         employee=request.user, leave_type__name="Sick"
#     ).first()
#     frozen_leave_record = ContractualLeaveRecord.objects.filter(
#         employee=request.user, leave_type__name="Frozen"
#     ).first()
    
#     if request.method == 'POST':
#         form = ContractualLeaveApplicationForm(request.POST)
#         if form.is_valid():
#             leave_application = form.save()

#             # Retrieve the leave type and employee
#             leave_type = leave_application.leave_type
#             employee = leave_application.employee

#             # Check if a record exists for this leave type and employee
#             try:
#                 leave_record = ContractualLeaveRecord.objects.get(
#                     employee=employee, leave_type=leave_type)
                
#                 # Update availed leaves and remaining leaves
#                 leave_record.availed_leaves += (leave_application.to_date - leave_application.from_date).days + 1  # Include both dates
#                 leave_record.save()

#                 # Optionally, display the remaining leaves
#                 remaining_leaves = leave_record.remaining_leaves
#                 messages.success(request, f"Leave applied successfully! Remaining leaves: {remaining_leaves}")

#             except ContractualLeaveRecord.DoesNotExist:
#                 messages.error(request, "No leave record found for this employee and leave type.")

#             return redirect('leave_status')  # Redirect to an appropriate page (e.g., leave status page)

#     else:
#         form = ContractualLeaveApplicationForm()

#     return render(request, 'apply_contractual_leave.html', {'form': form,
#         "casual_leave_used": casual_leave_record.availed_leaves if casual_leave_record else 0,
#         "casual_leave_remaining": casual_leave_record.remaining_leaves if casual_leave_record else 20,
#         "sick_leave_used": sick_leave_record.availed_leaves if sick_leave_record else 0,
#         "sick_leave_remaining": sick_leave_record.remaining_leaves if sick_leave_record else 18,
#         "frozen_leave_total": frozen_leave_record.leave_type.total_leaves if frozen_leave_record else 0,
#         "frozen_leave_used": frozen_leave_record.availed_leaves if frozen_leave_record else 0,
#         "frozen_leave_remaining": frozen_leave_record.remaining_leaves if frozen_leave_record else 0,})

from .models import LeaveApplication

def apply_permanent_leave(request):
    try:
        form = PermanentLeaveApplicationForm(request.POST)
        if request.method == 'POST':
            application_type = request.POST['application_type']  
            from_date = request.POST['from_date']
            to_date = request.POST['to_date']  
            reason = request.POST['reason']
            
            date_format = "%Y-%m-%d"
            from_date = datetime.strptime(from_date, date_format).date()
            to_date = datetime.strptime(to_date, date_format).date()
            
            availed_leave = to_date - from_date
            
            
            data = LeaveApplication.objects.create(
                employee = request.user,
                availed_leaves = availed_leave.days,
                application_type = application_type,
                from_date = from_date,
                to_date = to_date,
                reason = reason
            )
            
            data.save()
        
        else:
            form = PermanentLeaveApplicationForm()
            
    except Exception as e:
        messages.error(request, "Error: " + str(e))

    return render(request, 'employee_attendance/apply_permanent_leave.html', {'form': form})



def apply_contractual_leave(request):
    if request.method == 'POST':
        print("Not Valid")
        from icecream import ic
        
        form = ContractualLeaveApplicationForm(request.POST)
        ic(form.application_type.field.choices)
        if form.is_valid():
            from icecream import ic
            print("Valid")
            leave_application = form.save(commit=False)
            
            leave_application.employee = request.user 
            ic(leave_application)

            # Fetch the leave_type instance correctly from the form
            leave_type = form.cleaned_data.get('leave_type')  # This will be the model instance

            # Fetch or create the leave record
            leave_record, created = ContractualLeaveRecord.objects.get_or_create(
                employee=request.user,
                leave_type=leave_type,
                defaults={"availed_leaves": 0},
            )

            # Check leave balance
            total_days = (leave_application.to_date - leave_application.from_date).days + 1
            if leave_record.remaining_leaves >= total_days:
                # Update leave balance
                leave_record.availed_leaves += total_days
                leave_record.save()

                # Save the leave application
                leave_application.save()
                messages.success(request, "Leave application submitted successfully!")
                return redirect('contractual_leave_dashboard')
            else:
                messages.error(request, "Insufficient leave balance!")
    else:
        form = ContractualLeaveApplicationForm()

    return render(request, 'employee_attendance/apply_contractual_leave.html', {'form': form})





