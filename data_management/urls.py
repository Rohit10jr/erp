from django.urls import path, include

from .views import (
    CRUDAPI,
    ProductionFlowView,
    PreferredSuppliersGETAPI,
    # DropdownView,
    # load_db
)
# from .DashboardAPI import DashboardGETAPI

urlpatterns = [

    path('master-data-management', CRUDAPI.as_view()),
    path('production-flow', ProductionFlowView.as_view()),
    path('supplier_get',PreferredSuppliersGETAPI.as_view()),
    # path('dropdown/', DropdownView),
    # path('dashboard',DashboardGETAPI.as_view()),
    # path('reports',ReportsAPI.as_view()),
    # path('download-report',DownloadReport.as_view())
    # path('load',load_db)
]
