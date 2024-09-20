from django.db import models
from data_management.models import Rawmaterials, Product, ProductionFlow, ProductionPhases, Parties, Currency
from accounts.models import User, Branch
from django.core.exceptions import ValidationError
# from django.contrib.postgres.fields import ArrayField
# from sales_management.models import Sales_order
# from purchase_management.models import Purchase_order
# from sales_management.models import Sales_order,Sales_order_items


status_choices = [('new', 'new'),
                  ('completed', 'completed'),
                  ('cancelled', 'cancelled'),
                  ('modified', 'modified')]

freight_charges_paid_by_choices = [('self', 'self'),
                                   ('other_party', 'other_party')]

fcp_choices_debit_note = [('Self', 'Self'), 
                          ('Customer', 'Customer')]

rm_type_choices = [('Semi-Finished-Goods', 'Semi-Finished-Goods'),
                   ('Raw material/Accesories', 'Raw material/Accesories'), ('other', 'other')]

production_type_choices = [('internal', 'internal'),
                           ('sales-order', 'sales-order'),]

mpo_status_choices = [('awaiting_raw_material', 'awaiting_raw_material'),
                      ('initiate_sub_production', 'initiate_sub_production')]


class Inventory_rawmaterial(models.Model):
    rm = models.ForeignKey(Rawmaterials, on_delete=models.SET_NULL, null=True, blank=True)
    rm_name = models.CharField(max_length=200, null=True, blank=True)
    rm_stock = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    rm_stock_production = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    rm_min_stock =  models.DecimalField(decimal_places=2, null=True, max_digits=20)
    warehouse_name = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            if self.rm:
                rm = Rawmaterials.objects.get(id=self.rm.id)
                self.rm_name = rm.rm_name
        except Exception as error:
            raise ValidationError(error)
        return super(Inventory_rawmaterial, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.rm.rm_name) + '-' + str(self.rm_stock)


