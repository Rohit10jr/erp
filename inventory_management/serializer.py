from .models import Inventory_product, Inventory_rawmaterial, Transfer_requests, Transfer_request_type, vehicle_deatails
from rest_framework.serializers import ModelSerializer, ValidationError, Serializer, SerializerMethodField, JSONField, ListField, FileField
from django.db.models import Q
from purchase_management.models import PurchaseOrderItems, Purchase_order
from data_management.models import RMAccessoriesGroup, Product, Rawmaterials, Parties, MeasuredUnits
from accounts.models import Branch 
from .models import Purchase_request, Purchase_request_items, DebitNotes, GRN, GRN_items


rm_type_choice = [('semi_finished_goods', 'semi_finished_goods'), 
                  ('rawmaterial', 'Rawmaterial')]


class Inventory_rm_serializer(ModelSerializer):
    rm_get = SerializerMethodField('get_rm')
    category = SerializerMethodField('get_category')

    def get_category(self,obj):
        if obj.rm:
            return obj.rm.category
        return None

    def get_rm(self, obj):
        if obj.rm:
            return {'id': obj.rm.id, 'name': obj.rm.rm_name}
        return None

    class Meta:
        model = Inventory_rawmaterial
        fields = ['id', 'rm', 'rm_get', 'rm_stock','category',
                  'rm_stock_production', 'warehouse_name']
        

class InventoryDetailsSerializer(Serializer):
    list_of_goods = ListField


class Inventory_product_serializer(ModelSerializer):
    product_get = SerializerMethodField('get_product')
    warehouse_name_get = SerializerMethodField('get_ware_house_name')
    category = SerializerMethodField('get_category')
    cost_of_inventory = SerializerMethodField('get_cost')
    product_code = SerializerMethodField('get_product_code')
    currency = SerializerMethodField('get_currency')

    def get_product_code(self,obj):
        if obj.product:
            return obj.product.product_code
        return None
    
    def get_currency(self,obj):
        if obj.product:
            if obj.product.currency:
                return obj.product.currency.currency_code
            return None
        return None

    def get_cost(self,obj):
        if obj.product:
            cost = obj.product.maximum_price * obj.product_stock
            return cost
        return 0

    def get_ware_house_name(self, obj):
        if obj.warehouse_name:
            return obj.warehouse_name.branch_name

    def get_product(self, obj):
        if obj.product:
            return obj.product.product_name
        return None
    
    def get_category(self,obj):
        if obj.product:
            if obj.product.product_type == 'finished':
                return 'Finished Goods'
            return 'Semi-finished Goods'
        return None
    
    class Meta:
        model = Inventory_product
        fields = ['id', 'category','product', 'product_get', 'product_stock','cost_of_inventory','currency',
                  'assigned_stock', 'stock_remaining', 'warehouse_name', 'warehouse_name_get','product_code']
        
    def validate(self, data):
        # try:
        inventory_obj = self.Meta.model.objects.filter(
            product=data['product'].id, warehouse_name=(data['warehouse_name']))
        if self.instance:
            inventory_obj = inventory_obj.exclude(id=self.instance.id)
        if len(inventory_obj) > 0:
            # print(inventory_obj[0].id)
            product_name = data['product'].product_name
            warehouse_name = data['warehouse_name']
            raise ValidationError(
                f'{product_name} already has invetory data in {warehouse_name} warehouse')
        return data
    

class transfer_request_type_serializer(ModelSerializer):
    class Meta:
        model = Transfer_request_type
        fields = ['id', 'request_type_id',
                  ' request_type']


class transfer_requests_serializer(ModelSerializer):
    from_party_get = SerializerMethodField('get_from_party')
    to_party_get = SerializerMethodField('get_to_party')

    def get_from_party(self,obj):
        if obj.from_party:
            try:
                branch = Branch.objects.get(id=obj.from_party)
                return branch.branch_name
            except:
                return None
        return None
    
    def get_to_party(self,obj):
        if obj.to_party:
            try:
                if obj.request_type == 'Internal-Transfer':
                    to_party = Branch.objects.get(id=obj.to_party).branch_name
                else:
                    to_party = Parties.objects.get(id=obj.to_party).party_name
                return to_party
            except:
                return None
        return None
    
    class Meta:
        model = Transfer_requests
        fields = ['id','request_id', 'request_date', 'request_type',"to_party_get",
                  'from_party', 'to_party', 'request_details', 'jobwork_details','from_party_get',
                  'expected_date_completion', 'required_status', 'status', 'freight_charges', 'freight_charges_paid_by', 'transporter', 'vehicle_type', 'vehicle_number', 'comments', 'total_price'
                  ]


