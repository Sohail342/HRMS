from django.db import models
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.division_name


class Wing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    division = models.ForeignKey(Division, to_field='division_name', on_delete=models.CASCADE, related_name='wings')

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    region_category = models.CharField(max_length=100, blank=True, null=True)
    functional_group = models.ManyToManyField(FunctionalGroup, related_name='regions')

    # Flag for head office
    head_office = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Branch(models.Model):
    branch_code = models.IntegerField(unique=True)
    branch_name = models.CharField(max_length=100, unique=True)
    branch_Category = models.CharField(max_length=100, default=None)
    branch_address = models.TextField(blank=True, null=True)
    branch_region = models.ForeignKey(Region, on_delete=models.CASCADE, to_field='name', null=True,  blank=True)

    def __str__(self):
        return self.branch_name


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


class EmployeeGrade(models.Model):
    grade_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.grade_name


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
    def create_user(self, email, name, password=None, password2=None, is_admin_employee=False):
        """
        Creates and saves a User with the given email, name, and password.
        If the user already exists, it ensures the password is not overwritten.
        """
        if not email:
            raise ValueError("Users must have an email address")

        # Check if user exists or create a new user instance
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            is_admin_employee=is_admin_employee,
        )

        # Only set password if provided and if user is admin
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # If no password is provided, make the password unusable.

        user.save(using=self._db)
        return user

    def update_user(self, user, name=None, email=None, password=None, is_admin_employee=None):
        """
        Update an existing user without resetting the password unless specified.
        """
        updated = False

        if name:
            user.name = name
            updated = True
        if email:
            user.email = self.normalize_email(email)
            updated = True
        if is_admin_employee is not None:
            user.is_admin_employee = is_admin_employee
            updated = True
        if password:
            user.set_password(password)  # Only update the password if provided
            updated = True

        # Only save the user if something was updated
        if updated:
            user.save(using=self._db)
        
        return user



    def create_superuser(self, email, name,  password=None):
        """
        Creates and saves a superuser with the given email, name
        and password.
        """
        user = self.create_user(
            email,
            name=name,
            is_admin_employee=True,
        )

        user.set_password(password)

        user.is_admin = True
        user.is_active = True 
        user.save(using=self._db)
        return user



class Employee(AbstractBaseUser):
    # Core user fields
    
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_admin_employee = models.BooleanField(default=False)
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
        'Branch', on_delete=models.CASCADE, null=True, blank=True, related_name='employees', to_field="branch_name"
    )
    qualifications = models.ManyToManyField(
        'Qualification', related_name='employees', blank=True
    )
    region = models.ForeignKey(
        'Region', on_delete=models.CASCADE, null=True, blank=True, related_name='employees'
    )
    date_of_last_promotion = models.DateField(default="1900-01-01", blank=True, null=True)
    date_current_posting = models.DateField(default="1900-01-01", blank=True, null=True)
    date_current_assignment = models.DateField(default="1900-01-01", blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, default="1111")
    admin_signature = models.BooleanField(default=False)
    phone_no_emergency_contact = models.CharField(max_length=15, blank=True, null=True, default="1111")
    employee_email = models.EmailField(max_length=100, blank=True, null=True, default="aa@aa.aa")
    date_of_joining = models.DateField(default="1900-01-01", blank=True, null=True)
    user_group = models.CharField(max_length=200, default=None, blank=True, null=True)
    transferred_status = models.CharField(max_length=20, choices=TRANSFER_CHOICES, blank=True, null=True)
    pending_inquiry = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    
    

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

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
    

    def save(self, *args, **kwargs):

        # Hash the password only if it's not already hashed
        if self.pk is None or (self.password and not self.password.startswith('pbkdf2_')):
            self.set_password(self.password)  # Hash the password

        '''When Pending case is False, remove remarks and transferred_status'''
        if not self.pending_inquiry:
            self.remarks = ""
            self.transferred_status = ""
    

        super(Employee, self).save(*args, **kwargs)

        

    def set_password(self, raw_password):
        super().set_password(raw_password)
        self._password_set = True  


