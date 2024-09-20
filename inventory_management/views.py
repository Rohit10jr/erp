from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .serializer import * 
from .models import * 
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_100_CONTINUE, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_206_PARTIAL_CONTENT, HTTP_201_CREATED,)
from django.http import JsonResponse, HttpResponse
from .models import Purchase_request, Purchase_request_items, DebitNotes
from rest_framework.permissions import AllowAny, IsAuthenticated
from data_management.models import Rawmaterials,Payments
import datetime
from accounts.models import FileUpload
from io import BytesIO
import json
from utils.utils import get_order_serial_number, order_serial_numbers
import os


class PurchaseRequestAPI(ListCreateAPIView):
    serializer_class = purchase_request_create_serializer
    permission_classes = [IsAuthenticated]
    queryset = Purchase_request.objects.all()

    def list(self, request):
        queryset = Purchase_request.objects.all()
        serializer = purchase_request_serializer(queryset, many=True)
        purchase_request_no = get_order_serial_number(
            order_serial_numbers['purchase_request'], Purchase_request, 'purchase_request_no')
        return Response({'status': 'success', 'data': serializer.data, 'purchase_request_no': purchase_request_no},
                        status=HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data, 'request_data')
        try:
            request_items = data['request_items']
            del data['request_items']
            data['expected_date_of_delivery'] = data['date_delivery_expected']
            del data['date_delivery_expected']
            del data['date']
            data['branch'] = request.user.branch.id
            data['warehouse_user_id'] = request.user.id
            pr_serializer = purchase_request_serializer(
                data=data)
            if pr_serializer.is_valid():
                pr_serializer.save()
            purchase_request = Purchase_request.objects.get(
                purchase_request_no=data['purchase_request_no'])
            PR_serializer = pr_serializer.data
            result = {}
            PRI_serializer = []
            for item_id in request_items:
                item = request_items[item_id]
                if 'measured_unit_get' in item:
                    unit = item['measured_unit_get']
                    # rm_name = item['rm_name_get']
                else:
                    unit = item['measured_unit']
                purchase_request_items = Purchase_request_items.objects.create(
                    purchase_request_no=purchase_request, rm_quantity=item[
                        'quantity'], rm_name=item['rm_name'], rm_group=item['rm_group'],
                        category = item['category'],
                    measured_unit=unit)
                serializer = purchase_request_items_serializer(
                    purchase_request_items)
                PRI_serializer.append(
                    serializer.data)
                print(item)
            result = {'purchase_request': PR_serializer,
                      'purchase_request_items': PRI_serializer}
            # result = 'sd'
        except Exception as error:
            return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
        return Response({'status': 'success', 'data': result}, status=HTTP_201_CREATED)
    

