from django.contrib import admin
from django.urls import path, re_path, include
from . import views

# app_name = 'main'
urlpatterns = [
    path('createpost/', views.createpost, name= 'create_post'),
    path('viewpost/', views.viewpost, name= 'view_post'),
    path('post/<int:id>/<slug:slug>', views.fullviewpost, name = 'fullviewpost'),
    path('bloghome/', views.bloghome, name= 'bloghome'),
]