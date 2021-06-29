from django.contrib import admin
from django.urls import path, re_path, include
from . import views

# app_name = 'main'
urlpatterns = [
    path('', views.home, name= 'user-home'),
    path('news/',views.news, name='user_news'),
    path('faq/',views.faq, name='home_faq'),
    path('covidlung/', views.covidlung, name='covidlung'),
    path('contactus/',views.contact, name='home_contact'),
    path('contactform/',views.contactform, name='contactform'),
    path('publiccontactform/', views.publiccontactform, name='publiccontactform'),
    path('search/', views.search, name='search'),
    path('aboutus/', views.aboutus, name='aboutus'),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
]
