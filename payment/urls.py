from django.urls import path
from .views import initiate_payment, callback,databasedel

urlpatterns = [
    path('pay/', initiate_payment, name='pay'),
    path('callback/', callback, name='callback'),
    path('databasedel/', databasedel, name= 'databasedel'),
]