class purchase_request_create_serializer(Serializer):
    request_items = JSONField()

    class Meta:
        model = Purchase_request
        fields = ['id', 'purchase_request_no', 'purchase_request_date', 'expected_date_of_delivery',
                  'warehouse_user_id', 'production_order_id', 'comments', 'request_items']


class vehicle_deatails_serializer(ModelSerializer):
    class Meta:
        model = vehicle_deatails
        fields = ['Vehicle_Type', 'vehicle_number']


class purchase_request_serializer(ModelSerializer):
    request_items_list = SerializerMethodField('get_items')
    branch_get = SerializerMethodField('get_branch')

    def get_branch(self, obj):
        if obj.branch:
            return obj.branch.branch_name
        return None

    def get_items(self, obj):
        if obj.purchase_request_no:
            purchase_request_items = Purchase_request_items.objects.filter(
                purchase_request_no=obj.id)
            purchase_request_items_list = []
            for i in purchase_request_items:
                purchase_request_items_list.append(
                    purchase_request_items_serializer(i).data)
            return purchase_request_items_list
        return None

    class Meta:
        model = Purchase_request
        fields = ['id', 'purchase_request_no', 'purchase_request_date', 'branch', 'expected_date_of_delivery', 'warehouse_user_id', 'branch_get', 'production_order_id', 'comments',
                  'request_items_list', 'status']


class purchase_request_items_serializer(ModelSerializer):
    purchase_order_no_get = SerializerMethodField(
        'get_purchase_order_no')
    rm_group_get = SerializerMethodField(
        'get_rm_group')
    rm_name_get = SerializerMethodField(
        'get_rm_name')

    def get_rm_name(self,obj):
        if obj.rm_name:
            try:
                if obj.category == 'Semi-Finished goods':
                    rm = Product.objects.get(id=obj.rm_name)
                    return rm.product_name
                elif obj.category == 'Raw material' or obj.category == 'Accessories' or obj.category == 'Consumables':
                    rm = Rawmaterials.objects.get(id=obj.rm_name)
                    # print(rm,'rm')
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

    def get_purchase_order_no(self, obj):
        if obj.purchase_order_no:
            try:
                purchase_order_no = Purchase_order.objects.get(
                    id=obj.purchase_order_no)
                return purchase_order_no.purchase_order_no
            except:
                return None
        return None

    class Meta:
        model = Purchase_request_items
        fields = ['id', 'purchase_request_no', 'purchase_order_no_get', 'purchase_order_no', 'purchase_inquiry_no',
                  'rm_name', 'rm_name_get','rm_quantity', 'measured_unit', 'rm_group','rm_group_get','category']


class GRNCreateSeriliazer(ModelSerializer):
    grn_items = JSONField()

    class Meta:
        model = GRN
        fields = ['id', 'grn_no', 'grn_date', 'grn_items', 'jobwork_invoice_total', 'grn_received_from', 'order_type','document_attached', 'order_no', 'warehouse', 'freight_charges_paid_by', 'freight_charges',
                  'vehicle_type', 'vehicle_number', 'received_by', 'payment_terms', 'due_date', 'invoice_no', 'jobwork_invoice_details', 'grand_total_price', 'currency', 'comments',
                  ]


