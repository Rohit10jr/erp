from django.forms import ModelForm
from .models import Inventory_product, Inventory_rawmaterial, Purchase_request, Purchase_request_items, Transfer_requests, Transfer_request_type


class purchase_requestform(ModelForm):
    class Meta:
        model = Purchase_request
        fields = '__all__'


class purchase_request_itemsform(ModelForm):
    class Meta:
        model = Purchase_request_items
        fields = '__all__'


class Inventory_productForm(ModelForm):
    class Meta:
        model = Inventory_product
        fields = '__all__'


class Inventory_rawmaterialForm(ModelForm):
    class Meta:
        model = Inventory_rawmaterial
        fields = '__all__'


class transfer_request_typeForm(ModelForm):
    class Meta:
        model = Transfer_request_type
        fields = '__all__'


class transfer_requestsForm(ModelForm):
    class Meta:
        model = Transfer_requests
        fields = '__all__'


