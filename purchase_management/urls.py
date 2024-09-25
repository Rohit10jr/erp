from django.urls import path, include
from .views import *

# from .views import *
urlpatterns = [
    path('purchase-order',PurchaseOrderView.as_view()),
    path('purchase-inquiry',PurchaseInquiryView.as_view())
]