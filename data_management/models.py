from django.db import models
from django.core.exceptions import ValidationError
# from django.contrib.postgres.fields import ArrayField
# Create your models here.



product_type_choices = [('finished', 'finished'),
                        ('semi-finished', 'semi-finished'),]

rm_type_choices = [('rawmaterial', 'rawmaterial'),
                    ('semi-finished-goods', 'semi-finished-goods'),]


class PaymentMode(models.Model):
    payment_mode = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.payment_mode


class MeasuredUnits(models.Model):
    id = models.AutoField(primary_key=True)
    measured_unit_name = models.CharField(max_length=30, unique=True)
    measured_unit_code = models.CharField(max_length=30, unique=True, default='id')

    def __str__(self) -> str:
        return self.measured_unit_name

    def save(self, *args, **kwargs):
        self.measured_unit_name = self.measured_unit_name .lower()
        super(MeasuredUnits, self).save(*args, **kwargs)


class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    currency_name = models.CharField(max_length=30, unique=True)
    currency_code = models.CharField(max_length=30, unique=True, default='id')

    def __str__(self) -> str:
        return self.currency_name

    def save(self, *args, **kwargs):
        self.currency_name = self.currency_name.lower()
        super(Currency, self).save(*args, **kwargs)


class PartyType(models.Model):
    party_type = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=30, null=True)

    class Meta:
        verbose_name = "PartyType"

    def __str__(self) -> str:
        return self.party_type

    def save(self, *args, **kwargs):
        self.party_type = self.party_type.lower()
        super(PartyType, self).save(*args, **kwargs)


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=30, unique=True)
    country_code = models.CharField(max_length=30, unique=True, default='id')

    class Meta:
        verbose_name = "Country"

    def __str__(self) -> str:
        return self.country_name

    def save(self, *args, **kwargs):
        self.country_name = self.country_name.lower()
        super(Country, self).save(*args, **kwargs)


class State(models.Model):
    id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=30, null=True, blank=True)
    state_code = models.CharField(max_length=30, unique=True, default='id')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    # GST_code = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self) -> str:
        return self.state_name


class ProductionPhases(models.Model):
    id = models.AutoField(primary_key=True)
    phase_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "ProductionPhase"
        db_table = 'ProductionPhase'

    def __str__(self) -> str:
        return self.phase_name

    def save(self, *args, **kwargs):
        self.phase_name = self.phase_name.lower()
        super(ProductionPhases, self).save(*args, **kwargs)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product_code = models.CharField(unique=True, max_length=50, default='id')
    product_name = models.CharField(unique=True, max_length=100)
    product_type = models.CharField(max_length=50, choices=product_type_choices, default='finished')
    igst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    sgst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    cgst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    # min_stock = models.IntegerField(default=100)
    measured_unit = models.ForeignKey(MeasuredUnits, on_delete=models.SET_NULL, null=True, blank=True)
    maximum_price = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    minimum_stock_quantity = models.IntegerField(null=True)
    minimum_price = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    multiple_parts = models.BooleanField(default=False)
    hsncode = models.CharField( max_length=100,null=True,blank=True)
    # parts = ArrayField(
    #             models.CharField(max_length=50, blank=True),
    #             blank=True,
    #             default=list,
    #             null=True
    #         )

    class Meta:
        verbose_name = "Product"

    def __str__(self) -> str:
        return self.product_name
    
    def save(self, *args, **kwargs):
        if self.multiple_parts == False:
            self.parts = [self.product_name]
        # else:
        #     if self.product_type == 'finished':
        #         if ('package' in self.parts) == False:
        #             self.parts.append('package')
        super(Product, self).save(*args, **kwargs)


class RMAccessoriesGroup(models.Model):
    category = models.CharField(max_length=30)
    group_name = models.CharField(max_length=100)
    # preferred_suppliers = ArrayField(
    #                         models.CharField(max_length=50, blank=True),
    #                         blank=True,
    #                         default=list,
    #                         null=True
    #                     )

    class Meta:
        verbose_name = "RM/Accessories Group"

    def __str__(self) -> str:
        return self.group_name
    

