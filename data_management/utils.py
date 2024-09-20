from .models import *
from .serializer import *
from .forms import *
from accounts.models import *
from accounts.serializer import *

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


status_for_filter_not_include = {
    'purchase_request':['Completed'],
    'purchase_inquiry':['Cancelled','Rejected','Completed','Closed'],
    'sales_order':['cancelled','Completed']
}

titles_for_tables = {
    'user': 'User',
    'department': 'Department',
    'subdivision': 'Division',
    'userrole': 'User Role',
    'branch': 'Branch',
    'measuredunits': 'Measurement Units',
    'currency': 'Currency',
    'partytype': 'Party Type',
    'country': 'Country',
    'parties': 'Party',
    'product': 'Product',
    'rawmaterial': 'Raw material',
    'productionphase': 'Phase',
    'state': 'State',
    # 'erp_role': 'role',
    'transfer_request': 'Inventory Transfer',
    'purchase_order': "Purchase order",
    'sales_order': "Sales order",
    'production_order': 'Production Order',
    'rm_accessories_group': 'Raw material / Assories Group',
    'purchase_request':'Purchase Request',
    'purchase_inquiry':'Purchase Inquiry',
    'payment_mode':'Payment Mode',
    'mode_of_receipt':"Mode of receipt",
    'grn':'GRN'
}

model_for_dropdown = {
    'user': 'name',
    'department': 'name',
    'subdivision': 'name',
    'userrole': 'role',
    'branch': 'branch_name',
    'measuredunits': 'measured_unit_name',
    'currency': 'currency_name',
    'partytype': 'party_type',
    'country': 'country_name',
    'parties': 'party_name',
    'product': 'product_name',
    'rawmaterial': 'rm_name',
    'productionphase': 'phase_name',
    'state': 'state_name',
    'erp_role': 'role',
    'transfer_request': 'request_id',
    'purchase_order': "purchase_order_no",
    'sales_order': "sales_order_no",
    'production_order': 'production_number',
    'rm_accessories_group': 'group_name',
    'purchase_request':'purchase_request_no',
    'purchase_inquiry':'purchase_inquiry_no',
    'payment_mode':'payment_mode',
    'mode_of_receipt':"mode_of_receipt",
    'grn':'grn_no'
}


class Paginate(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    # page_query_param = 'p'
    max_page_size = 1

    def get_paginated_response(self, data):
        # print(data)
        return Response({
            'links': {
                'previous': self.get_previous_link(),
                'next': self.get_next_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })
