from .models import ( Purchase_order, Purchase_inquiry,
                     Purchase_inquiry_items, PurchaseOrderItems, Purchase_return, Purchase_return_items,
                    #  GRN, GRN_items, 
                     )
from rest_framework import serializers
from data_management.models import Parties,Rawmaterials,Product,RMAccessoriesGroup


class PurchaseInquirySerializer(serializers.ModelSerializer):
    inquiry_items_list = serializers.SerializerMethodField('get_items')
    supplier_id_get = serializers.SerializerMethodField('get_supplier')

    def get_supplier(self,obj):
        if obj.supplier_id:
            # supplier = Parties.objects.get(id=obj.supplier_id)
            return obj.supplier_id.party_name
        return None

    def get_items(self, obj):
        if obj.purchase_inquiry_no:
            purchase_inquiry_items = Purchase_inquiry_items.objects.filter(
                purchase_inquiry_no=obj.id)
            purchase_inquiry_items_list = []
            for i in purchase_inquiry_items:
                purchase_inquiry_items_list.append(
                    PurchaseInquiryItemsSerializer(i).data)
            return purchase_inquiry_items_list
        return None
    
    class Meta:
        model = Purchase_inquiry
        fields = ['id', 'purchase_inquiry_no', 'po_date','purchase_request_no','supplier_id_get',
                  'supplier_id', 'procurement_user_id', 'expected_date_receipt','freight_charges_paid_by','payment_terms','due_date',
                'total_price','comments','status','inquiry_items_list'
                  ]
        


class PurchaseInquiryItemsSerializer(serializers.ModelSerializer):
    currency_code = serializers.SerializerMethodField('get_currency_code')
    rm_group_get = serializers.SerializerMethodField(
        'get_rm_group')
    rm_name_get = serializers.SerializerMethodField('get_rm_name')

    def get_rm_name(self,obj):
        print(obj.rm_name,obj.category,'rm_name')
        if obj.rm_name:
            try:
                if obj.category == 'Semi-Finished Goods':
                    rm = Product.objects.get(id=obj.rm_name)
                    return rm.product_name
                elif obj.category == 'Raw material' or obj.category == 'Accessories' or obj.category == 'Consumables':
                    rm = Rawmaterials.objects.get(id=obj.rm_name)
                    print(rm,'rm')

                    return rm.rm_name
                else:
                    return None
            except:
                return None

    def get_rm_group(self,obj):
        if obj.rm_group:
            try:
                rm_group_name = RMAccessoriesGroup.objects.get(
                    id=obj.rm_group)
                return rm_group_name.group_name
            except:
                return None
        return None

    def get_currency_code(self,obj):
        if obj.currency:
            return obj.currency.currency_code
        return None
    
    class Meta:
        model = Purchase_inquiry_items
        fields = ['id', 'purchase_inquiry_no','rm_group','rm_group_get','category', 'rm_name','currency_code', 'rm_name_get','rm_quantity', 'rm_unitprice',
                  'rm_total_cost', 'measured_unit', 'currency']


class PurchaseInquiryCreateSerializer(serializers.ModelSerializer):
    inquiry_items = serializers.JSONField()
    issue_for_request = serializers.BooleanField(default=False)
    class Meta:
        model = Purchase_inquiry
        fields = ['id', 'purchase_inquiry_no', 'po_date',
                  'supplier_id', 'procurement_user_id', 'expected_date_receipt','freight_charges_paid_by','payment_terms','due_date',
                'total_price','comments','status','inquiry_items','issue_for_request'
                  ]
        

class PurchaseOrderSerializer(serializers.ModelSerializer):
    order_items_list = serializers.SerializerMethodField('get_items')
    supplier_id_get = serializers.SerializerMethodField('get_supplier')

    def get_supplier(self,obj):
        if obj.supplier_id:
            return obj.supplier_id.party_name
        return None
    
    def get_items(self, obj):
        if obj.purchase_order_no:
            purchase_order_items = PurchaseOrderItems.objects.filter(
                purchase_order_no=obj.id)
            purchase_order_items_list = []
            for i in purchase_order_items:
                purchase_order_items_list.append(
                    PurchaseOrderItemsSerializer(i).data)
            return purchase_order_items_list
        return None

    class Meta:
        model = Purchase_order
        fields = ['id', 'purchase_order_no', 'po_date','reject_comments','tally_status',
                  'supplier_id','supplier_id_get', 'procurement_user_id', 'expected_date_receipt','freight_charges_paid_by','payment_terms','due_date',
                'total_price','delivery_at','comments','status','order_items_list'
                  ]


