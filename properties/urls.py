# properties/urls.py
from django.urls import path
from .views import *

# app_name = 'properties'

urlpatterns = [
    path('', home, name='home'),

    # path('location/', views.houses_by_location, name='houses_by_location'),

    path('about/', about_us, name='about'),
    path('faq/', faq, name='faq'),
    path('contact/', contact, name='contact'),
    path('house_create/', house_create, name='house_create'),
    path('see_results/', see_results, name='results'),
    path("search/", search_results, name="search_results"),
    path('houses/<int:pk>/', house_detail, name='house_detail'),
    path('all_houses', all_houses, name='all_houses'),
    path('landlord/', landlord, name='landlord')


                 ]
