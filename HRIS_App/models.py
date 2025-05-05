from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "  Group"


class FunctionalGroup(models.Model):
    name = models.CharField(max_length=100)
    allias = models.CharField(max_length=100, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, to_field="name", related_name='functional_groups')

    def __str__(self):
        return f'{self.name} - {self.group.name}'


class Division(models.Model):
    division_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True,default=None)
    functional_group = models.ForeignKey(FunctionalGroup, on_delete=models.CASCADE, related_name='divisions')

    class Meta:
        verbose_name = "Division"
        verbose_name_plural = " Division"

    def __str__(self):
        return self.division_name


class Wing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    division = models.ForeignKey(Division, to_field='division_name', on_delete=models.CASCADE, related_name='wings')

    def __str__(self):
        return self.name


class Region(models.Model):
    region_id = models.IntegerField(unique=True, default=None, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    region_category = models.CharField(max_length=100, blank=True, null=True)
    functional_group = models.ManyToManyField(FunctionalGroup, related_name='regions')
    csv_file = CloudinaryField(
        blank=True, 
        null=True, 
    )

    # Flag for head office
    head_office = models.BooleanField(default=False)

    # Region grading %
    A_Grade_seats = models.FloatField(default=15.0) 
    B_Grade_seats = models.FloatField(default=20.0)
    C_Grade_seats = models.FloatField(default=50.0)
    D_Grade_seats = models.FloatField(default=10.0)
    E_Grade_seats = models.FloatField(default=5.0)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "  Regions"


class Branch(models.Model):
    branch_code = models.IntegerField(unique=True)
    branch_name = models.CharField(max_length=500)
    branch_Category = models.CharField(max_length=100, default=None)
    branch_address = models.TextField(blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, to_field="name", null=True,  blank=True)

    def __str__(self):
        return self.branch_name
    
    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = " Branches"


class Designation(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, default="Null")

    def __str__(self):
        return self.title


class Cadre(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class EmployeeType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Employee Type"
        verbose_name_plural = " Employee Types"



class EmployeeGrade(models.Model):
    grade_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.grade_name
    
    class Meta:
        verbose_name = "Employee Grade"
        verbose_name_plural = " Employee Grades"


class Qualification(models.Model):
    QUALIFICATION_TYPE_CHOICES = [
        ('Professional', 'Professional'),
        ('Educational', 'Educational')
    ]
    name = models.CharField(max_length=300, unique=True)
    qualification_type = models.CharField(max_length=20, choices=QUALIFICATION_TYPE_CHOICES, blank=True, null=True, default="Educational")
    institution = models.CharField(max_length=100, blank=True, null=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.name} ({self.qualification_type})"




class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, is_admin_employee=False):
        """
        Creates and saves a User with the given email, name, and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_admin_employee=is_admin_employee,
        )
        
        if password:
            user.set_password(password)  # Set the provided password
        else:
            print("Unsable Password")
            user.set_unusable_password() 

        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email=email,
            name=name,
            password=password,
            is_admin_employee=True,  # Superusers are admin employees
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user




class Employee(AbstractBaseUser):
    # Core user fields
    
    email = models.EmailField(verbose_name="Email", max_length=255, blank=True, null=True, unique=True)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=128, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_admin_employee = models.BooleanField(default=False)
    is_letter_template_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Employee-related fields

    TRANSFER_CHOICES = [
        ('within_group', 'Transferred within Group'),
        ('outside_group', 'Transferred outside Group'),
    ]

    cnic_no = models.CharField(max_length=13, unique=True, blank=True, null=True)
    husband_or_father_name = models.CharField(max_length=100, blank=True, null=True)
    SAP_ID = models.IntegerField(default=None, unique=True, blank=True, null=True,)
    designation = models.ForeignKey(
        'Designation', on_delete=models.SET_NULL, null=True, blank=True, to_field='title'
    )
    cadre = models.ForeignKey(
        'Cadre', on_delete=models.SET_NULL, null=True, blank=True
    )
    employee_type = models.ForeignKey(
        'EmployeeType', on_delete=models.SET_NULL, null=True, blank=True, to_field='name'
    )
    employee_grade = models.ForeignKey(
        'EmployeeGrade', on_delete=models.SET_NULL, null=True, blank=True, to_field="grade_name"
    )
    branch = models.ForeignKey(
        'Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='employees', to_field="branch_code"
    )
    qualifications = models.ManyToManyField(
        'Qualification', related_name='employees', blank=True, 
    )
    region = models.ForeignKey(
        'Region', on_delete=models.CASCADE, null=True, to_field="name",  blank=True, related_name='employees'
    )
    date_of_retirement  = models.CharField(max_length=100, blank=True, null=True)
    place_of_posting  = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.CharField(max_length=100, blank=True, null=True)
    date_of_contract_expiry = models.CharField(max_length=100, blank=True, null=True)
    date_current_posting = models.CharField(max_length=100, blank=True, null=True)
    date_current_assignment = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, default="1111")
    admin_signature = models.BooleanField(default=False)
    employee_salutation = models.CharField(max_length=15, blank=True, null=True, default="MR.")
    date_of_joining = models.CharField(max_length=100, blank=True, null=True)
    user_group = models.CharField(max_length=200, default=None, blank=True, null=True)
    transferred_status = models.CharField(max_length=20, choices=TRANSFER_CHOICES, blank=True, null=True)
    pending_inquiry = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    transfer_remarks = models.TextField(blank=True, null=True)
    review_period = models.CharField(max_length=100, blank=True, null=True)
    first_appraiser = models.CharField(max_length=100, blank=True, null=True)
    second_appraiser = models.CharField(max_length=100, blank=True, null=True)


     # New grading field for APA 2024
    GRADE_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Very Good', 'Very Good'),
        ('Good', 'Good'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Unsatisfactory', 'Unsatisfactory'),
        ('Not Assigned', 'Not Assigned'),
    ]

    grade_assignment = models.CharField(max_length=100, choices=GRADE_CHOICES, blank=True, null=True, default='Not Assigned')

    # tracked employees if they are not an admin (is_admin=False) or an admin employee (is_admin_employee=False
    employee_user = models.BooleanField(default=True)


    # Upload PDF (BSC Form for employees on Cloudinary)
    pdf_file = CloudinaryField(
        blank=True, 
        null=True, 
    )
    '''Filds end'''

   

    def validate_grades(self):
        total_employees = 0
        try:
            # Get the total number of employees in the same region
            total_employees = Employee.objects.filter(is_admin=False).filter(region=self.region).count()
        except:
            # Get all employees if admin login
            total_employees = Employee.objects.filter().count()

        # If there are no employees, no validation is necessary
        if total_employees == 0:
            return


        if self.is_admin == False:
            '''
            Fetch the Region instance for employees or employees admin ( not admin itself) 
            and calculate grading eligbility base on Region % ( define in region model for each region) 
            '''
            region_instance = Region.objects.get(name=self.region)

            # Define the number of employees allowed per grade based on percentage
            grade_limits = {
                'Excellent': int(total_employees * region_instance.A_Grade_seats / 100),
                'Very Good': int(total_employees * region_instance.B_Grade_seats / 100),
                'Good': int(total_employees * region_instance.C_Grade_seats / 100),
                'Needs Improvement': int(total_employees * region_instance.D_Grade_seats / 100),
                'Unsatisfactory': int(total_employees * region_instance.E_Grade_seats / 100),
            }


            # Convert to integers, with rounding to handle fractional employees
            grade_limits = {grade: int(limit) for grade, limit in grade_limits.items()}

            # Calculate the remaining employees after applying the floor values
            assigned_employees = sum(grade_limits.values())
            remaining_employees = total_employees - assigned_employees

            # Distribute the remaining employees (this could go to the grade with the smallest number)
            if remaining_employees > 0:
                # Add remaining employees to the lowest grade
                grade_limits['Unsatisfactory'] += remaining_employees

            # Count how many employees currently have each grade
            current_grade_counts = Employee.objects.filter(region=self.region).values('grade_assignment').annotate(count=models.Count('id'))

            # Subtract the current counts from the grade limits
            for entry in current_grade_counts:
                grade = entry['grade_assignment']
                count = entry['count']
                if grade in grade_limits:
                    grade_limits[grade] -= count


            # Check if the current instance's grade exceeds the remaining limit
            if self.grade_assignment in grade_limits and grade_limits[self.grade_assignment] <= 0:
                raise ValueError(f"The grade '{self.grade_assignment}' has already reached its limit in the region.")


    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # Hash the password

    def check_password(self, raw_password):
        if self.password is None:
            return False  # Password is not set, cannot authenticate
        return check_password(raw_password, self.password)
    

    def save(self, *args, **kwargs):
        # Ensure that only employees are tracked, excluding admins or admin employees
        if self.is_admin or self.is_admin_employee:
            self.employee_user = False 
        else:
            self.employee_user = True 

        # Clear remarks and transfer status if no pending inquiry
        if not self.pending_inquiry:
            self.remarks = ""
            self.transferred_status = ""

        # Validate grades before saving
        self.validate_grades()

        # Ensure all validations are applied
        self.full_clean()

        # Save the instance
        super().save(*args, **kwargs)


        
    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = " Employees"


