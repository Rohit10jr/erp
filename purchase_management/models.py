from django.db import models
from accounts.models import User
from data_management.models import Rawmaterials, Parties, Currency, Product
from django.core.exceptions import ValidationError
# from django.contrib.postgres.fields import ArrayField
# from inventory_management.models import GRN_items, GRN


rm_type_choices = [('semi_finished_goods', 'semi_finished_goods'),
                   ('rawmaterial', 'Rawmaterial'),]

rm_type_choices_poi = [('Semi-Finished-Goods', 'Semi-Finished-Goods'),
                       ('Raw material/Accesories', 'Raw material/Accesories'), ('other', 'other')]

freight_charges_paid_by_choices = [('Self', 'Self'),
                                   ('Customer', 'Customer')]


class Purchase_inquiry(models.Model):
    purchase_inquiry_no = models.CharField(max_length=50, null=True, blank=True)
    po_date = models.DateField()
    purchase_request_no = models.CharField(max_length=50, null=True, blank=True)
    supplier_id = models.ForeignKey(Parties, on_delete=models.SET_NULL, null=True)
    procurement_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    expected_date_receipt = models.DateField(null=True, blank=True)
    freight_charges_paid_by = models.CharField(max_length=30, choices=freight_charges_paid_by_choices, default="Self")
    payment_terms = models.CharField(max_length=50, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    comments = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    # purchase_order_no = models.ForeignKey(
    #     Purchase_order, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'purchase_inquiry'

    def __str__(self):
        return self.purchase_inquiry_no


class Purchase_inquiry_items(models.Model):
    purchase_inquiry_no = models.ForeignKey(Purchase_inquiry, on_delete=models.SET_NULL, null=True)
    # rm_id = models.ForeignKey(Rawmaterials, on_delete=models.SET_NULL, null=True)
    category = models.CharField( default='Raw material', max_length=100)
    rm_group = models.CharField(null=True,blank=True,max_length=100)
    rm_name = models.CharField(max_length=100, null=True, blank=True)
    rm_quantity = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    rm_unitprice = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    rm_total_cost = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    measured_unit = models.CharField(max_length=50, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'purchase_inquiry_items'

    def __str__(self):
        return self.rm_name


class Purchase_order(models.Model):
    purchase_order_no = models.CharField(null=True, blank=True, max_length=50)
    po_date = models.DateField(null=True, blank=True)
    supplier_id = models.ForeignKey(Parties, on_delete=models.SET_NULL, null=True)
    procurement_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    expected_date_receipt = models.DateField(null=True, blank=True)
    freight_charges_paid_by = models.CharField(max_length=40, choices=freight_charges_paid_by_choices, default="Self")
    payment_terms = models.CharField(max_length=50, null=True, blank=True)
    tally_status = models.CharField(max_length=50, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    purchase_inquiry_no = models.ForeignKey(Purchase_inquiry, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_at = models.CharField(null=True, blank=True, max_length=100)
    comments = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    reject_comments = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'purchase_order'

    def __str__(self):
        return self.purchase_order_no


class PurchaseOrderItems(models.Model):
    purchase_order_no = models.ForeignKey(Purchase_order, on_delete=models.SET_NULL, null=True)
    category = models.CharField( default='Raw material', max_length=100)
    rm_group = models.CharField(null=True,blank=True,max_length=100)
    rm_name = models.CharField(max_length=100, null=True, blank=True)
    rm_quantity = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    rm_unitprice = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    rm_total_cost = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    measured_unit = models.CharField(max_length=50, null=True, blank=True)
    cgst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    sgst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    igst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    gst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    received_units = models.IntegerField(default=0)
    quantity_yet_to_receive = models.IntegerField(null=True, blank=True)
    # expected_date_receipt = models.DateField()

    class Meta:
        verbose_name = 'purchase_order_items'

    def __str__(self):
        return self.rm_name

    def save(self, *args, **kwargs):
        try:
            self.quantity_yet_to_receive = int(
                self.rm_quantity) - int(self.received_units)
        except Exception as error:
            raise ValidationError(error)
        return super(PurchaseOrderItems, self).save(*args, **kwargs)


class Purchase_return(models.Model):
    purchase_return_id = models.IntegerField()
    # grn_id = models.ForeignKey(GRN_items, on_delete=models.SET_NULL, null=True)
    returned_date = models.DateField()
    transport_cost = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    debit_note_number = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'purchase_return'

    def __str__(self):
        return self.transport_cost


class Purchase_return_items(models.Model):
    purchase_return_id = models.ForeignKey(Purchase_return, on_delete=models.SET_NULL, null=True)
    rm_id = models.ForeignKey(Rawmaterials, on_delete=models.SET_NULL, null=True)
    returned_units = models.IntegerField()
    returned_unit_price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    actual_unit_price = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    rm_sgst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    rm_cgst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)
    rm_igst = models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=20)

    class Meta:
        verbose_name = 'purchase_return_items'

    def __str__(self):
        return self.rm_id


