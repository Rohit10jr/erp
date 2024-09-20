from django.urls import path, include
from .views import PurchaseRequestAPI, DebitNotesAPI, InventoryTransferAPI, InventoryDetailsAPI,InventoryUpdate,FileUploadAPI
# from .GRNViews import GRNCreateAPI
# from .views import *

urlpatterns = [
    path('purchase-request', PurchaseRequestAPI.as_view()),
    path('inventory-transfer', InventoryTransferAPI.as_view()),
    path('debit-note', DebitNotesAPI.as_view()),
    # path('goods-receipt-note', GRNCreateAPI.as_view()),
    path('inventory-details', InventoryDetailsAPI.as_view()),
    path('inventory-update',InventoryUpdate.as_view()),
    path('upload-file',FileUploadAPI.as_view())
]
