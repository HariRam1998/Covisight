from django.urls import path, re_path, include
from . import views

# app_name = 'main'
urlpatterns = [
    path('cowinapi/', views.cowin, name= 'cowin'),
    path('cowintable/', views.cowintable, name= 'cowintable'),
    path('covidanalysis/', views.covidanalysis, name= 'covidanalysis'),
]