class InventoryTransferAPI(ListCreateAPIView):
    # serializer_class = Inventory_transfer
    permission_classes = [IsAuthenticated]
    serializer_class = transfer_requests_serializer
    queryset = Transfer_requests.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Transfer_requests.objects.all()
        today = datetime.datetime.today()
        year = int(str(today.year)[2:])
        month = today.month
        year_str = ''
        if month < 4:
            year_str += '{}-{}'.format(str(year-1), str(year))
        else:
            year_str += '{}-{}'.format(str(year), str(year+1))
        queryset = self.get_queryset()
        check_str_jw = 'JW/'+year_str
        check_str_it = 'IT/'+year_str
        last_obj_jw = (Transfer_requests.objects.filter(
            request_id__contains=check_str_jw).order_by('id')).last()
        last_obj_it = (Transfer_requests.objects.filter(
            request_id__contains=check_str_it).order_by('id')).last()
        last_number_jw = 1
        last_number_it = 1
        if last_obj_jw:
            last_number_jw = int(last_obj_jw.request_id[11:])+1
        if last_obj_it:
            last_number_it = int(last_obj_it.request_id[11:])+1
        jobwork_no = 'SHJW/'+year_str+'/'+str(last_number_jw)
        internal_transfer_no = 'SHIT/'+year_str+'/'+str(last_number_it)
        serializer = transfer_requests_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data, 'internal-transfer': internal_transfer_no, 'jobwork': jobwork_no})
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = transfer_requests_serializer(data=data)
        from_party = None
        if (request.user.branch):
            from_party = request.user.branch.id
        data['from_party'] = from_party
        for item_id in data['request_details']:
            item = data['request_details'][item_id]
            try:
                if item['category'] == 'Semi-Finished Goods':
                    inventory = Inventory_product.objects.filter(
                        warehouse_name_id=from_party, product_name=item['rm_name_get'])
                    print(inventory, 'inventory')
                    if len(inventory):
                        inventory = inventory[0]
                    inventory.product_stock -= int(item['quantity'])
                    inventory.save()
                else:
                    inventory = Inventory_rawmaterial.objects.filter(
                        warehouse_name_id=from_party, rm_name=item['rm_name_get'])
                    print(inventory, 'inventory')
                    if len(inventory):
                        inventory = inventory[0]
                    inventory.rm_stock -= int(item['quantity'])
                    inventory.save()
            except:
                continue
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data})
        return Response({'status': 'success', 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)


class DebitNotesAPI(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DebitNoteSerializer
    queryset = DebitNotes.objects.all()

    def list(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        queryset = self.get_queryset()
        debit_note_number = get_order_serial_number(
            order_serial_numbers['debit_note'], DebitNotes, 'debit_note_no')
        try:
            if pk:
                queryset = DebitNotes.objects.get(debit_note_no=pk)
                data = DebitNoteSerializer(queryset)
            else:
                data = DebitNoteSerializer(queryset, many=True)
        except Exception as error:
            return Response({'status': 'failure', 'data': str(error)}, status=HTTP_200_OK)
        return Response({'status': 'success', 'data': data.data, 'debit_note_no': debit_note_number}, status=HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            user_branch = request.user.branch
            data['warehouse_id'] = user_branch.id
            if data['debit_note_no'] == None:
                debit_note_no = get_order_serial_number(
                    order_serial_numbers['debit_note'], Purchase_request, 'debit_note_no')
                data['debit_note_no'] = debit_note_no
            serializer = DebitNoteSerializer(data=data)
            for item in data['debit_items']:
                debit_item = data['debit_items'][item]
                debit_item_quantity = int(debit_item['rm_quantity'])
                try:
                    if debit_item['rm_type'] == 'Product':
                        inventory = Inventory_product.objects.filter(
                            warehouse_name=user_branch, product=debit_item['rm_name'])[0]
                        inventory.product_stock = inventory.product_stock - debit_item_quantity
                        inventory.save()
                    else:
                        inventory = Inventory_rawmaterial.objects.filter(
                            warehouse_name=user_branch, rm=debit_item['rm_name'])[0]
                        inventory.rm_stock = inventory.rm_stock - debit_item_quantity
                        inventory.save()
                except:
                    pass
                try:
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'status': 'success', 'data': serializer.data}, status=HTTP_201_CREATED)
                    return Response({'status': 'failure', 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
                except:
                    return Response({'status': 'failure', 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
            return Response({'status': 'success', 'data': 'error'}, status=HTTP_200_OK)
        except Exception as error:
            return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)


class InventoryDetailsAPI(CreateAPIView):
    Permission_classes = [AllowAny]
    serializer_class = InventoryDetailsSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        inventory_data = []
        # data = json.loads(data)
        warehouse = request.user.branch.id
        print(data['list_of_goods'],'he')
        for element in data['list_of_goods']:
            print(element,'elemetn')
            try:
                inventory = 0
                if element['category'] == 'Semi-Finished goods':
                    inventory = Inventory_product.objects.get(
                        product_name__iexact=element['name'], warehouse_name=warehouse).product_stock
                else:
                    inventory = Inventory_rawmaterial.objects.get(
                        rm_name__iexact=element['name'], warehouse_name=warehouse).rm_stock
                    # print('name',inventory.rm_name)
            except:
                inventory = 0
            inventory_data.append({'category': element['category'],
                                   'name': element['name'], 'stock': inventory})
        return Response({'status': 'success', 'data': inventory_data}, status=HTTP_200_OK)
        

class InventoryUpdate(CreateAPIView):
    Permission_classes = [AllowAny]
    serializer_class = Inventory_rm_serializer

    def patch(self, request, *args, **kwargs):
        data = request.data
        pk = request.query_params.get('pk')
        print(pk,'pk')
        try:   
            raw_material = Rawmaterials.objects.get(id=pk)
            if request.user.branch:
                raw_material_inventory= Inventory_rawmaterial.objects.filter(rm_name=raw_material.rm_name,warehouse_name=request.user.branch.id)
                if len(raw_material_inventory) > 0:
                    raw_material_inventory[0].rm_stock = raw_material_inventory[0].rm_stock - int(data['quantity_released_to_production'])
                else:
                    return Response({'status': 'failure', 'data': 'check your inventory data'}, status=HTTP_206_PARTIAL_CONTENT)
        except Exception as error:
            return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
        rm_inventory_serializer = Inventory_rm_serializer(raw_material_inventory[0])
        return Response({'status': 'success', 'data': rm_inventory_serializer.data}, status=HTTP_200_OK)


class FileUploadAPI(CreateAPIView):
    serializer_class = FileUploadSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        time = str(datetime.datetime.now())
        file_name = 'attached_document_{}'.format(time)
        # print(data,'dats',data['document_attached'].name)
        if(type(data['document_attached'])!= str):
            name, extension = os.path.splitext(data['document_attached'].name)
            print(extension,'hy',data['document_attached'])
            bytesIO_obj = BytesIO(data['document_attached'].read())
            bytes_obj = bytesIO_obj.read()
            file_obj = FileUpload.objects.create(file=bytes_obj,file_name=file_name,file_type=extension)       
            return Response({'status':'success','file_name':file_obj.id},status=HTTP_200_OK)
        return Response({'status':'success','file_name':None},status=HTTP_200_OK)