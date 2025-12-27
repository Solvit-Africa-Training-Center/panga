# properties/urls.py
from django.urls import path
from . import views

app_name = 'properties'
urlpatterns = [

    path('', views.home, name='home'),
    path('create/', views.house_create, name='house_create'),
    path('list/', views.house_list, name='house_list'),
    path('available/', views.available_house, name='available_house'),
    path('search/', views.house_search, name='house_search'),   
    path('<int:pk>/', views.house_detail, name='house_detail'),
    path('<int:pk>/update/', views.house_update, name='house_update'),
    path('<int:pk>/delete/', views.house_delete, name='house_delete'),   
    path('type/<str:house_by_type>/', views.house_by_type, name='house_by_type'), 
    #path('location/', views.houses_by_location, name='houses_by_location'),
    
  
]
