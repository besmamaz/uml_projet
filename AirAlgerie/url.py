from django.urls import path
from .views import  search_flights

urlpatterns = [
    
    path('search_vol/', search_flights, name='search_vol'),
    
]