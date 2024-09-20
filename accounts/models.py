from django.db import models
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import uuid
import random
from data_management.models import Country, State
# from django.contrib.auth.management.commands import createsuperuser
# Create your models here.


erp_role_choices = [('dont have access', 'dont have access'),
                    ('read', 'read'),
                    ('write', 'write')]


class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    pincode = models.CharField(max_length=100, null=True, blank=True)
    gst_number = models.CharField(blank=True, max_length=30)
    # door_no = models.CharField(max_length=100,null=True,blank=True)
    branch_code = models.CharField(
        editable=False, unique=True, max_length=10, null=True, blank=True, default='branchcode')
    branch_name = models.CharField(
        max_length=30, unique=True, null=True, blank=True)
    address = models.CharField(
        max_length=50, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.branch_code = str(uuid.uuid4())[:6]
        return super(Branch, self).save(*args, **kwargs)

    def __str__(self):
        return self.branch_name
    

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    role = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Sub_division(models.Model):
    id = models.AutoField(primary_key=True)
    department = models.ForeignKey(
        Department, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name
    

class FileUpload(models.Model):
    file = models.BinaryField()
    file_name = models.CharField(max_length=100,null=True,blank=True)
    file_type = models.CharField(max_length=100,null=True,blank=True)
    uploaded_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file_name
    

    
class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL)
    role = models.CharField(max_length=30, unique=True)
    division = models.ForeignKey(
        Sub_division, null=True, blank=True, on_delete=models.SET_NULL)
    access = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.role
    

class MyUserManager(BaseUserManager):
    def create_user(self, employee_id, password, name, **extra_fields):
        if not employee_id:
            raise ValueError('The Employee ID must be set')
        if not name:
            raise ValueError('The Name must be set')
        
        phone = extra_fields.get('phone', None)
        department_id = extra_fields.get('department', None)
        sub_division = extra_fields.get('department_subdivision', None)
        role = extra_fields.get('role', None)
        email = extra_fields.get('email', None)
        # branch = extra_fields.get('branch', None)

        if phone:
            try:
                phone = int(phone)
            except:
                raise ValueError('Phone number must contain only numbers')
            
        # Create the user instance
        user = self.model(
            employee_id=employee_id,
            name=name,
            email=email,
            phone=phone,
            department=department_id,
            department_subdivision=sub_division,
            role=role,
            # branch=branch,
            **extra_fields
        )
        
        # Set the user's password
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, password, name, **extra_fields):
        # Create the user with the provided details
        user = self.create_user(
            employee_id=employee_id,
            password=password,
            name=name,
            **extra_fields
        )
        try:
            user_role = UserRole.objects.get(role='admin')
        except:
            user_role = UserRole.objects.create(role='admin')

        user.role = user_role
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    employee_id = models.CharField(unique=True, null=False, max_length=50)
    name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=10,
        validators=[MinLengthValidator(10)],
        null=True,
        blank=True
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    department_subdivision = models.ForeignKey(Sub_division, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    reset_password = models.BooleanField(default=True)
    # branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = MyUserManager()
    
    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['name', 'password']

    def save(self, *args, **kwargs):
        # self.id = self.employee_id
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.employee_id

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        return self.role and self.role.role and self.role.role.lower() == 'admin'
    
    class Meta:
        ordering = ('created_at',)


class Activities(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    table = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    action = models.CharField(max_length=30)

    def __str__(self):
        return self.name + '-' + self.action


class Configurations(models.Model):
    configuration_details = models.JSONField(null=True,blank=True)