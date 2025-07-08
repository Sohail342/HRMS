from django.shortcuts import render, redirect
from django.contrib import messages
import cloudinary
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from datetime import datetime

from .models import ContractRenewal, EducationalDocument
from .forms import EducationalDocumentForm, NonInvolvementCertificateForm, StationaryRequestForm
from apps.group_head.decorators import employee_user_required 





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



#  ------------- Educational Document Upload -------------
def upload_education_documents(request, sap_id):
    if request.method == "POST":
        try:
            document_file = EducationalDocument.objects.get(employee__SAP_ID=request.user.SAP_ID)
        except EducationalDocument.DoesNotExist:
            document_file = None

        if document_file is None:
            # Handle case where there is no existing document, or create a new one
            document_file = EducationalDocument(employee=request.user)

        if 'document' in request.FILES:
            uploaded_file = request.FILES.get('document')
            document_type = request.POST.get('document_type')

            # Validate the file type (only allow PDF)
            if not uploaded_file.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed.")
                return redirect('employee_attendance:upload_education_documents', sap_id=sap_id)

            try:
                # Save the file to the document object
                upload_result = cloudinary.uploader.upload(uploaded_file,  resource_type = "raw")
                document_file.document = upload_result['secure_url']
                document_file.document_type = document_type
                document_file.save()  # Save the document object to the database

                messages.success(request, "Your educational document has been uploaded successfully.")
                return redirect('employee_attendance:upload_education_documents', sap_id=sap_id)

            except ValidationError as e:
                messages.error(request, f"Error uploading file: {e}")
                return redirect('group_head:upload_pdf', sap_id=sap_id)
            
        else:
            messages.error(request, "Invalid file type. Only PDF files are allowed.")
            
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




def apply_permanent_leave(request):
    user_type = request.user.employee_type
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
    
    return render(request, 'employee_attendance/apply_permanent_leave.html', {'form': form, 'user_type': str(user_type)})


