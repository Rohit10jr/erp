from django.db.models import Q
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, ValidationError, Serializer, SerializerMethodField
from .models import (PartyType, Parties, Product, PartyType,PaymentMode,RMAccessoriesGroup, 
                     Rawmaterials, Currency, MeasuredUnits, BillOfMaterials, ProductionPhases, 
                     ProductionFlow, Country ,Productivity, State,Payments)



class ProductSerializer(ModelSerializer):
    currency_get = SerializerMethodField("get_currency")
    currency_code = SerializerMethodField('get_currency_code')
    measured_unit_get = SerializerMethodField("get_measured_unit")
    measured_unit_code = SerializerMethodField("get_measured_unit_code")

    def get_measured_unit_code(self, obj):
        if obj.measured_unit:
            return obj.measured_unit.measured_unit_code
        return None

    def get_measured_unit(self, obj):
        if obj.measured_unit:
            return obj.measured_unit.measured_unit_name
        return None
    

    def get_currency(self, obj):
        if obj.currency:
            return obj.currency.currency_name
        return None

    def get_currency_code(self, obj):
        if obj.currency:
            return obj.currency.currency_code
        return None

    class Meta:
        model = Product
        fields = ['pk', 'product_code', 'measured_unit','hsncode', 'measured_unit_get','measured_unit_code', 'product_name', 'product_type', 'currency_code', 'multiple_parts', 'parts',
                  'minimum_stock_quantity','igst','sgst','cgst','maximum_price', 'minimum_price', 'currency', 'currency_get']

    def validate(self, data):
        if not data['multiple_parts']:
            data['parts'] = []
        if data['maximum_price'] < data['minimum_price']:
            raise ValidationError(
                'Maximum price must be greater than minimum price')
        return super().validate(data)


class PartyTypeSerializer(ModelSerializer):
    class Meta:
        model = PartyType
        fields = ['pk', 'party_type','category']

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if not self.instance and PartyType.objects.filter(party_type=data['party_type']).exists():
            raise ValidationError("Party type already exists")
        return data


class PartiesUpdateSerializer(ModelSerializer):
    party_country = SerializerMethodField('party_country_get')
    party_type = SerializerMethodField('party_type_get')


class PartiesSerializer(ModelSerializer):
    party_country_get = SerializerMethodField('get_party_country')
    party_type_get = SerializerMethodField('get_party_type')
    party_state_get = SerializerMethodField('get_party_state')
    party_state_code = SerializerMethodField('get_party_state_code')

    def get_party_country(self, object):
        if object.party_country:
            return object.party_country.country_name
        return None

    def get_party_state(self, object):
        if object.party_state:
            return object.party_state.state_name
        return None
    
    def get_party_state_code(self,object):
        if object.party_state:
            return object.party_state.state_code

    def get_party_type(self, object):
        if object.party_type:
            return object.party_type.party_type
        return None

    class Meta:
        model = Parties
        fields = ['pk', 'party_name', 'party_country','party_category', 'party_country_get', 'party_type', 'party_type_get', 'party_state', 'party_state_code','billing_address','delivery_address','payment_terms',
                  'party_pincode', 'party_contact_no', 'party_contact_name', 'party_email', 'party_gstin', 'party_state_get', 'party_products','party_city']

    def validate(self, data):
        queryset = Parties.objects.all()
        """
        Check that start is before finish.
        """
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.filter(party_name=data['party_name']).exists():
            # print(queryset.filter(party_name=data['party_name']))
            raise ValidationError("Party already exists")
        elif data['party_country'] and str(data['party_country'].country_name).lower() != 'india':
            # print(data['party_country'])
            data['party_state'] = None
            data['party_gstin'] = ''
        return data


