from django.urls import path
from .views import home

# app_name = 'accounts'

urlpatterns = [
    path('', home, name='home'),

]
