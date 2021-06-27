from django.contrib import admin
from django.urls import path
from . import views

# app_name = 'main'
urlpatterns = [
    path('register/', views.register, name= 'user_register'),
    path('login/', views.login1, name= 'user_login'),
    path('logout/', views.logoutfun, name= 'user_logout'),
    path('validate_username/', views.validate_username, name='validate_username'),
    path('validate_email/', views.validate_email, name='validate_email'),
    path('validate_loginemail/', views.validate_loginemail, name='validate_loginemail'),
    path('validate_fpassword/',views.validate_fpassword, name='validate_fpassword'),
    path('fpassword/',views.fpassword, name='user_fpassword'),
    path('cfpassword/',views.cfpassword, name='ccfpassword'),
    path('account/',views.useraccount, name='user_account'),
    path('profile/',views.userprofile, name='user_profile'),
    path('accountcp/',views.useraccountcp, name='user_accountcp'),
    path('notification/', views.notification, name='notification'),
]
