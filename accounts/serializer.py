from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from .models import Department, User, UserRole, Sub_division,Configurations #,Branch

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_str, force_bytes, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import BadHeaderError, send_mail
from django.conf import settings


class UserRoleSerializer(serializers.ModelSerializer):
    department_get = serializers.SerializerMethodField("get_department")
    division_get = serializers.SerializerMethodField("get_division")

    def get_division(self, obj):
        if obj.division:
            return obj.division.name
        return None

    def get_department(self, obj):
        if obj.department:
            return obj.department.name
        return None

    class Meta:
        model = UserRole
        fields = ['pk', 'id', 'role', 'department', 'access',
                  'department_get', 'division', 'division_get']


class Userprofileserializer(serializers.ModelSerializer):
    user_branch = serializers.SerializerMethodField("get_branch")
    role_get = serializers.SerializerMethodField(
        "get_role")
    branch_get = serializers.SerializerMethodField("get_branch_name")

    def get_branch_name(self, obj):
        if obj.branch:
            return obj.branch.branch_name
        return None

    def get_role(self, obj):
        if obj.role:
            return obj.role.role
        return None

    def get_branch(self, obj):
        if obj.branch:
            branch_obj = {'cityname': obj.branch.cityname,
                          'state': obj.branch.state.state_name,
                          'state_code':obj.branch.state.state_code,
                          'country': obj.branch.country.country_name,
                          'pincode': obj.branch.pincode,
                          'branch_name': obj.branch.branch_name,
                          "gst_number": obj.branch.gst_number, 
                          "address":obj.branch.address,
                          'gst_number': obj.branch.gst_number,
                          'industry_name':None
                          }
            # Branch.objects.filter(id = obj.branch.id).values_list
            configs = Configurations.objects.filter(configuration_details__has_key='industry_details')
            print(configs,'s')
            if len(configs):
                print(configs[0].configuration_details['industry_details'],'hi')
                branch_obj['industry_name'] = configs[0].configuration_details['industry_details']['Name']
            return branch_obj
        return None

    class Meta:
        model = User
        fields = ['pk', 'employee_id', 'name', 'email', 'phone', 'branch_get', 'role_get',
                  'department', 'department_subdivision', 'role', 'branch', 'user_branch']
        

class SubDivisionSerializer(serializers.ModelSerializer):
    department_get = serializers.SerializerMethodField("get_department")

    def get_department(self, obj):
        if obj.department:
            return obj.department.name
        return None

    def validate(self, data):
        division_obj = self.Meta.model.objects.filter(
            department=data['department'].id, name=(data['name']).lower())
        print(data['department'].id, data['name'])
        if len(division_obj) > 0:
            print(division_obj[0].id)
            raise ValidationError(
                'division already exists in this department')

        return data

    class Meta:
        model = Sub_division
        fields = ['pk', 'id', 'department', 'name', 'department_get']


# class BranchSerializer(ModelSerializer):
#     country_get = serializers.SerializerMethodField("get_country")
#     state_get = serializers.SerializerMethodField('get_state')
#     state_code = serializers.SerializerMethodField('get_state_code')


#     def get_country(self, obj):
#         if obj.country:
#             return obj.country.country_name
#         return None

#     def get_state(self, obj):
#         if obj.state:
#             return obj.state.state_name
#         return None

#     def get_state_code(self, obj):
#         if obj.state:
#             return obj.state.state_code
#     class Meta:
#         model = Branch
#         fields = ['pk', 'id', 'branch_name', 'cityname', 'state', 'state_get',
#                   'country', 'country_get', 'pincode', 'gst_number','address','state_code']
#         read_only_field = ['Branch_code']

#     def validate(self, data):
#         queryset = Branch.objects.all()
#         if self.instance:
#             id = self.instance.id
#             print(id)
#             queryset = queryset.exclude(id=id)
#         return data


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'employee_id', 'name', 'email', 'phone', 'password',
                  'department', 'department_subdivision', 'role', 'branch']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user


class UserUpdateSerializer(ModelSerializer):
    role_get = serializers.SerializerMethodField(
        "get_role")
    branch_get = serializers.SerializerMethodField("get_branch")

    def get_branch(self, obj):
        if obj.branch:
            return obj.branch.branch_name
        return None

    def get_role(self, obj):
        if obj.role:
            return obj.role.role
        return None

    class Meta:
        model = User
        fields = ['pk', 'employee_id', 'name', 'email',
                  'phone', 'role', 'role_get', 'branch', 'branch_get']


class DepartmentsSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = ['pk', 'id', 'name', 'role']


class LoginSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['employee_id', 'password']


class EmailCheckSerializer(Serializer):
    email = serializers.EmailField()

class NullSerializer(Serializer):
    pass

class ScheduleStatusSerializer(Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class ScheduleMailSerializer(Serializer):
    time = serializers.TimeField()


class ConfigurationsSerializer(ModelSerializer):
    class Meta:
        model = Configurations
        fields = ['id','configuration_details']