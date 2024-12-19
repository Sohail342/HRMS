from django.shortcuts import render, redirect
from HRIS_App.models import Region, Employee
from django.contrib import messages
from group_head.decorators import employee_user_required
from django.contrib.auth.decorators import login_required
from .forms import CreatePasswordForm
from django.contrib.auth import login


# User Login
def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('employee_user:dashboard')
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        try:
            employee = Employee.objects.get(email=email)
            if employee.check_password(password):
                # Log the user in
                login(request, employee)
                messages.success(request, "Login successful!")
                return redirect('employee_user:dashboard') 
            else:
                messages.error(request, "Incorrect password.")
        except Employee.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    
    return render(request, "employee_user/login_user.html")


# Employees Information
@employee_user_required
def information_employee(request):
    employee = Employee.objects.get(SAP_ID=request.user.SAP_ID)

    # Functional groups
    group = None
    groups = employee.region.functional_group.all()

    for group in groups:
        group = group.group
        break

    return render(request, 'employee_user/information_employee.html', {"employee_information":employee, "group":group})



# User Verification
def verification_user_view(request):
    if request.user.is_authenticated:
        return redirect('employee_user:dashboard')
    

    query_set = Region.objects.values("name")

    if request.method == 'POST':
        sap_id = request.POST.get('sap_id').strip()
        region = request.POST.get('region')

        # Validate the user against the SAP ID and Region
        validate_user = Employee.objects.filter(SAP_ID=sap_id, region=region)
        
        if not validate_user:
            messages.error(request, "Invalid SAP ID or Region!")
            return redirect("employee_user:user_verification")
        else:
            return redirect("employee_user:create_password", sap_id=sap_id) 
    
    return render(request, "employee_user/user_verification.html", {'query_set': query_set})



# Create Password
def create_password_view(request, sap_id):
    if request.user.is_authenticated:
        return redirect('employee_user:dashboard')
    

    if request.method == "POST":
        form = CreatePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            
            # Check if the employee with the given SAP ID exists
            try:
                employee = Employee.objects.get(SAP_ID=sap_id)
                employee.password = password 
                employee.email = email
                employee.save()
                messages.success(request, "Password updated successfully.")
                return redirect('employee_user:user_login')
            except Employee.DoesNotExist:
                messages.error(request, "Employee with the given SAP ID does not exist.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CreatePasswordForm()

    return render(request, 'employee_user/create_password.html', {'form': form})



# Employee Dashboard
@login_required(login_url="employee_user:user_login")
@employee_user_required
def dashboard_view(request):
    return render(request, 'employee_user/dashboard.html')


# RICP 

def RICP(request):

    return render(request, 'employee_user/RICP.html', {"test":[1, 2, 3, 4, 5]})