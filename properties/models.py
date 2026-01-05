from django.db import models
import datetime
from decimal import Decimal
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from accounts.models import User



class Country(models.Model):
    name = models.CharField(max_length=100, default="Rwanda")

    def __str__(self):
        return self.name


class Province(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.country.name})"


class City(models.Model):
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.province.name})"


class District(models.Model):
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class Sector(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='sectors')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class Cell(models.Model):
    sector = models.ForeignKey(
        Sector, on_delete=models.CASCADE, related_name='cells')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.sector.name})"


class Village(models.Model):

    cell = models.ForeignKey(
        Cell, on_delete=models.CASCADE, related_name='villages')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class House(models.Model):
    housing_types = (
        ('Single Room', 'Single Room'),
        ('Apartment', 'Apartment'),
        ('House', 'House'),
        ('Villa', 'Villa'),
        ('Studio', 'Studio'),
        ('Duplex', 'Duplex'),
        ('Condo', 'Condo'),
        ('Townhouse', 'Townhouse'),
        ('Office', 'Office'),
    )
    house_status = [
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Under Maintenance', 'Under Maintenance'),
        

    ]

    type = models.CharField(
        max_length=50,  choices=housing_types, default='House')
    status = models.CharField(
        max_length=50,  choices=house_status, default='Available')

    date_of_listing = models.DateTimeField(
        auto_now_add=True, editable=False, null=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    landlord = models.ForeignKey(
    User, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='houses')
    monthly_rent = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=Decimal("0.00")
                             )
    neighborhood = models.CharField(max_length=100,  null=True, blank=True)
    street_address = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    n_bed_rooms = models.IntegerField(
        default=1, null=True, blank=True)
    n_bath_rooms = models.IntegerField(
        default=1, null=True, blank=True)
    surface = models.IntegerField(
        default=1, null=True, blank=True)
    has_wifi = models.BooleanField(default=False)
    parkings = models.IntegerField(default=0, null=True, blank=True)
    main_image = models.ImageField(upload_to='houses', null=True, blank=True)
    image_one = models.ImageField(upload_to='houses', null=True, blank=True)
    image_two = models.ImageField(upload_to='houses', null=True, blank=True)
    image_three = models.ImageField(upload_to='houses', null=True, blank=True)
    image_four = models.ImageField(upload_to='houses', null=True, blank=True)
    on_map = models.TextField(null=True, blank=True)


class Reservation(models.Model):
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reservations')
    start_date = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation - {self.house.label} by {self.user}"


class VisitRequest(models.Model):
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name='visit_requests')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='visit_requests')
    visit_date = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit request - {self.house.label} by {self.user}"
