from django.shortcuts import render
from accounts.utils import hasaccess
import datetime
from django.db.models import Sum
from accounts.serializer import * 

from accounts.models import Branch
from .models import * 
import json 
from .forms import *
from .utils import Paginate, model_data, model_for_dropdown, status_for_filter_not_include,titles_for_tables
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .forms import *

from django.db.models import F
from django.http import JsonResponse, HttpResponse
from utils.utils import ResponseChoices
from rest_framework.permissions import AllowAny, IsAdminUser, BasePermission, IsAuthenticated
from rest_framework.status import (
    HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_206_PARTIAL_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_203_NON_AUTHORITATIVE_INFORMATION, HTTP_206_PARTIAL_CONTENT,
    HTTP_403_FORBIDDEN
)
from django.shortcuts import render
from .serializer import *
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListAPIView,
)

# from purchase_management.models import Purchase_order,PurchaseOrderItems
# from sales_management.models import Sales_order,Delivery_note,Sales_order_items
# from inventory_management.models import Inventory_product,Inventory_rawmaterial,Transfer_requests,GRN
# from production_management.models import ProductionBOM,ProductionManagement,MaterialRequest,ProductivityManagement
# from sales_management.serializer import sales_order_serializer,delivery_note_serializer,sales_order_report_serializer
# from inventory_management.serializer import Inventory_product_serializer,Inventory_rm_serializer,transfer_requests_serializer,GRNSerializer
# from purchase_management.serializer import PurchaseOrderSerializer,PurchaseReportSerializer
# from production_management.serializer import ProductionBOMserializer,ProductionManagementSerializer,MaterialRequestSerializer,ProductivityManagementSerializer
# Create your views here.





