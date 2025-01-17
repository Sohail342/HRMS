from django.shortcuts import render, redirect
from HRIS_App.models import Region, Employee
from django.contrib import messages
from group_head.decorators import employee_user_required
from django.contrib.auth.decorators import login_required
from .forms import CreatePasswordForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404
from .models import RicpData, RicpKPI
from django.utils.dateformat import DateFormat
import json


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

    if request.method == "POST":
        review_period = request.POST['review_period']
        first_appraiser = request.POST['first_appraiser']
        second_appraiser = request.POST['second_appraiser']
        wing_dept = request.POST['wing_dept']
        division = request.POST['division']
        joining_date = request.POST['joining_date']
        employee = request.user.SAP_ID
        
        # Create or update the Employee object
        employee_data, created = Employee.objects.get_or_create(SAP_ID=employee)

        # Update the employee's information
        employee_data.review_period = review_period
        employee_data.first_appraiser = first_appraiser
        employee_data.second_appraiser = second_appraiser
        employee_data.date_of_joining = joining_date
        employee_data.save()

        messages.success(request, "Data Sucessfully Updated")
        return redirect("employee_user:ricp_form")

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




# -------------------------------------------------------------------------------------------------------

from employee_attendance.models import  LeaveApplication

@login_required(login_url="employee_user:user_login")
@employee_user_required
def dashboard_view(request):
    user_type = request.user.employee_type
    
    # Get leaves for employee ( requested user )
    casual_leaves = LeaveApplication.objects.filter(employee=request.user, application_type='Casual').values('availed_leaves')
    casual_leaves_count = sum(item['availed_leaves'] for item in casual_leaves)
    remaining_casual_leaves = 20 - casual_leaves_count
    
    
    privilege_leaves = LeaveApplication.objects.filter(employee=request.user, application_type='Privilege').values('availed_leaves')
    privilege_leaves_count = sum(item['availed_leaves'] for item in privilege_leaves)
    remaining_privilege_leaves = 30 - privilege_leaves_count
    
    sick_leaves = LeaveApplication.objects.filter(employee=request.user, application_type='Sick').values('availed_leaves')
    sick_leaves_count = sum(item['availed_leaves'] for item in sick_leaves)
    remaining_sick_leaves = 18 - sick_leaves_count

    pending_count = LeaveApplication.objects.filter(employee=request.user, status='Pending').count()
    approved_count = LeaveApplication.objects.filter(employee=request.user, status='approved').count()
    declined_count = LeaveApplication.objects.filter(employee=request.user, status='declined').count()


    
    content = {
        "user_type":str(user_type),
        'casual_leaves': casual_leaves_count,
        'remaining_casual_leaves': remaining_casual_leaves,
        
        'privilege_leaves': privilege_leaves_count,
        'remaining_privilege_leaves': remaining_privilege_leaves,
        
        'sick_leaves': sick_leaves_count,
        'remaining_sick_leaves':remaining_sick_leaves,

        'pending_count': pending_count,
        'approved_count': approved_count,
        'declined_count': declined_count,

    }
    return render(request, 'employee_attendance/permanent_leave_dashboard.html', content)




# RICP 
@login_required(login_url="employee_user:user_login")
@employee_user_required
def RICP(request):
    employee = request.user
    
    # Get data for filled forms
    form_data = RicpKPI.objects.filter(ricp_data__employee=employee).filter(bsc_form_type="RICP")

    if request.method == "POST":
        # Delete the form data
        form_data.delete()
        return redirect("employee_user:ricp_form")
    return render(request, 'employee_user/RICP.html', {"form_data": form_data})



#customer_kpi
@login_required(login_url="employee_user:user_login")
@employee_user_required
def customer_kpi(request):
    employee = request.user

    # Get data for filled forms
    form_data = RicpKPI.objects.filter(ricp_data__employee=employee).filter(bsc_form_type="customer_kpi")

    if request.method == "POST":
        # Delete the form data
        form_data.delete()
        return redirect("employee_user:customer_kpi")
    return render(request, 'employee_user/customer_kpi.html', {"form_data": form_data})

#financials_kpi
@login_required(login_url="employee_user:user_login")
@employee_user_required
def financials_kpi(request):
    employee = request.user

    # Get data for filled forms
    form_data = RicpKPI.objects.filter(ricp_data__employee=employee).filter(bsc_form_type="financials_kpi")

    if request.method == "POST":
        # Delete the form data
        form_data.delete()
        return redirect("employee_user:financials_kpi")
    return render(request, 'employee_user/Financials_kpi.html', {"form_data": form_data})



#learning_growth_kpi
@login_required(login_url="employee_user:user_login")
@employee_user_required
def learning_growth_kpi(request):
    employee = request.user

    # Get data for filled forms
    form_data = RicpKPI.objects.filter(ricp_data__employee=employee).filter(bsc_form_type="learning_Growth_kpi")

    if request.method == "POST":
        # Delete the form data
        form_data.delete()
        return redirect("employee_user:learning_growth_kpi")
    return render(request, 'employee_user/Learning_Growth_kpi.html', {"form_data": form_data})



