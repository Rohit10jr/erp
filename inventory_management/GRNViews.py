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
from rest_framework.permissions import AllowAny,IsAuthenticated
from data_management.models import Rawmaterials,Payments
import datetime
import json
from utils.utils import get_order_serial_number, order_serial_numbers


class GRNCreateAPI(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = GRN.objects.all()
    serializer_class = GRNCreateSeriliazer

    def list(self, request):
        pk = self.request.query_params.get('pk', None)
        filter_value = self.request.query_params.get('filter',None)
        queryset = self.get_queryset()
        if filter_value == 'Pending Payments':
            queryset = queryset.filter(pending_amount__gt=0,order_type__in=['Supplier','Misc'])
        # year = str(datetime.)
        grn_no = get_order_serial_number(
            order_serial_numbers['grn'], GRN, 'grn_no')
        try:
            if pk:
                queryset = GRN.objects.get(sales_order_no=pk)
                data = GRNSerializer(queryset)
            else:
                data = GRNSerializer(queryset, many=True)
        except Exception as error:
            return Response({'status': 'failure', 'data': str(error)}, status=HTTP_200_OK)
        return Response({'status': 'success', 'data': data.data, 'grn-no': grn_no}, status=HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        data = request.data
        pk = request.query_params.get('id')
        try:
            print(pk)
            grn = GRN.objects.get(pk=pk)
            Payment = Payments.objects.create(invoice_number=data['grn_no'],payment_date=data['payment_date'],
                                            payment_type = 'Debit',amount_paid=data['paid_amount'],
                                            party_id=data['grn_received_from'],payment_mode_id=data['payment_mode'],
                                            currency = grn.currency
                                            )
            print()
            grn.total_amount_paid = float(grn.total_amount_paid)+ float(data['paid_amount'])
            grn.pending_amount = float(grn.pending_amount) - float(data['paid_amount'])
            grn.save()
            grn_serializer = GRNSerializer(grn)
            return Response({'status': 'success', 'data': grn_serializer.data}, status=HTTP_200_OK)
        except Exception as error:
            return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
        
    def post(self, request, *args, **kwargs):

        data = request.data
        # print(data, 'data')
        # try:
        warehouse = request.user.branch.id
        order_type = data['order_type']
        data['pending_amount'] = 0
        if (order_type == 'Internal Transfer' or order_type == 'Jobwork'):
            if order_type == 'Jobwork':
                data['pending_amount'] = data['jobwork_invoice_total']
            transfer_request = Transfer_requests.objects.get(
                id=data['order_no'])
        elif order_type == 'Supplier':
            purchase_order = Purchase_order.objects.get(
                id=data['order_no'])
            data['pending_amount'] = data['grand_total']
        transfer_completed = 'Completed'
        if 'currency' in data and data['currency']:
            currency = Currency.objects.get(id=data['currency'])
            data['currency_id'] = currency.id
        grn_items = data['grn_items']
        del data['grn_items']
        del data['goods_receipts_no']
        del data['goods_received_form']
        del data['goods_receipts_date']
        data['grn_received_from'] = data['received_from']
        del data['received_from']
        data['warehouse_id'] = warehouse
        data['grand_total_price'] = data['grand_total']
        data['pending_amount'] = data['grand_total']
        del data['grand_total']
        if 'date_delivery_expected' in data:
            data['due_date'] = data['date_delivery_expected']
        grn_serializer = GRNSerializer(data=data)

        try:
            if grn_serializer.is_valid():
                grn_serializer.save()
        except:
            return Response({'data':grn_serializer.errors},status=HTTP_206_PARTIAL_CONTENT)
        print(grn_serializer.errors,'check')
        grn = GRN.objects.filter(grn_no=data['grn_no'])[0]

# jwi,
        GRN_serializer = grn_serializer.data
        GRNI_serializer = []
    # try:
        for item_id in grn_items:
            item = grn_items[item_id]
            if 'rm_name_get' in item:
                product = item['rm_name_get']
            else:
                product = item['product_name']
            if order_type == 'Jobwork':
                item['category'] = item['product_type']
                item['rm_group'] = None
            received_quantity_actual = int(item['quantity_received'])
            grn_item = GRN_items.objects.create(
                grn=grn,category=item['category'],rm_group=item['rm_group'], rm_name=product,
                ordered_quantity=item['quantity'], unit_price=item['unit_price'], actual_unit_price=item['actual_unitprice'],
                sgst=item['SGST'], cgst=item['CGST'], igst=item['IGST'], total_price_with_gst=item['total_price'],
                currency_id=item['currency_id'], measurement_unit=item['measured_unit'],
                received_quantity=item['quantity_received'],gst=item['gst']
            )
            # try:
            if item['category'] == 'Semi-Finished Goods' or item['category'] == 'Misc':
                print(product)
                inventory = Inventory_product.objects.filter(
                    warehouse_name=warehouse, product_name__iexact=product)
                if len(inventory):
                    inventory = inventory[0]
                    print(inventory.product_stock,'before')
                    inventory.product_stock += received_quantity_actual
                    inventory.save()
                    print(inventory.product_stock,'after')
            else:
                inventory = Inventory_rawmaterial.objects.filter(
                        warehouse_name=warehouse, rm_name__iexact=product)
                if len(inventory):
                    inventory = inventory[0]
                    inventory.rm_stock += received_quantity_actual
                    inventory.save()

            if order_type == 'Internal Transfer':
                print(item, ';s')
                transfer_request.request_details[item_id]['quantity_received'] = int(
                    item['quantity_received'])
                transfer_request.request_details[item_id]['quantity_yet_to_receive'] = int(
                    item['quantity_yet_to_receive']) - int(item['quantity_received'])
                print(
                    transfer_request.request_details[item_id]['quantity_yet_to_receive'], 'ds')
                if transfer_request.request_details[item_id]['quantity_yet_to_receive'] != 0:
                    transfer_completed = 'Partially Completed'

            elif order_type == 'Jobwork':
                if 'quantity_received' not in transfer_request.jobwork_details[item_id]:
                    transfer_request.jobwork_details[item_id]['quantity_received'] = 0
                if 'quantity_yet_to_receive' not in transfer_request.jobwork_details[item_id]:
                    transfer_request.jobwork_details[item_id]['quantity_yet_to_receive'] = item['quantity']
                transfer_request.jobwork_details[item_id]['quantity_received'] = transfer_request.jobwork_details[item_id]['quantity_received'] + int(received_quantity_actual)
                transfer_request.jobwork_details[item_id]['quantity_yet_to_receive'] = int(transfer_request.jobwork_details[item_id]['quantity_yet_to_receive']) - received_quantity_actual
                if transfer_request.jobwork_details[item_id]['quantity_yet_to_receive'] != 0:
                    transfer_completed = 'Partially Completed'
            elif order_type == 'Supplier':
                purchase_order_item = PurchaseOrderItems.objects.get(
                    id=item['item_id'])
                purchase_order_item.received_units =purchase_order_item.received_units + int(
                    received_quantity_actual)
                purchase_order_item.quantity_yet_to_receive = purchase_order_item.quantity_yet_to_receive - int(received_quantity_actual)
                purchase_order_item.save()
                if purchase_order_item.quantity_yet_to_receive != 0:
                    transfer_completed = 'Partially Completed'
            # except:
            #     continue

        serializer = GRNItemsSerializer(
            grn_item)
        GRNI_serializer.append(
            serializer.data)

        if order_type == 'Internal Transfer' or order_type == 'Jobwork':
            transfer_request.status = transfer_completed
            transfer_request.save()
        elif order_type == 'Supplier':
            purchase_order.status = transfer_completed
            purchase_order.save()
        result = {'GRN': GRN_serializer,
                  'GRNItems': GRNI_serializer}
        # result = 'sr'
        # except Exception as error:
        #     return Response({'status': 'failure', 'data': str(error)}, status=HTTP_206_PARTIAL_CONTENT)
        return Response({'status': 'success', 'data': result}, status=HTTP_201_CREATED)