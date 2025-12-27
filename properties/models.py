from django.db import models
import datetime
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    name = models.CharField(max_length=100, default="Rwanda")
    
    def __str__(self):
        return self.name

class Province(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.country.name})"

class District(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.province.name})"      

    
class Sector(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sectors')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.district.name})"
class Cell(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='cells')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.sector.name})" 
     
class Village(models.Model):
   
    cell = models.ForeignKey('Cell', on_delete=models.CASCADE, related_name='villages')
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

class House(models.Model):
    housing_types = [
        ('Single Room','Single Room'),
        ('Apartment','Apartment'),
        ('House','House'),
        ('Villa','Villa'),
        ('Studio','Studio'),
        ('Duplex','Duplex'),
        ('Condo','Condo'),
        ('Townhouse','Townhouse'),
         ('Other','Other'),   
    ]
    house_status = [
        ('Available','Available'),
        ('Rented','Rented'),
        ('Under Maintenance','Under Maintenance'),

    ]

    type = models.CharField(max_length=50,  choices=housing_types, default='House') 
    status = models.CharField(max_length=50,  choices=house_status, default='Available')

    date_of_listing = models.DateTimeField(auto_now_add=True, editable=False, null=True)    
    name = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='', null=True, blank=True)
    location = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='houses')
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    neighborhood = models.CharField(max_length=100,  null=True, blank=True)
    street_address = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField()

    @classmethod
    def search(cls, query_text):        
        return cls.objects.filter(
            Q(name__icontains=query_text) |
            Q(description__icontains=query_text) |
            Q(location__name__icontains=query_text) |  # Village name
            Q(location__cell__name__icontains=query_text) |  # Cell name
            Q(location__cell__sector__name__icontains=query_text) |  # Sector name
            Q(location__cell__sector__district__name__icontains=query_text) |  # District name
            Q(street_address__icontains=query_text) |
            Q(neighborhood__icontains=query_text) |
            Q(type__icontains=query_text),
            is_active=True
        ).select_related(
            'location',
            'location__cell',
            'location__cell__sector',
            'location__cell__sector__district'
        ).distinct()


class ListingImage(models.Model):
    listing = models.ForeignKey(House, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='')
    is_main = models.BooleanField(default=True)

    def __str__(self):
        return f"Image for {self.listing.name}"



    