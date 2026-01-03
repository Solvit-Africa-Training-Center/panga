from django.urls import path
from .views import *

# app_name = 'properties'

urlpatterns = [
    path('', home, name='home'),

    path('about/', about_us, name='about'),
    path('faq/', faq, name='faq'),
    path('contact/', contact, name='contact'),

    path("search/", search_results, name="search_results"),
    path('houses/<int:pk>/', house_detail, name='house_detail'),
    path('all_houses', all_houses, name='all_houses'),


    path('add/', add_house, name='add_house'),
    path('edit/<int:house_id>/', edit_house, name='edit_house'),
    path('delete/<int:house_id>/', delete_house, name='delete_house'),
    path('my-properties/', landlord_properties, name='landlord_properties'),


    path('api/provinces/', get_provinces, name='get_provinces'),
    path('api/cities/', get_cities, name='get_cities'),
    path('api/districts/', get_districts, name='get_districts'),
    path('api/sectors/', get_sectors, name='get_sectors'),
    path('api/cells/', get_cells, name='get_cells'),
    path('api/villages/', get_villages, name='get_villages'),

    path('reserve/<int:house_id>/', create_reservation, name='create_reservation'),
    path('visit-request/<int:house_id>/',
         create_visit_request, name='create_visit_request'),
    path('my-reservations/', my_reservations, name='my_reservations'),
    path('my-visit-requests/', my_visit_requests, name='my_visit_requests'),
    path('cancel-reservation/<int:reservation_id>/',
         cancel_reservation, name='cancel_reservation'),
    path('cancel-visit-request/<int:visit_request_id>/',
         cancel_visit_request, name='cancel_visit_request'),

    path(
        'landlord/reservations/', landlord_reservations, name='landlord_reservations'
    ),
    path(
        'landlord/visit-requests/', landlord_visit_requests, name='landlord_visit_requests'),



]
