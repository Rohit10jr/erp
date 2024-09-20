from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
import datetime
# import pyrebase

order_serial_numbers = {
    'sales_order': 'SHPL',
    'production order': 'SHPDO',
    'material request': 'SHMRN',
    'purchase_request': 'SHPR',
    'debit_note': 'SHDNS',
    'grn': 'SHGRN',
    'delivery_invoice': 'SH',
    'purchase_inquiry': 'SHPI',
    'purchase_order': 'SHPL',
    'credit_note': 'SHCN',
    'delivery_note': 'SHDN',
}


class ResponseChoices(TextChoices):
    SUCCESS = 'success', _('success')
    FAILURE = 'failure', _('failure')
    LOGOUT = 'logout success', _('logout success')
    NOT_VALID_MODEL = 'Please give a valid model name', _('give a valid model')


def get_order_serial_number(number_code, model_name, field_name=None):
    today = datetime.datetime.today()
    year = int(str(today.year)[2:])
    month = today.month
    year_str = ''
    if month < 4:
        year_str += '{}-{}'.format(str(year-1), str(year))
    else:
        year_str += '{}-{}'.format(str(year), str(year+1))
    search_type = 'contains'
    filter = field_name + '__' + search_type
    print(model_name, 'name', field_name)
    print('10' > '9')
    last_obj = (model_name.objects.filter(
        **{filter: year_str})).last()
    
    print(last_obj, 'status')
    last_number = 1
    if last_obj:
        str_length = len(number_code) + len(year_str) + 2
        last_number_str = getattr(last_obj, field_name)
        print(last_number_str[str_length:],'da')
        last_number = int(last_number_str[str_length:]) + 1
    serial_number = '{}/{}/{}'.format(number_code, year_str, last_number)
    return serial_number