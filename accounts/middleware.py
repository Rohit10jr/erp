from accounts.utils import hasaccess
from functools import reduce
import operator
from rest_framework.response import Response
from django.http import JsonResponse


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        user,useraccess=request.user,reduce(operator.concat,list(request.user.role.access.values()))
        response = self.get_response(request)
        print(response)
        print('REQUEST METHOD',bool(not request.GET),request.method,request.GET.get('model'))
        print(request.method != 'GET' ,request.GET.get('model' and bool(request.GET.get('model') in useraccess)) , user.is_superuser)
        if request.method != 'GET'  and request.GET.get('model' and bool(request.GET.get('model') in useraccess)) or user.is_superuser:
        #    print('request satisfied',response.data)
        # Code to be executed for each request/response after
        # the view is called.
           return response
        if not request.GET.get('model') or bool(request.GET):
            return response
        
        return JsonResponse({"status": "failure","message":"You dont have permission"}, status=400)
