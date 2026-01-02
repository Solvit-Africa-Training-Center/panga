from django.contrib import admin
from .models import Country, Province, District, Sector, Cell, Village, House, City

admin.site.register(House)
admin.site.register(Country)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(District)
admin.site.register(Sector)
admin.site.register(Cell)
admin.site.register(Village)