class GRNSerializer(ModelSerializer):
    grn_items_get = SerializerMethodField('get_items')
    currency_code = SerializerMethodField("get_currency_code")
    grn_received_from_get = SerializerMethodField("get_received_from")
    sender_address = SerializerMethodField("get_sender_address")
    order_no_get = SerializerMethodField("get_order_no")

    def get_sender_address(self,obj):
        if obj.grn_received_from:
            try:
                if obj.order_type == 'Internal Transfer':
                    party_details = Branch.objects.get(id=obj.grn_received_from)
                    party_details = party_details.address
                else:
                    party_details = Parties.objects.get(id=obj.grn_received_from)
                    if party_details.billing_address:
                        party_details = party_details.billing_address
                    else:
                        party_details = party_details.delivery_address
                return party_details
            except:
                return None
        return None
    
    def get_order_no(self,obj):
        if obj.order_no:
            try:
                if obj.order_type == 'Internal Transfer' or obj.order_type == 'JobWork':
                    transfer = Transfer_requests.objects.get(id=obj.order_no)
                    return transfer.request_id
                else:
                    order = Purchase_order.objects.get(id=obj.order_no)
                    return order.purchase_order_no
            except:
                return None
        return None 

    def get_currency_code(self, obj):
        if obj.currency:
            return obj.currency.currency_code

    def get_items(self, obj):
        if obj.grn_no:
            grn_items = GRN_items.objects.filter(
                grn=obj.id)
            items_list = []
            for item in grn_items:
                items_list.append(
                    GRNItemsSerializer(item).data)
            return items_list
        return None
    
    def get_received_from(self,obj):
        if obj.grn_received_from:
            try:
                if obj.order_type == 'Internal Transfer':
                    party_details = Branch.objects.get(id=obj.grn_received_from)
                    party_details = party_details.branch_name
                else:
                    party_details = Parties.objects.get(id=obj.grn_received_from)
                    party_details = party_details.party_name
                return party_details
            except:
                return None
        return None
    
    class Meta:
        model = GRN
        fields = ['id', 'grn_no', 'grn_date','order_no_get', 'grn_items_get', 'jobwork_invoice_total', 'grn_received_from','grn_received_from_get', 'order_type', 'order_no', 'warehouse', 'freight_charges_paid_by', 'freight_charges','document_attached',
                  'vehicle_type', 'vehicle_number', 'received_by','total_amount_paid', 'payment_terms', 'due_date', 'sender_address','invoice_no', 'jobwork_invoice_details', 'grand_total_price', 'currency', 'currency_code', 'comments', 'pending_amount','status']


class GRNItemsSerializer(ModelSerializer):
    rm_group_get = SerializerMethodField(
        'get_rm_group')
    rm_name_get = SerializerMethodField('get_rm_name')
    hsncode = SerializerMethodField('get_hsncode')
    measurement_unit_code = SerializerMethodField('get_measurement_code')

    def get_rm_name(self,obj):
        # print(obj.rm_name,obj.category,'rm_name')
        if obj.rm_name:
            try:
                if obj.category == 'Semi-Finished Goods':
                    rm = Product.objects.get(id=obj.rm_name)
                    return rm.product_name
                elif obj.category == 'Raw material' or obj.category == 'Accessories' or obj.category == 'Consumables':
                    rm = Rawmaterials.objects.get(id=obj.rm_name)
                    # print(rm,'rm')
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

    def get_hsncode(self,obj):
        # print(obj.rm_name,obj.category,'rm_name')
        if obj.rm_name:
            try:
                if obj.category == 'Semi-Finished Goods':
                    rm = Product.objects.get(id=obj.rm_name)
                    return rm.hsncode
                elif obj.category == 'Raw material' or obj.category == 'Accessories' or obj.category == 'Consumables':
                    rm = Rawmaterials.objects.get(id=obj.rm_name)
                    # print(rm,'rm')
                    return rm.hsncode

                else:
                    return None
            except:
                return None

    def get_measurement_code(self,obj):
        if obj.measurement_unit:
            try:
                measured_unit = MeasuredUnits.objects.get(measured_unit_name=obj.measurement_unit)
                return measured_unit.measured_unit_code
            except:
                return None
        return None            

    class Meta:
        model = GRN_items
        fields = ['id', 'grn', 'rm_group','rm_group_get','rm_name_get','category', 'hsncode','rm_name', 'ordered_quantity', 'received_quantity', 'unit_price', 'actual_unit_price',
                  'sgst', 'cgst', 'igst','gst', 'total_price_with_gst','measurement_unit_code', 'currency', 'measurement_unit', 'cost_of_defective_materials', 'number_of_defective_materials']


class DebitNoteSerializer(ModelSerializer):
    class Meta:
        model = DebitNotes
        fields = '__all__'


class FileUploadSerializer(Serializer):
    document_attached = FileField()