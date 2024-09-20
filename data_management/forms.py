from django.forms import ModelForm
from accounts.models import *
from data_management.models import *
# from inventory_management.models import Inventory_product, Inventory_rawmaterial, vehicle_deatails

# model_list

class UserprofileForm(ModelForm):
    class Meta:
        models = User
        fields = '__all__'


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone',
                  'department', 'department_subdivision', 'role', 'branch']


class UserRoleForm(ModelForm):
    class Meta:
        model = UserRole
        fields = '__all__'


class ProductionphaseForm(ModelForm):
    class Meta:
        model = ProductionPhases
        fields = '__all__'


class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'


class SubDivisionForm(ModelForm):
    class Meta:
        model = Sub_division
        fields = '__all__'


class PartyTypeForm(ModelForm):
    class Meta:
        model = PartyType
        fields = '__all__'


class CountryForm(ModelForm):
    class Meta:
        model = Country
        fields = '__all__'


class PartyForm(ModelForm):
    class Meta:
        model = Parties
        fields = '__all__'
        # exclude = ['party_address']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ProductionFlowForm(ModelForm):
    class Meta:
        model = ProductionFlow
        fields = '__all__'


class RawmaterialsForm(ModelForm):
    class Meta:
        model = Rawmaterials
        fields = '__all__'


class BillOfMaterialsForm(ModelForm):
    class Meta:
        model = BillOfMaterials
        fields = '__all__'


class ProductionPhasesForm(ModelForm):
    class Meta:
        model = ProductionPhases
        fields = '__all__'


class ProductivityForm(ModelForm):
    class Meta:
        model = Productivity
        fields = '__all__'


class CurrencyForm(ModelForm):
    class Meta:
        model = Currency
        fields = '__all__'


class UnitForm(ModelForm):
    class Meta:
        model = MeasuredUnits
        fields = '__all__'

# inventory app

# class vehicle_deatails_form(ModelForm):
#     class Meta:
#         model = vehicle_deatails
#         fields = ['Vehicle_Type', 'vehicle_number']

# class InventoryRmForm(ModelForm):
#     class Meta:
#         models = Inventory_rawmaterial
#         fields = '__all__'

# class InventoryProductForm(ModelForm):
#     class Meta:
#         models = Inventory_product
#         fields = '__all__'

# class BranchForm(ModelForm):
#     class Meta:
#         model = Branch
#         fields = '__all__'