@csrf_protect
def submit_form_data(request):
    if request.method == "POST":
        # Extract data
        employee_id = request.user.SAP_ID
        kpis = json.loads(request.POST.get("kpis"))
        form_final_score = request.POST.get("finalScore")

        bsc_form_type = request.POST.get('bsc_form_type')

        # Get or create the data for the employee
        employee = get_object_or_404(Employee, SAP_ID=employee_id)
        form_data, created = RicpData.objects.get_or_create(employee=employee)
        form_data.save()


        # Save KPIs
        for kpi_data in kpis:
            # Check score is digit or not ( if not set to 0)
            score = kpi_data.get("score")
            if not score:
                score = 0


            RicpKPI.objects.create(
                ricp_data=form_data,
                kpi=kpi_data["kpi"],
                achievement=kpi_data["achievement"],
                weightage=kpi_data.get("weightage"),
                target_date=kpi_data["targetDate"],
                bsc_form_type=bsc_form_type,
                score=score,
                form_final_score=form_final_score,
            )

            # Redirect based on `bsc_form_type`
        if bsc_form_type == "RICP":
            return JsonResponse({"redirect_url": "/user/customer_kpi/form/"})
        elif bsc_form_type == "customer_kpi":
            return JsonResponse({"redirect_url": "/user/financials_kpi/form/"})
        elif bsc_form_type == "financials_kpi":
            return JsonResponse({"redirect_url": "/user/learning_growth_kpi/form/"})
        elif bsc_form_type == "learning_Growth_kpi":
            return JsonResponse({"redirect_url": "/user/kpi/summary/"})

        
        # Return a success message
        return JsonResponse({"message": "Submitted successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)



# Display Overall KPIS Result
def overall_kpi_result(request):
    
    # Final form scores
    ricp_form_final_score = 0
    customer_form_final_score = 0
    financials_form_final_score = 0
    learning_growth_form_final_score = 0
    
    try:
        employee = Employee.objects.get(SAP_ID=request.user.SAP_ID)
        ricp_data = RicpData.objects.get(employee=employee)
        ricp_kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="RICP")
        financials_kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="financials_kpi")
        customer_kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="customer_kpi")
        learning_growth_kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="learning_Growth_kpi")



        '''    
                    Get the final evaluation for the employee
        Get Distinct forms for requested user or get data for filled forms
        
        '''
        ricp_data = RicpKPI.objects.filter(ricp_data__employee=employee).values('bsc_form_type').distinct()

        # Get the form final score for each form
        form_final_scores = {}
        for form in ricp_data:
            form_final_scores[form["bsc_form_type"]] = RicpKPI.objects.filter(ricp_data__employee=employee, bsc_form_type=form["bsc_form_type"]).last().form_final_score
        
    
        for value in ricp_kpis:
            ricp_form_final_score = value.form_final_score 
            
        for value in financials_kpis:
            financials_form_final_score = value.form_final_score
            
        for value in customer_kpis:
            customer_form_final_score = value.form_final_score
            
        for value in learning_growth_kpis:
            learning_growth_form_final_score = value.form_final_score
            
            
            
        # Sum the all form final scores
        total_score = sum(form_final_scores.values())

        # Get the final evaluation
        final_evaluation = "Unsatisfactory"
        if total_score == 0:
            final_evaluation = ""
        elif total_score <= 1:
            final_evaluation = "Unsatisfactory"
        elif total_score <= 2:
            final_evaluation = "Needs Improvement"
        elif total_score <= 3:
            final_evaluation = "Good"
        elif total_score <= 4:
            final_evaluation = "Very Good"
        elif total_score <= 5:
            final_evaluation = "Outstanding"



    except Employee.DoesNotExist:
        messages.error(request, "Employee with the given SAP ID does not exist.")
        return redirect("employee_user:dashboard")


    context = {
        "ricp_form_final_score": ricp_form_final_score,
        "customer_form_final_score": customer_form_final_score,
        "financials_form_final_score": financials_form_final_score,
        "learning_growth_form_final_score": learning_growth_form_final_score,
        "ricp_kpis": ricp_kpis,
        "financials_kpis": financials_kpis,
        "customer_kpis": customer_kpis,
        "learning_growth_kpis": learning_growth_kpis,
        "total_score": total_score,
        "final_evaluation": final_evaluation,
    }
    
    return render(request, 'employee_user/overall_kpi_result.html', context)


def update_kpis(request, form_type):
    kpis = []
    employee = request.user
    ricp_data = RicpData.objects.get(employee=employee)
    
    if form_type == "ricp":
        kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="RICP")
    if form_type == "customer_kpi":
        kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="customer_kpi")
    elif form_type == "financials_kpi":
        kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="financials_kpi")
    elif form_type == "learning_growth_kpi":
        kpis = RicpKPI.objects.filter(ricp_data=ricp_data, bsc_form_type="learning_Growth_kpi")
        
    from icecream import ic
    for i in kpis:
        ic(i.id)
    
    if request.method == "POST":
        for kpi in kpis:
            kpi.kpi = request.POST.get(f'kpi_{kpi.id}', kpi.kpi)
            kpi.achievement = request.POST.get(f'achievement_{kpi.id}', kpi.achievement)
            kpi.target_date = request.POST.get(f'target_date_{kpi.id}', kpi.target_date)
            kpi.score = request.POST.get(f'score_{kpi.id}', kpi.score)
            kpi.save()
        messages.success(request, "KPIs updated successfully!")
        return redirect('employee_user:update_kpis', form_type=form_type)

    return render(request, 'employee_user/update_kpis.html', {"ricp_kpis": kpis, "form_type": form_type})


def delete_kpi(request, kpi_id, form_type):
    
    kpi = RicpKPI.objects.get(id=kpi_id)
    kpi.delete()
    messages.success(request, "KPI deleted successfully!")
    return redirect('employee_user:update_kpis', form_type=form_type)

