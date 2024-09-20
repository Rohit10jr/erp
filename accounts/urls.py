from django.urls import path, include
# from api.api import GetPostAPI, PutAPI
from .views import *

urlpatterns = [
    path('signup/', UserRegistration.as_view()),
    path('login/', Login.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('schedule_mail/', ScheduleMail.as_view()),
    # path('schedule_status_update',schedule_hourly_status.as_view()),
    path("menu/",MenuAccess.as_view()),
    path('config-create/',ConfigCreateAPI.as_view())

]
