from django.shortcuts import render
from .serializer import *
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView)
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.status import (HTTP_100_CONTINUE,HTTP_200_OK,HTTP_400_BAD_REQUEST,HTTP_206_PARTIAL_CONTENT,HTTP_201_CREATED)
from django.http import JsonResponse, HttpResponse
from purchase_management.models import Purchase_inquiry, Purchase_order, PurchaseOrderItems, Purchase_inquiry_items
from purchase_management.serializer import PurchaseOrderCreateSerializer, PurchaseOrderItemsSerializer, PurchaseOrderSerializer
import datetime
from data_management.models import Parties
from django.db.models import Q
from utils.utils import get_order_serial_number, order_serial_numbers
# from inventory_management.models import Purchase_request_items, Purchase_request


class PurchaseOrderView(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseOrderCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Purchase_order.objects.all()

    def list(self, request):
        queryset = Purchase_order.objects.all()
        serializer = PurchaseOrderSerializer(queryset, many=True)
        purchase_order_number = self.request.query_params.get(
            'purchase_order_no', None)
        print(purchase_order_number)
        if purchase_order_number:
            try:
                current_purchase_order = Purchase_order.objects.get(
                    purchase_order_no=purchase_order_number)
                print(current_purchase_order)
                serializer = PurchaseOrderSerializer(current_purchase_order)
            except:
                return Response({'status': 'failure', 'data': 'give a valid purchase order no'})
        # purchase_order_no = get_order_serial_number(
        #     'SHPL', Purchase_order, 'purchase_order_no')
        purchase_order_no = get_order_serial_number(
            order_serial_numbers['purchase_order'], Purchase_order, 'purchase_order_no')
        return Response({'status': 'success', 'data': serializer.data, 'purchase_order_no': purchase_order_no}, status=HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        if 'supplier' in data:
            supplier = Parties.objects.get(id=data['supplier'])
        print('purchase_order_no' in data)
        if not 'purchase_order_no' in data:
            print('purchase_order_no' in data, 'yes')
            queryset = self.get_queryset()
            data['purchase_order_no'] = get_order_serial_number(
                order_serial_numbers['purchase_order'], Purchase_order, 'purchase_order_no')
        purchase_order = Purchase_order.objects.create(
            procurement_user_id=self.request.user, po_date=data[
                'po_date'], purchase_order_no=data['purchase_order_no'],
            expected_date_receipt=data['expected_date_receipt'], due_date=data['due_date'],
            supplier_id_id=data['supplier'],
            freight_charges_paid_by=data['freight_charges_paid_by'],
            payment_terms=data['payment_terms'], total_price=data['total_price'], delivery_at=data[
                'delivery_at'], comments=data['comments'], status=data['status']
        )
        print('dfastra')
        PR_serializer = PurchaseOrderSerializer(purchase_order)
        PR_serializer = PR_serializer.data
        result = {}
        PRI_serializer = []
        purchase_request_no = None
        print(data['order_items'])
        for item_id in data['order_items']:
            item = data['order_items'][item_id]
            if bool(item):
                if 'purchase_request_no' in data:
                    request_item = Purchase_request_items.objects.get(id=item_id)
                    purchase_request_no = request_item.purchase_request_no
                    request_item.purchase_order_no = purchase_order.id
                    request_item.save()
                
                print(item,'sd')
                if (item['category']).lower() != 'semi-finished goods':
                    raw_material = Rawmaterials.objects.get(id=item['rm_name'])
                    print(float(item['rm_unitprice']),'price')
                    raw_material.last_purchase_price = float(item['rm_unitprice'])
                    raw_material.save()
                else:
                    raw_material = Product.objects.get(id=item['rm_name'])
                if 'measured_unit_get' in item:
                    unit = item['measured_unit_get']
                    product_name = item['rm_name']
                else:
                    unit = item['measured_unit']
                    product_name = item['rm_name']
                cgst =0
                igst =0 
                sgst = 0
                gst = 0
                total_price = float(item['rm_total_cost'])
                if supplier.party_country:
                    if (supplier.party_country.country_name).lower() == 'india':
                        if request.user:
                            if (supplier.party_state.state_name).lower() == (request.user.branch.state.state_name).lower:
                                cgst = total_price * (float(raw_material.cgst)/100)
                                sgst = total_price * (float(raw_material.sgst)/100)
                                gst = int(raw_material.cgst) + int(raw_material.sgst)
                            else:
                                igst = total_price * (float(raw_material.igst)/100)
                                gst = int(raw_material.igst)
                purchase_order_items = PurchaseOrderItems.objects.create(
                    purchase_order_no=purchase_order, rm_quantity=item['rm_quantity'], rm_unitprice=item['rm_unitprice'], currency_id=item[
                        'currency'], rm_total_cost=item['rm_total_cost'], rm_name=product_name, rm_group=item['rm_group'],category=item['category'],
                    sgst=sgst,igst=igst,cgst=cgst,gst=gst,
                    measured_unit=unit)
                serializer = PurchaseOrderItemsSerializer(
                    purchase_order_items)
                PRI_serializer.append(
                    serializer.data)
                print(item)
        if purchase_request_no:
            purchase_request = Purchase_request.objects.filter(
                purchase_request_no=purchase_request_no)[0]
            purchase_request_items = Purchase_request_items.objects.filter(
                purchase_request_no=purchase_request_no)
            completed_flag = True
            for request_item in purchase_request_items:
                if request_item.purchase_order_no == None or request_item.purchase_order_no == '':
                    completed_flag = False
            if completed_flag:
                purchase_request.status = 'Completed'
                purchase_request.save()

        result = {'Purchase_order': PR_serializer,
                  'Purchase_order_items': PRI_serializer}
        # except Exception as error:
        #     return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
        return Response({'status': 'success', 'data': result}, status=HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        action = self.request.query_params.get('action', None)
        data = request.data
        if pk:
            purchase_order = Purchase_order.objects.get(id=pk)
            if action:
                if action == 'approve':
                    purchase_order.status = 'New'
                    purchase_order.save()
                elif action == 'reject':
                    purchase_order.reject_comments = data['reject_comments']
                    purchase_order.status = 'Rejected'
                    purchase_order.save()
                elif action == 'update':
                    purchase_order = Purchase_order.objects.filter(pk=pk).update(procurement_user_id=self.request.user,
                                                                                 expected_date_receipt=data[
                                                                                     'expected_date_receipt'], due_date=data['due_date'],
                                                                                 supplier_id_id=data['supplier'],
                                                                                 freight_charges_paid_by=data[
                                                                                     'freight_charges_paid_by'],
                                                                                 payment_terms=data['payment_terms'], total_price=data['total_price'], delivery_at=data['delivery_at'], comments=data['comments'], status=data['status'])
                    purchase_order = Purchase_order.objects.get(pk=pk)
                    PO_serializer = PurchaseOrderSerializer(
                        purchase_order).data
                    print('jos')
                    POI_serializer = []
                    try:
                        for item_id in data['order_items_for_edit']:
                            item = data['order_items_for_edit'][item_id]
                            if 'measured_unit_get' in item:
                                unit = item['measured_unit_get']
                                product_name = item['rm_name']
                            else:
                                unit = item['measured_unit']
                                product_name = item['rm_name']
                            purchase_order_item = PurchaseOrderItems.objects.filter(pk=item_id, purchase_order_no=purchase_order).update(
                                rm_quantity=item['rm_quantity'], rm_unitprice=item['rm_unitprice'], currency_id=item[
                                    'currency'], rm_total_cost=item['rm_total_cost'], rm_name=product_name,  rm_group=item['rm_group'],category=item['category'],
                                measured_unit=unit)
                            print(item_id, 'id')
                            purchase_order_item = PurchaseOrderItems.objects.get(
                                id=item_id)
                            serializer = PurchaseOrderItemsSerializer(
                                purchase_order_item)
                            POI_serializer.append(
                                serializer.data)
                            print(item)
                        for item_id in data['order_items']:
                            # print(, 'items')
                            item = data['order_items'][item_id]
                            if 'measured_unit_get' in item:
                                unit = item['measured_unit_get']
                                product_name = item['rm_name']
                            else:
                                unit = item['measured_unit']
                                product_name = item['rm_name']
                            purchase_order_item = PurchaseOrderItems.objects.create(
                                purchase_order_no=purchase_order,
                                rm_quantity=item['rm_quantity'], rm_unitprice=item['rm_unitprice'], currency_id=item[
                                    'currency'], rm_total_cost=item['rm_total_cost'], rm_name=product_name, rm_group=item['rm_group'],category=item['category'],
                                measured_unit=unit)
                            serializer = PurchaseOrderItemsSerializer(
                                purchase_order_item)
                            POI_serializer.append(
                                serializer.data)
                            print(item)
                        for item_id in data['order_items_to_delete']:
                            purchase_order_item = PurchaseOrderItems.objects.get(
                                pk=item_id)
                            purchase_order_item.delete()
                        result = {'sales_order': PO_serializer,
                                  'sales_order_items': POI_serializer}
                        return Response({'status': 'success', 'data': result}, status=HTTP_201_CREATED)
                    except Exception as error:
                        return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
            serializer = PurchaseOrderSerializer(purchase_order)
            return Response({'status': 'success', 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({'status': 'failure', 'data': 'select or choose any items'}, status=HTTP_206_PARTIAL_CONTENT)
    

class PurchaseInquiryView(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseInquiryCreateSerializer
    permission_classes = [AllowAny]
    queryset = Purchase_inquiry.objects.all()

    def list(self, request):
        queryset = Purchase_inquiry.objects.filter(
            ~Q(status='Cancelled') & ~Q(status='Rejected') & ~Q(status='Completed') & ~Q(status='Closed'))
        print(queryset,'query')
        serializer = PurchaseInquirySerializer(queryset, many=True)
        purchase_inquiry_no = get_order_serial_number(
            order_serial_numbers['purchase_inquiry'], Purchase_inquiry, 'purchase_inquiry_no')

        return Response({'status': 'success', 'data': serializer.data, 'purchase_inquiry_no': purchase_inquiry_no}, status=HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        # try:
        print('purchase_inquiry_no' in data)
        if not 'purchase_inquiry_no' in data:
            print('purchase_inquiry_no' in data, 'yes')
            today = datetime.datetime.today()
            year = int(str(today.year)[2:])
            month = today.month
            year_str = ''
            if month < 4:
                year_str += '{}-{}'.format(str(year-1), str(year))
            else:
                year_str += '{}-{}'.format(str(year), str(year+1))
            queryset = self.get_queryset()
            last_obj = (Purchase_inquiry.objects.filter(
                purchase_inquiry_no__contains=year_str).order_by('id')).last()
            last_number = 1
            if last_obj:
                last_number = int(last_obj.purchase_inquiry_no[11:])+1
            data['purchase_inquiry_no'] = 'SHPI/'+year_str+'/'+str(last_number)
        purchase_inquiry = Purchase_inquiry.objects.create(
            procurement_user_id=self.request.user, po_date=data[
                'po_date'], purchase_inquiry_no=data['purchase_inquiry_no'],
            expected_date_receipt=data['expected_date_receipt'], due_date=data['due_date'],
            supplier_id_id=data['supplier'],
            freight_charges_paid_by=data['freight_charges_paid_by'],
            payment_terms=data['payment_terms'], total_price=data['total_price'], comments=data['comments'], status=data['status']
        )
        print('dfastra')
        PR_serializer = PurchaseInquirySerializer(purchase_inquiry)
        PR_serializer = PR_serializer.data
        # print('jos')
        result = {}
        PRI_serializer = []
        for item_id in data['inquiry_items']:
            if ('purchase_request_no' in data and data['purchase_request_no'] != '' and data['purchase_request_no'] != None
                    and data['issue_for_request']):
                request_item = Purchase_request_items.objects.get(id=item_id)
                request_item.purchase_inquiry_no.append(purchase_inquiry.id)
                request_item.save()
            item = data['inquiry_items'][item_id]
            if 'measured_unit_get' in item:
                unit = item['measured_unit_get']
                product_name = item['rm_name']
            else:
                unit = item['measured_unit']
                product_name = item['rm_name']
            print('rm_unitprice' in item, 'check')
            if not 'rm_unitprice' in item:
                item_unit_price = None
                item_total_cost = None
                item_currency = None
                print(item, 'after')
            else:
                item_unit_price = item['rm_unitprice']
                item_total_cost = item['rm_total_cost']
                item_currency = item['currency']
            print(item)
           
            purchase_inquiry_items = Purchase_inquiry_items.objects.create(
                purchase_inquiry_no=purchase_inquiry, rm_quantity=item[
                    'rm_quantity'], rm_unitprice=item_unit_price, currency_id=item_currency, rm_total_cost=item_total_cost, rm_name=product_name, rm_group=item['rm_group'],category=item['category'],
                measured_unit=unit)
            serializer = PurchaseInquiryItemsSerializer(
                purchase_inquiry_items)
            PRI_serializer.append(
                serializer.data)
            
            print(item)
        result = {'Purchase_inquiry': PR_serializer,
                  'Purchase_inquiry_items': PRI_serializer}
        return Response({'status': 'success', 'data': result}, status=HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        pk = self.request.query_params.get('pk', None)
        action = self.request.query_params.get('action', None)
        data = request.data
        if pk:
            purchase_inquiry = Purchase_inquiry.objects.get(id=pk)
            if action:
                if action == 'approve':
                    purchase_inquiry.status = 'New'
                elif action == 'reject':
                    purchase_inquiry.status = 'Rejected'
                elif action == 'cancel':
                    purchase_inquiry.status = 'Cancelled'
                elif action == 'update':
                    purchase_inquiry.comments = data['comments']
                elif action == 'closed':
                    purchase_inquiry.status = 'Closed'
                purchase_inquiry.save()
            serializer = PurchaseInquirySerializer(purchase_inquiry)
            return Response({'status': 'success', 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({'status': 'failure', 'data': 'select or choose any items'}, status=HTTP_206_PARTIAL_CONTENT)