class Inventory_product(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    product_stock = models.PositiveIntegerField()
    assigned_stock = models.JSONField(null=True, blank=True)
    stock_remaining = models.PositiveIntegerField(null=True, blank=True)
    rm_min_stock =  models.PositiveIntegerField(null=True, blank=True)
    warehouse_name = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            if self.product:
                product = Product.objects.get(id=self.product.id)
                self.product_name = product.product_name

        except Exception as error:
            raise ValidationError(error)
        return super(Inventory_product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.product) + '-' + str(self.warehouse_name)


class Transfer_request_type(models.Model):
    request_type = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'transfer_request_type'

    def __str__(self):
        return self.request_type


class Transfer_requests(models.Model):
    request_id = models.CharField(max_length=50, null=True, blank=True)
    request_date = models.DateField(auto_now_add=True)
    request_type = models.CharField(max_length=50, null=True, blank=True)
    from_party = models.CharField(max_length=50, null=True, blank=True)
    to_party = models.CharField(max_length=50, null=True, blank=True)
    request_details = models.JSONField(null=True, blank=True)
    jobwork_details = models.JSONField(null=True, blank=True)
    expected_date_completion = models.DateField(auto_now_add=True)
    required_status = models.CharField(blank=True, null=True, max_length=40)
    status = models.CharField(default='new', max_length=50)
    freight_charges = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    freight_charges_paid_by = models.CharField(max_length=20, choices=freight_charges_paid_by_choices, default="Self")
    transporter = models.ForeignKey(Parties, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    total_price = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    # currency = models.ForeignKey(
    #     Currency, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Transfer_requests'


class Purchase_request(models.Model):
    purchase_request_no = models.CharField(max_length=50, null=True, blank=True)
    purchase_request_date = models.DateField(auto_now_add=True)
    expected_date_of_delivery = models.DateField(null=True, blank=True)
    warehouse_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    production_order_id = models.CharField(max_length=50, null=True, blank=True)
    comments = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Purchase_request'

    def __str__(self):
        return self.purchase_request_no


class Purchase_request_items(models.Model):
    purchase_request_no = models.ForeignKey(Purchase_request, on_delete=models.SET_NULL, null=True)
    category = models.CharField( default='Raw material', max_length=100)
    rm_group = models.CharField(null=True,blank=True,max_length=100)
    rm_name = models.CharField(max_length=100, null=True, blank=True)
    rm_quantity = models.IntegerField(null=True)
    measured_unit = models.CharField(max_length=50, null=True, blank=True)
    purchase_order_no = models.IntegerField(null=True, blank=True)
    # rm_id = models.IntegerField(null=True, blank=True)
    # rm_unitprice = models.IntegerField(null=True, blank=True)
    # currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    # purchase_inquiry_no = ArrayField(
    #     models.CharField(max_length=50, blank=True),
    #     blank=True, default=list, null=True
    # )

    class Meta:
        verbose_name = 'purchase_request_items'

    def __str__(self):
        return self.purchase_request_no


class vehicle_deatails(models.Model):
    Vehicle_Type = models.CharField(blank=True, null=True, max_length=50)
    vehicle_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.vehicle_number


class DebitNotes(models.Model):
    debit_note_no = models.CharField(max_length=50, blank=True, null=True)
    return_date = models.DateField(auto_now_add=True)
    supplier_invoice_number = models.CharField(max_length=100, blank=True, null=True)
    freight_charges = models.FloatField(null=True, blank=True)
    freight_charges_paid_by = models.CharField(max_length=20, choices=fcp_choices_debit_note, default="Self")
    grand_total_price = models.FloatField(null=True, blank=True)
    # transporter = models.ForeignKey(Parties, on_delete=models.SET_NULL, null=True,blank=True
    # )
    send_to = models.ForeignKey(Parties, on_delete=models.SET_NULL, null=True)
    warehouse = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    debit_items = models.JSONField(null=True, blank=True)


class GRN(models.Model):
    # grn_id = models.IntegerField()
    # grn_type = models.CharField(max_length=100,null=True,blank=True)
    grn_no = models.CharField(max_length=100, null=True, blank=True)
    grn_date = models.DateField(auto_now_add=True, null=True)
    grn_received_from = models.IntegerField(null=True, blank=True)
    order_no = models.CharField(max_length=100, null=True, blank=True)
    order_type = models.CharField(max_length=50, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    warehouse = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    freight_charges_paid_by = models.CharField(max_length=20, choices=fcp_choices_debit_note, null=True, blank=True)
    freight_charges = models.DecimalField(decimal_places=2, null=True, max_digits=20, blank=True)
    received_by = models.CharField(max_length=100, null=True, blank=True)
    grand_total_price = models.DecimalField(decimal_places=2, null=True, max_digits=20, blank=True)
    jobwork_invoice_details = models.JSONField(null=True, blank=True)
    jobwork_invoice_total = models.CharField(max_length=100, null=True, blank=True)
    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    payment_terms = models.CharField(max_length=100, null=True, blank=True)
    pending_amount = models.DecimalField(decimal_places=2, default=0, max_digits=20)
    total_amount_paid = models.DecimalField(decimal_places=2, default=0, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    document_attached = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default='New')
    # purchase_invoice_date = models.DateField()
    # purchase_invoice_value = models.IntegerField()
    # total_purchase_value = models.DecimalField(decimal_places=2,null=True,blank=True,max_digits=20)

    class Meta:
        verbose_name = 'Grn'

    def __str__(self):
        return self.grn_no


class GRN_items(models.Model):
    grn = models.ForeignKey(GRN, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField( default='Raw material', max_length=100)
    rm_group = models.CharField(null=True,blank=True,max_length=100)
    rm_name = models.CharField(max_length=100, null=True, blank=True)
    ordered_quantity = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    received_quantity = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    unit_price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    actual_unit_price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    measurement_unit = models.CharField(max_length=50, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_defective_materials = models.IntegerField(null=True, blank=True)
    cost_of_defective_materials = models.DecimalField(decimal_places=2, null=True, max_digits=20, blank=True)
    gst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    sgst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    cgst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    igst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    gst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    total_price_with_gst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    gst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)

    class Meta:
        verbose_name = 'Grn_Items'

    def __str__(self):
        return str(self.grn)
