from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kyd_app import views


urlpatterns = [
    path('user/<user_id>', views.GetUser.as_view()),
    path('users/register', views.RegisterUser.as_view()),
    path('devices/user/<user_id>', views.GetDevicesByUser.as_view()),
    path('device/<device_id>', views.GetDevice.as_view()),
    path('devices/create', views.CreateDevice.as_view()),
    path('devices/register', views.RegisterDevice.as_view()),
    path('devices/verify', views.VerifyDevice.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
