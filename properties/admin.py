from django.contrib import admin
from .models import Country, Province, District, Sector, Cell, Village, House, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 5 




@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    # 1. Columns shown in the main list table
    search_fields =( 'label', 'neighborhood', 'location__name', 'location__cell__name', 'location__cell__sector__district__name')
    list_display = ( 'type', 'status', 'monthly_rent', 'location', 'date_of_listing')
 
    list_filter = ('type', 'status', 'location__cell__sector__district', 'date_of_listing')
    
    search_fields = ( 'description', 'neighborhood')    
 
    readonly_fields = ('date_of_listing',)    

    inlines = [ListingImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image', 'type', 'status',  'description')
        }),
        ('Location & Pricing', {
            'fields': ('location', 'neighborhood', 'street_address', 'monthly_rent')
        }),
        ('Meta Data', {
            'fields': ('is_active', 'date_of_listing'),
        }),
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'province')
    list_filter = ('province',)

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'district')
    list_filter = ('district__province',)

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector')

@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('name', 'cell')
    search_fields = ('name',)