class CRUDAPI(ListAPIView, RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NullSerializer
    pagination_class = Paginate

    def get_serializer_class(self, *args, **kwargs):
        model_name = self.request.query_params.get('model', None)
        if model_name and model_name in model_data:
            model = model_data[model_name]
            return model['serializer']
        return self.serializer_class
    
    def get_table(self):
        model_name = self.request.query_params.get('model', None)
        if model_name and model_name in model_data:
            model = model_data[model_name]
            return model['model']
        return None
    
    def get_queryset(self):
        pk = self.request.query_params.get('pk', None)
        filter_by = self.request.query_params.get('filter_by', None)
        filter_value = self.request.query_params.get('filter_value', None)
        my_filter = {}
        if filter_value and filter_by:
            filter_value = filter_value.split(',')
            filter_by = filter_by.split(',')
            for i in range(0, len(filter_by)):
                print(filter_by[i], filter_value[i])
                my_filter[filter_by[i]] = filter_value[i]
        table = self.get_table()
        if table:
            queryset = table.objects.all()
            if pk:
                print(pk)
                return table.objects.get(pk=pk)
            if filter_by and filter_value:
                queryset = queryset.filter(**my_filter)
                print(queryset)
            return queryset
        return None
    
    def get(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        page = self.request.query_params.get('page', None)
        write = False
        try:
            serializer_class = self.get_serializer_class()
            if serializer_class == NullSerializer:
                return Response({"status": ResponseChoices.FAILURE, "data": ResponseChoices.NOT_VALID_MODEL},
                                status=HTTP_206_PARTIAL_CONTENT)
            queryset = self.get_queryset()
            if pk:
                serializer = serializer_class(queryset)
            else:
                serializer = serializer_class(queryset, many=True)
        except Exception as e:
            return Response({"status": ResponseChoices.FAILURE, 'data': str(e)}, status=HTTP_206_PARTIAL_CONTENT)
        if pk:
            return Response(serializer.data, status=HTTP_200_OK)
        return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data, 'write': write}, status=HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer_class = self.get_serializer_class()
        if serializer_class == NullSerializer:
            return Response({"status": ResponseChoices.FAILURE, "data": ResponseChoices.NOT_VALID_MODEL}, status=HTTP_206_PARTIAL_CONTENT)
        if serializer_class == BillOfMaterialsSerializer:
            if 'measured_unit' in data:
                # data['measured_unit'] = MeasuredUnits.objects.get(id=data['measured_unit']).id
                # del data['measured_unit']
                del data['measured_unit_get']
        serializer = serializer_class(data=data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": ResponseChoices.SUCCESS, "data": serializer.data}, status=HTTP_201_CREATED)
        return Response({"status": ResponseChoices.FAILURE, 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
    
    def update(self, request):
        pk = self.request.query_params.get('pk')
        data = request.data
        print(data, 'ddat')
        try:
            table = self.get_table()
            if table:
                if pk:
                    obj = table.objects.get(pk=pk)
                    primary_key = table._meta.pk.name
                    print(table, pk, obj, 'table')
                    serializer_class = self.get_serializer_class()
                    serializer = serializer_class(obj, data=data)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                            return Response({'status': ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_200_OK)
                        except Exception as e:
                            return Response({'status': ResponseChoices.FAILURE, 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
                    return Response({'status': ResponseChoices.SUCCESS, 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
            return Response({'status': ResponseChoices.SUCCESS, 'data': 'check primary key and model name'}, status=HTTP_206_PARTIAL_CONTENT)
        except Exception as e:
            return Response({'status': ResponseChoices.FAILURE, 'data': str(e)}, status=HTTP_206_PARTIAL_CONTENT)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_queryset()
        self.perform_destroy(instance)
        return Response(status=HTTP_200_OK)


class ProductionFlowView(APIView):
    serializer_class = PFSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        production_flow = None
        product = Product.objects.get(pk=data['product_code'])
        # if product.multiple_parts:
        for part_name in product.parts:
            try:
                production_flow = ProductionFlow.objects.get(
                    product_code=product, part_name=part_name)
            except:
                production_flow = ProductionFlow.objects.create(
                    product_code=product, part_name=part_name)
            try:
                productivity_list = Productivity.objects.filter(
                    product=product, part_name=part_name)
                print(productivity_list, part_name)
                phases = {}
                count = 1
                for productivity in productivity_list:
                    phases[count] = productivity.phase.phase_name
                    count += 1
                production_flow.phases = phases
                production_flow.save()
            except:
                continue
        return Response({'status': 'success' }, status=HTTP_200_OK)
    

class PreferredSuppliersGETAPI(APIView):
    serializer_class =PreferredSuppliersGETSerializer

    def post(self, request, *args, **kwargs):
        rm_list = request.data['rm_list']
        supplier_list = []
        for raw_material in rm_list:
            try:
                raw_material_obj = Rawmaterials.objects.get(id=raw_material)
                if len(raw_material_obj.preferred_supplier):
                    for supplier in raw_material_obj.preferred_supplier:
                        supplier_obj = Parties.objects.get(party_name__iexact=supplier)
                        if supplier_obj not in supplier_list:
                            supplier_list.append(supplier_obj)
            except:
                continue   
        suppliers = Parties.objects.filter(party_category__iexact='Supplier').exclude(id__in=rm_list)
        html = '<option disabled selected value="">Parties</option>'
        object_list = {}
        for supplier in supplier_list:
            html += '<option value="{}">{}</option>'.format(supplier.id,supplier.party_name)
            object_list[supplier.id] = PartiesSerializer(supplier).data
        for supplier in suppliers:
            html += '<option value="{}">{}</option>'.format(supplier.id,supplier.party_name)
            object_list[supplier.id] = PartiesSerializer(supplier).data
        return Response({'status': 'success','html':html,'object_list':object_list }, status=HTTP_200_OK)
    

# def DropdownView(request):
#     model = request.GET.get('model', None)
#     model_str = model
#     name = request.GET.get('name', None)
#     filter_by = request.GET.get('filter_by', None)
#     filter_value = request.GET.get('filter_value', None)
#     remove_own_branch = request.GET.get('remove_own_branch', None)
#     options_title = request.GET.get('options_title', None)
#     id = request.GET.get('id', 'id')
#     field_name = request.GET.get('value_field', None)
#     filter_dict = {}
#     print(options_title, 'das')
#     filter_dict[filter_by] = filter_value
#     order_by = request.GET.get('order_by', None)
#     objects = None
#     data_list = []
#     dropdown_html = ''
#     if model:
#         if not name:
#             name = model_for_dropdown[model.lower()]
#         if options_title:
#             dropdown_html = '<option selected disabled value="" >Select {}</option>'.format(
#                 options_title
#             )
#         else:
#             dropdown_html = '<option selected disabled value="" >Select {}</option>'.format(
#                 titles_for_tables[model]
#             )
#         serializer = model_data[model.lower()]['serializer']
#         table = model_data[model.lower()]['model']
#         print('model', model)
#         objects = table.objects.all()
#         print(request.user.branch,request.user.branch,'user_branch')
#         if model == Branch and remove_own_branch and request.user.branch.id:
#             objects = Branch.objects.exclude(id=request.user.branch.id)
#         if order_by:
#             objects = objects.order_by(order_by)
#         if model_str in status_for_filter_not_include:
#             objects = objects.exclude(status__in=status_for_filter_not_include[model_str])
#         if model_str == 'transfer_request' and request.user.branch:
#             if filter_value == 'Internal-Transfer':
#                 objects = objects.filter(to_party=request.user.branch.id)
#             else:
#                 objects = objects.filter(from_party=request.user.branch.id)

#         object_list = {}
#         if filter_by:
#             print(filter_by, filter_value)
#             if filter_value:
#                 objects = objects.filter(**filter_dict)
#             else:
#                 return
#         if table == Purchase_order:
#             objects = Purchase_order.objects.filter(status__in=['New','Partially Completed'])
#         if len(objects):
#             for data in objects:
#                 # print(data, 'filter')
#                 # print(name, 'da')
#                 if field_name:
#                     value_field_data = getattr(data, field_name)
#                     # print(value_field_data)
#                     object_list[value_field_data] = serializer(data).data
#                 else:
#                     object_list[data.pk] = serializer(data).data
#                 current_data = {'id': data.pk,
#                                 'name': getattr(data, name).title()}
#                 if table == Currency:
#                     current_data['code'] = getattr(data, 'currency_code')
#                 data_list.append(
#                     current_data)
#                 if (field_name):
#                     dropdown_html += f"<option value='{getattr(data,field_name)}'>{getattr(data,name).title()}</option>"
#                 else:
#                     dropdown_html += f"<option value='{data.pk}'>{getattr(data,name).title()}</option>"

#         return JsonResponse({'list': data_list, 'html': dropdown_html, 'object_list': object_list})
#     return JsonResponse({'data':"give a model name"})