class PurchaseOrderItemsSerializer(serializers.ModelSerializer):
    currency_code = serializers.SerializerMethodField('get_currency_code')
    rm_group_get = serializers.SerializerMethodField(
        'get_rm_group')
    rm_name_get = serializers.SerializerMethodField('get_rm_name')

    def get_rm_name(self,obj):
        print(obj.rm_name,obj.category,'rm_name')
        if obj.rm_name:
            try:
                if obj.category == 'Semi-Finished Goods' or obj.category == 'Semi-Finished goods':
                    rm = Product.objects.get(id=obj.rm_name)
                    return rm.product_name
                elif obj.category == 'Raw material' or obj.category == 'Accessories' or obj.category == 'Consumables':
                    rm = Rawmaterials.objects.get(id=obj.rm_name)
                    print(rm,'rm')
                    return rm.rm_name
                else:
                    return None
            except:
                return None

    def get_rm_group(self,obj):
        if obj.rm_group:
            try:
                rm_group_name = RMAccessoriesGroup.objects.get(
                    id=obj.rm_group)
                return rm_group_name.group_name
            except:
                return None
        return None

    def get_currency_code(self,obj):
        if obj.currency:
            return obj.currency.currency_code
        return None

    class Meta:
        model = PurchaseOrderItems
        fields = ['id', 'purchase_order_no','rm_group','rm_group_get','category','igst','cgst','igst', 'quantity_yet_to_receive','currency_code','rm_name','rm_name_get', 'rm_quantity', 'rm_unitprice',
                  'rm_total_cost', 'measured_unit', 'gst','currency', 'received_units']


class PurchaseReportSerializer(serializers.ModelSerializer):
    rm_name_get = serializers.SerializerMethodField('get_rm_name')
    supplier = serializers.SerializerMethodField('get_supplier')
    purchase_order_no_get = serializers.SerializerMethodField('get_po_number')
    date = serializers.SerializerMethodField('get_date')
    status = serializers.SerializerMethodField('get_status')
    currency_code = serializers.SerializerMethodField("get_currency")

    def get_currency(self,obj):
        if obj.currency:
            return obj.currency.currency_code
        return None


    def get_supplier(self,obj):
        if obj.purchase_order_no:
            if obj.purchase_order_no.supplier_id:
                return obj.purchase_order_no.supplier_id.party_name
            return None
        return None

    def get_date(self,obj):
        if obj.purchase_order_no:
            return obj.purchase_order_no.po_date
        return None
    
    def get_po_number(self,obj):
        if obj.purchase_order_no:
            return obj.purchase_order_no.purchase_order_no
        return None

    def get_status(self,obj):
        if obj.purchase_order_no:
            return obj.purchase_order_no.status
        return None        

    def get_rm_name(self,obj):
        print(obj.rm_name, obj.category, 'rm_name')
        if obj.rm_name:
            try:
                if obj.category == 'Semi-Finished Goods' or obj.category == 'Semi-Finished goods':
                    rm = Product.objects.get(id=obj.rm_name)
                    return rm.product_name
                elif obj.category == 'Raw material' or obj.category == 'Accessories' or obj.category == 'Consumables':
                    rm = Rawmaterials.objects.get(id=obj.rm_name)
                    print(rm,'rm')
                    return rm.rm_name
                else:
                    return None
            except:
                return None
    class Meta:
        model = PurchaseOrderItems
        fields = ['id','rm_name_get','purchase_order_no_get','rm_total_cost','supplier','currency_code','date','rm_quantity','received_units','status']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    order_items = serializers.JSONField()
    order_items_for_edit = serializers.JSONField(required=False)
    order_items_to_delete = serializers.ListField(required=False)
    class Meta:
        model = Purchase_order
        fields = ['id', 'purchase_order_no', 'po_date','reject_comments','tally_status',
                  'supplier_id', 'procurement_user_id', 'expected_date_receipt','freight_charges_paid_by','payment_terms','due_date',
                'total_price','delivery_at','comments','status','order_items','order_items_for_edit','order_items_to_delete'
                  ]


class purchase_return_serializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase_return
        fields = ['id', 'purchase_return_id', 'grn_id', 'returned_date',
                  'transport_cost', 'currency', 'debit_note_number']


class purchase_return_items_serializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase_inquiry_items
        fields = ['id', 'purchase_return_id', 'rm_id', 'returned_units', 'returned_unit_price', 'actual_unit_price '
                  'currency', 'rm_sgst', 'rm_cgst', 'rm_igst']
