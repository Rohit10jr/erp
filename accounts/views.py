from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import(
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    ListAPIView)
from .models import *
from random import randint
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.core.mail import BadHeaderError, send_mail
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializer import (
    # BranchSerializer, 
    DepartmentsSerializer,
    UsersSerializer, LoginSerializer,
    UserRoleSerializer, SubDivisionSerializer,
    UserUpdateSerializer, ScheduleStatusSerializer,
    ConfigurationsSerializer, ScheduleMailSerializer,
    NullSerializer, EmailCheckSerializer, Userprofileserializer,
)
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED,
    HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST,  
    HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN,
    HTTP_206_PARTIAL_CONTENT, HTTP_203_NON_AUTHORITATIVE_INFORMATION,
)
import json
from .models import User
from rest_framework import exceptions
from rest_framework.response import Response

from django.urls import reverse
from django.middleware.csrf import _get_new_csrf_token
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_str, force_bytes, smart_bytes, DjangoUnicodeDecodeError
from io import BytesIO
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import get_template
# from xhtml2pdf.pisa import pisaDocument
from django.conf import settings
import os
import uuid
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import SimpleUploadedFile

# from data_management.forms import *
# from data_management.models import *
# from data_management.serializer import *
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .utils import data_nav
# Create your views here.


def all_unexpired_sessions_for_user(user):
    user_sessions = []
    all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in all_sessions:
        session_data = session.get_decoded()
        if user.pk == session_data.get('_auth_user_id'):
            user_sessions.append(session.pk)
    print(user_sessions, 'sessions')
    return Session.objects.filter(pk__in=user_sessions)


def delete_all_unexpired_sessions_for_user(user, session_to_omit=None):
    session_list = all_unexpired_sessions_for_user(user)
    if session_to_omit is not None:
        session_list.exclude(session_key=session_to_omit.session_key)
    session_list.delete()


class UserRegistration(ListAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def has_access(self, request):
        model_name = self.request.query_params.get('model', None)
        erp_role = self.request.user.erp_role
        access = getattr(erp_role, 'user_management')
        print(erp_role, access)
        return access

    def list(self, request):
        employee_id = request.query_params.get('employee_id')
        try:
            users = User.objects.all()
            if employee_id:
                users = users.filter(employee_id=employee_id)
                print(users)
            serializer = UserUpdateSerializer(users, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'failure', 'data': str(e)}, status=HTTP_206_PARTIAL_CONTENT)

    def post(self, request, *args, **kwargs):
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            # try:
            serializer.save()
            print(serializer.data['name'], 'data')
            return Response({"status": "success", "data": serializer.data}, status=HTTP_200_OK)
        return Response({"status": "Not Created", "data": serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)

    def update(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        data = request.data
        if pk:
            try:
                user = User.objects.get(pk=pk)
                print(user)
                if 'password' in data:
                    user.set_password(data['password'])
                    user.save()
                    del data['password']
                serializer = UserUpdateSerializer(user, data=data)
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response({"status": "updated", "data": serializer.data}, status=HTTP_200_OK)
                    except:
                        return Response({'status': 'failure', 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
                return Response({'status': 'failure', 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
            except Exception as error:
                return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
        else:
            return Response({'status': 'failure', 'data': 'give valid primary key'}, status=HTTP_206_PARTIAL_CONTENT)

# @csrf_exempt
class Login(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')
        password = request.data.get('password')
        print(employee_id, password)

        user = authenticate(
            # doubt password 
            request, employee_id=employee_id, password=password)
        # print(user.name, 'password')
        if user:
            try:
                # delete_all_unexpired_sessions_for_user(user)
                token, created = Token.objects.get_or_create(user=user)
                print(token.key)
                login(request, user)
                csrf = _get_new_csrf_token()
                request.META['CSRF_COOKIE'] = csrf
                data = {'token': token.key,
                        'id': user.employee_id,
                        'email': user.email,
                        "username":user.name,
                        'csrf_token':csrf
                        }
                print(data)
                # users = get_all_logged_in_users()
                return Response({"status": "Login Successfull", "data": data, 'code': HTTP_200_OK, }, status=HTTP_200_OK)
            except Exception as e:
                return Response({"data": str(e)}, status=HTTP_206_PARTIAL_CONTENT)
        return Response({"status": "failure", 'data': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(request.session, 'session')
        logout(request)
        # get_all_logged_in_users()
        # delete_all_unexpired_sessions_for_user(request.user)
        return Response({"status": "success", 'data': 'Logged Out'}, status=HTTP_200_OK)


class ProfileView(APIView):
    serializer_class = Userprofileserializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        serializer = Userprofileserializer(user)
        return Response({'status': 'success', 'data': serializer.data}, status=HTTP_200_OK)


class ScheduleMail(CreateAPIView):
    serializer_class = ScheduleMailSerializer
    queryset = DjangoJob.objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data
        user = self.request.user
        print(data['time'], type(data['time']))
        hour = int(data['time'][:2])
        minute = int(data['time'][3:])
        print('hour', hour, 'min', minute)
        return Response(status=HTTP_200_OK)
    

class MenuAccess(ListAPIView):
    permission_classes=[AllowAny]
    def get(self,request):
        user=request.user
        # menuaccess=user.role.access.keys() if not user.is_superuser else data_nav.keys()
        menuaccess=user.role.access.keys() if not user.is_superuser else data_nav.keys()
        menuvalues= list(user.role.access.values()) if not user.is_superuser else list(data_nav.values())
        data={}
        # print(menuaccess)
        for index,i in enumerate(menuaccess):
            menudata={key:data_nav[i][key] for key in menuvalues[index]}
            data[i]=menudata
        return Response ({"data":data})  
    

class ConfigCreateAPI(ListCreateAPIView):
    serializer_class = ConfigurationsSerializer
    queryset = Configurations.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        config = self.request.query_params.get('config', None)
        serializer_class = self.get_serializer_class()
        configs = self.get_queryset()
        if config:
            configs = configs.filter(configuration_details__has_key=config)

            if(len(configs)):
                config_to_update = configs[0]
                print('ceh',config_to_update.configuration_details[config],type(request.data['configuration_details']))
                data_for_change = json.dumps(request.data['configuration_details'])
                data_for_change = json.loads(data_for_change)

                config_to_update.configuration_details[config] = data_for_change
                # setattr(config_to_update.configuration_details,config,request.data)

                config_to_update.save()
                config_serializer = serializer_class(config_to_update)
                return Response({'status': 'success' ,'data':config_serializer.data}, status=HTTP_201_CREATED) 
        else:
            print(type(data),data['configuration_details'],'data')
            # post_data = {}
            # post_data = data['in']
            data_for_change = json.loads(data['configuration_details'])
            print(data_for_change,'data_for_change')
            config_serializer = serializer_class(data=data_for_change)
            # try:
            
            if config_serializer.is_valid():
                config_serializer.save()
                return Response({'status': 'success' ,'data':config_serializer.data}, status=HTTP_201_CREATED)
        print(config_serializer.errors,'error')