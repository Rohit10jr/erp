from functools import lru_cache, reduce
import operator

data_nav = {
    "dashboard":{
    'dashboard':{
  "label": "Dashboard",
      "url": "/dashboard",
    },
  }, 'reports':{
  'inventory_list':{
        "label": "Inventory Report",
      "url": "/reports?page_name=inventory_list",
    },
       'wip_inventory':{
        "label": "WIP Inventory Report",
      "url": "/reports?page_name=wip_inventory",
    },
       'production_order':{
        "label": "Production Order Report",
      "url": "/reports?page_name=production_order",
    },
       'productivity':{
        "label": "Productivity Report",
      "url": "/reports?page_name=productivity",
    },
       'sales_order':{
        "label": "Sales Order Report",
      "url": "/reports?page_name=sales_order",
    },
       'purchase_order':{
        "label": "Purchase Order Report",
      "url": "/reports?page_name=purchase_order",
    },
       'inventory_transfer':{
        "label": "Inventory Transfer Report",
      "url": "/reports?page_name=inventory_transfer",
    },
       'payables':{
        "label": "Payables Report",
      "url": "/reports?page_name=payables",
    },
       'receivables':{
        "label": "Receivables Report",
      "url": "/reports?page_name=receivables",
    },
    }, 
    "user": {
    "branch": {
     "label": "Branch",
      "url": "/data-management/home?model_name=branch",
    },
    "department": {
      "label": "Department",
      "url": "/data-management/home?model_name=department",
    },
    "division": {
      "label": "Division",
      "url": "/data-management/home?model_name=subdivision",
    },
    "userrole": {
      "label": "User Role",
      "url": "/data-management/home?model_name=userrole",
    },
    "user": {
      "label": "User",
      "url": "/data-management/home?model_name=user",
    },
  },
   "sales": {
    "new-sales-order": {
      "label": "New Sales Order",
      "url": "/new-sales-order",
    },
    "update-sales-order": {
      "label": "Update Sales Order",
      "url": "/sales-order",
    },
  },
}
@lru_cache()
def hasaccess(request):
    try:
        user,params=request.user,request.query_params
        if not user.is_superuser:
            useraccess=reduce(operator.concat,list(user.role.access.values()))
            path=request.path.split('/')[-1]
            if model := params.get('model') or params.get('model_name') or path:
                return bool(model in useraccess or (path =='home' and not request.query_params))
            return False        
        return True
    except Exception as e:
        print(e)
        return False