class BillOfMaterialsSerializer(ModelSerializer):
    # rm_id_get = SerializerMethodField("get_rm_id")
    product_code_get = SerializerMethodField("get_product")
    measured_unit_get = SerializerMethodField("get_measured_unit")
    production_phase_get = SerializerMethodField("get_phase")
    rm_price = SerializerMethodField('get_price')
    rm_currency_code = SerializerMethodField('get_currency_code')
    rm_group_get = SerializerMethodField('get_rm_group')

    def get_rm_group(self, obj):
        if obj.rm_group:
            return obj.rm_group.group_name
        return None

    def get_currency_code(self, obj):
        if obj.category == 'Semi-Finished Goods':
            try:
                rm_obj = Product.objects.get(product_code=obj.rm_code)
                return rm_obj.currency.currency_code
            except:
                return None
        else:
            try:
                rm_obj = Rawmaterials.objects.get(rm_code=obj.rm_code)
                if rm_obj.currency:
                    return rm_obj.currency.currency_code
            except:
                return None
        return None

    def get_price(self, obj):
        if obj.category == 'Semi-Finished Goods':
            try:
                rm_obj = Product.objects.get(product_code=obj.rm_code)
                return rm_obj.maximum_price
            except:
                return None
        else:
            try:
                rm_obj = Rawmaterials.objects.get(rm_code=obj.rm_code)
                if rm_obj.currency:
                    return rm_obj.rm_max_price
            except:
                return None
        return None

    def get_phase(self, obj):
        if obj.production_phase:
            return obj.production_phase.phase_name
        return None

    def get_product(self, obj):
        if obj.product_code:
            return obj.product_code.product_name
        return None

    def get_measured_unit(self, obj):
        if obj.measured_unit:
            return obj.measured_unit.measured_unit_name
        return None

    class Meta:
        model = BillOfMaterials
        fields = ['pk', 'product_code', 'rm_serial_no', 'part_name', 'rm_price', 'rm_currency_code','rm_type','rm_group','rm_group_get',
                  'rm_code', 'rm_quantity', 'measured_unit', 'rm_name', 'category', 'production_phase_get', 'production_phase', 'measured_unit_get', 'product_code_get','damage']
        # read_only_fields = ['id', 'rm_idname']

    # def validate(self, attrs):
        # queryset = BillOfMaterials.objects.all()
        # if self.instance:
        #     queryset.exclude(id=self.instance.id)
        # else:
        #     queryset = queryset.filter(
        #         product_code=attrs['product_code'].pk, rm_code=attrs['rm_code'], rm_type=attrs['rm_type'])
        #     if queryset.exists():
        #         raise ValidationError(
        #             f"Raw material already exists for product")
        # return super().validate(attrs)


class ProductionPhasesSerializer(ModelSerializer):
    class Meta:
        model = ProductionPhases
        fields = ['pk', 'phase_name']


class StateSerializer(ModelSerializer):
    country_get = SerializerMethodField('get_country')

    def get_country(self, object):
        if object.country:
            return object.country.country_name
        return None

    class Meta:
        model = State
        fields = ['pk', 'country', 'country_get', 'state_name', 'state_code']


class ProductionFlowSerializer(ModelSerializer):
    product_get = SerializerMethodField("get_product")

    def get_product(self, obj):
        if obj.product_code:
            return obj.product_code.product_name
        return None

    class Meta:
        model = ProductionFlow
        fields = ['pk', 'id', 'product_code',
                  'part_name', 'phases', 'product_get']

    def validate(self, data):
        products = ProductionFlow.objects.filter(
            part_name=data['part_name'], product_code=data['product'])
        if self.instance:
            id = self.instance.id
            products = products.exclude(id=id)
        if products:
            raise ValidationError("Product already exists")
        # print('as', data['product_code'].parts)
        if data['product'].multiple_parts and data['part_name'] not in data['product'].parts:
            raise ValidationError("Invalid part name")
        if data['phases']:
            for phase in data['phases']:
                try:
                    phase_value = data['phases'][phase]
                    phase_obj = ProductionPhases.objects.get(
                        phase_name=phase_value)
                    phase_obj = ProductionPhasesSerializer(
                        instance=phase_obj).data
                    # print(phase_obj, phase_obj['phase_name'])
                    data['phases'][phase] = phase_obj
                except ProductionPhases.DoesNotExist:
                    raise ValidationError("Invalid phase")
        return data


class PFSerializer(ModelSerializer):
    class Meta:
        model = ProductionFlow
        fields = ['product_code', 'part_name']