class Rawmaterials(models.Model):
    id = models.AutoField(primary_key=True)
    rm_code = models.CharField(max_length=30, unique=True, default='id')
    category = models.CharField(max_length=100, null=True, blank=True)
    rm_group = models.ForeignKey(RMAccessoriesGroup, on_delete=models.SET_NULL, null=True, blank=True)
    rm_name = models.CharField(max_length=50)
    measured_unit = models.ForeignKey(MeasuredUnits, on_delete=models.SET_NULL, null=True, blank=True)
    igst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    sgst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    cgst = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    hsncode = models.CharField(max_length=100,null=True,blank=True)
    min_stock = models.IntegerField()
    rm_max_price = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    last_purchase_price = models.DecimalField(decimal_places=2, null=True, max_digits=25,default=0)
    # preferred_supplier = ArrayField(
    #                         models.CharField(max_length=30, null=True, blank=True),
    #                         default=list,
    #                         null=True,blank=True
    #                     )
    
    class Meta:
        verbose_name = "RawMaterial"

    def __str__(self) -> str:
        return self.rm_name


class BillOfMaterials(models.Model):
    id = models.AutoField(primary_key=True)
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=30, null=True, blank=True)
    rm_serial_no = models.IntegerField(unique=True, null=True, blank=True)
    rm_group = models.ForeignKey(RMAccessoriesGroup, on_delete=models.SET_NULL, null=True, blank=True, default=None)
    category = models.CharField(max_length=100, null=True, blank=True)
    rm_type = models.CharField(max_length=100, default='Raw material')
    rm_code = models.CharField(max_length=50, null=True, blank=True)
    # rm_id = models.IntegerField(null=True)
    rm_name = models.CharField(max_length=50)
    rm_quantity = models.DecimalField(decimal_places=2, null=True, max_digits=20)
    production_phase = models.ForeignKey(ProductionPhases, on_delete=models.SET_NULL, null=True, blank=True)
    measured_unit = models.ForeignKey(MeasuredUnits, on_delete=models.SET_NULL, null=True, blank=True)
    damage = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "BillOfMaterial"

    def __str__(self) -> str:
            return self.product_code.product_name + '-' + self.rm_name


class ProductionFlow(models.Model):
    id = models.AutoField(primary_key=True)
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
    part_name = models.CharField(max_length=100, null=True, blank=True)
    phases = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "ProductionFlow"

    def __str__(self) -> str:
        return self.part_name


class Parties(models.Model):
    id = models.AutoField(primary_key=True)
    party_category = models.CharField(max_length=100, null=True, blank=True)
    party_type = models.ForeignKey(PartyType, on_delete=models.SET_NULL, null=True)
    party_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    party_name = models.CharField(max_length=50)
    # door_no = models.CharField(max_length=100,null=True,blank=True)
    billing_address = models.TextField()
    delivery_address = models.TextField(null=True)
    payment_terms = models.CharField(max_length=100, default='30 days')
    party_state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    party_pincode = models.CharField(max_length=100, null=True, blank=True)
    party_gstin = models.CharField(max_length=30, null=True, blank=True)
    party_products = models.JSONField(null=True, blank=True)
    party_contact_name = models.CharField(max_length=30, null=True, blank=True)
    party_contact_no = models.CharField(max_length=30, null=True, blank=True)
    party_email = models.CharField(max_length=30, null=True, blank=True)
    party_city = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        verbose_name = "Party"

    def clean(self):
        parties = Parties.objects.filter(party_name__iexact=self.party_name.lower())
        if self.pk:
            parties = parties.exclude(pk=self.pk)
        if parties.exists():
            raise ValidationError("This party already exists.")

    def __str__(self) -> str:
        return self.party_name


class Productivity(models.Model):
    id = models.AutoField(primary_key=True)
    phase = models.ForeignKey(ProductionPhases, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    part_name = models.CharField(max_length=50, null=True, blank=True)
    quantity_perday = models.PositiveIntegerField()
    scrap_quantity = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.quantity_perday)
    

class Payments(models.Model):
    invoice_number = models.CharField(max_length=50, null=True, default=True)
    amount_paid =  models.DecimalField(decimal_places=2, null=True, max_digits=20)
    payment_date = models.DateField() 
    party_id = models.CharField(max_length=50, null=True, blank=True)
    payment_type =  models.CharField(max_length=50, null=True, blank=True)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return '{} - {}'.format(self.invoice_number, self.amount_paid)

    # are these both kind of similar
    # def __str__(self) -> str:
    #         return self.product_code.product_name + '-' + self.rm_name