class RawmaterialsSerializer(ModelSerializer):
    # preferred_supplier_get = SerializerMethodField("get_supplier")
    measured_unit_get = SerializerMethodField("get_measured_unit")
    currency_get = SerializerMethodField("get_currency")
    currency_code = SerializerMethodField('get_currency_code')
    rm_group_get = SerializerMethodField('get_rm_group')
    measured_unit_code = SerializerMethodField("get_measured_unit_code")

    def get_measured_unit_code(self, obj):
        if obj.measured_unit:
            return obj.measured_unit.measured_unit_code
        return None

    def get_currency_code(self, obj):
        if obj.currency:
            return obj.currency.currency_code
        return None

    def get_currency(self, obj):
        if obj.currency:
            return obj.currency.currency_name
        return None

    def get_measured_unit(self, obj):
        if obj.measured_unit:
            return obj.measured_unit.measured_unit_name
        return None
    
    def get_rm_group(self, obj):
        if obj.rm_group:
            return obj.rm_group.group_name

    # def get_supplier(self, obj):
    #     if obj.preferred_supplier_id:
    #         return obj.preferred_supplier_id.party_name
    #     return None

    class Meta:
        model = Rawmaterials
        fields = ['pk','category','rm_group','rm_group_get', 'hsncode','measured_unit_code','rm_name', 'rm_code', 'measured_unit', 'measured_unit_get', 'min_stock','igst','sgst','cgst',
                  'rm_max_price', 'currency', 'currency_get', 'preferred_supplier', 'currency_code','last_purchase_price']
        read_only_fields = ['pk']


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ['pk', 'country_code', 'country_name']


class ProductRawmaterials(ModelSerializer):
    class Meta:
        model = BillOfMaterials
        fields = '__all__'


class ProductivitySerializer(ModelSerializer):
    product_get = SerializerMethodField("get_product")
    phase_get = SerializerMethodField("get_phase")

    def get_phase(self, obj):
        if obj.phase:
            return obj.phase.phase_name
        return None

    def get_product(self, obj):
        if obj.product:
            return obj.product.product_name
        return None

    class Meta:
        model = Productivity
        fields = ['pk', 'id', 'product', 'product_get', 'part_name',
                  'phase', 'phase_get', 'quantity_perday', 'scrap_quantity']
        

class CurrencySerializer(ModelSerializer):
    class Meta:
        model = Currency
        fields = ['pk', 'currency_code', 'currency_name']


class UnitSerializer(ModelSerializer):
    class Meta:
        model = MeasuredUnits
        fields = ['pk', 'measured_unit_name', 'measured_unit_code']


class pf_serializer(Serializer):
    product = serializers.IntegerField(allow_null=False)
    part_name = serializers.CharField()
    productivity_to_add = serializers.ListField()
    productivity_to_update = serializers.ListField()
    productivity_to_delete = serializers.ListField()



class PaymentsSerializer(ModelSerializer):
    payment_mode_get = SerializerMethodField('get_payment_mode')    
    currency_get = SerializerMethodField("get_currency")
    currency_code = SerializerMethodField('get_currency_code')

    def get_currency_code(self, obj):
        if obj.currency:
            return obj.currency.currency_code
        return None

    def get_currency(self, obj):
        if obj.currency:
            return obj.currency.currency_name
        return None
    
    def get_payment_mode(self,obj):
        if obj.payment_mode:
            return obj.payment_mode.payment_mode

    class Meta:
        model = Payments
        fields = ['id','amount_paid','invoice_number','payment_date','payment_type','party_id','payment_mode','payment_mode_get','currency','currency_get','currency_code']


class RMAccessoriesGroupSerializer(ModelSerializer):
     class Meta:
        model = RMAccessoriesGroup
        fields = ['pk','group_name','category','preferred_suppliers']


class PaymentModeSerialiazer(ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id','payment_mode']


class PreferredSuppliersGETSerializer(Serializer):
    rm_list = serializers.ListField()


class DownloadReportSerializer(Serializer):
    report_list = serializers.ListField()
    page_name = serializers.CharField()