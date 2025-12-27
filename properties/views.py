from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import House, ListingImage, Province, District, Sector, Cell, Village
from .forms import HouseForm, ListingImageFormSet, HouseSearchForm 

def home(request):
    return render(request, "properties/homepage.html", {})

def house_list(request):
    #Display list of all houses with search and filtering
    houses = House.objects.filter(is_active=True).select_related('location').order_by('-date_of_listing')
    
    form = HouseSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        house_type = form.cleaned_data.get('type')
        status = form.cleaned_data.get('status')
        min_rent = form.cleaned_data.get('min_rent')
        max_rent = form.cleaned_data.get('max_rent')
        province = form.cleaned_data.get('province')
        district = form.cleaned_data.get('district')
        sector = form.cleaned_data.get('sector')
        cell = form.cleaned_data.get('cell')
        village = form.cleaned_data.get('village')
        
        
        if query:
            houses = houses.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__name__icontains=query) |
                Q(street_address__icontains=query) |
                Q(neighborhood__icontains=query)
            )
        
        if house_type:
            houses = houses.filter(type=house_type)
        
        if status:
            houses = houses.filter(status=status)
        
        if min_rent:
            houses = houses.filter(monthly_rent__gte=min_rent)
        
        if max_rent:
            houses = houses.filter(monthly_rent__lte=max_rent)
        
        if province:
            houses = houses.filter(
                location__cell__sector__district__province=province
            )
        
        if district:
            houses = houses.filter(
                location__cell__sector__district=district
            )
        
        if sector:
            houses = houses.filter(location__cell__sector=sector)
    
    paginator = Paginator(houses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_count': houses.count()
    }
    return render(request, 'properties/house_list.html', context)

def house_create(request):
    """Create a new house listing"""
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        image_formset = ListingImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and image_formset.is_valid():
            house = form.save()
            image_formset.instance = house
            image_formset.save()
            
            messages.success(request, 'House listing created successfully!')
            return redirect('properties:house_detail', pk=house.pk)  
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HouseForm()
        image_formset = ListingImageFormSet()
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'title': 'Create New Listing'
    }
    return render(request, 'properties/house_create.html', context)

def house_detail(request, pk):
    """Display details of a specific house listing"""
    house = get_object_or_404(House, pk=pk, is_active=True)
    images = ListingImage.objects.filter(listing=house)
    
    context = {
        'house': house,
        'images': images
    }
    return render(request, 'properties/house_detail.html', context)


def house_update(request, pk):
    """Update an existing house listing"""
    house = get_object_or_404(House, pk=pk)
    
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES, instance=house)
        image_formset = ListingImageFormSet(request.POST, request.FILES, instance=house)
        
        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            
            messages.success(request, 'House listing updated successfully!')
            return redirect('properties:house_create', pk=house.pk)  # Add 'properties:' here
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HouseForm(instance=house)
        image_formset = ListingImageFormSet(instance=house)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'house': house,
        'title': 'Update Listing'
    }
    return render(request, 'properties/house_create.html', context)


def house_delete(request, pk):
    """Delete a house listing"""
    house = get_object_or_404(House, pk=pk)
    
    if request.method == 'POST':
        house.delete()
        messages.success(request, 'House listing deleted successfully!')
        return redirect('properties:house_list')  
    
    context = {'house': house}
    return render(request, 'properties/house_confirm_delete.html', context)


def house_search(request):
    """Search houses by query text"""
    query = request.GET.get('q', '')
    
    if query:
        houses = House.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(location__name__icontains=query) |
            Q(location__cell__name__icontains=query) |
            Q(location__cell__sector__name__icontains=query) |
            Q(location__cell__sector__district__name__icontains=query) |
            Q(street_address__icontains=query) |
            Q(neighborhood__icontains=query) |
            Q(type__icontains=query),
            is_active=True
        ).select_related(
            'location',
            'location__cell',
            'location__cell__sector',
            'location__cell__sector__district'
        ).distinct().order_by('-date_of_listing')
        
        # Debug: Print what we're searching for
        print(f"Searching for: {query}")
        print(f"Found {houses.count()} houses")
        print(houses)
        
    else:
        houses = House.objects.filter(is_active=True).select_related(
            'location',
            'location__cell',
            'location__cell__sector',
            'location__cell__sector__district'
        ).order_by('-date_of_listing')
    
    paginator = Paginator(houses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_count': houses.count()
    }
    return render(request, 'properties/house_search.html', context)
    


# AJAX views for cascading dropdowns
def load_provinces(request):
    #Load provinces based on selected country
    country_id = request.GET.get('country_id')
    provinces = Province.objects.filter(country_id=country_id).order_by('name')
    return JsonResponse(list(provinces.values('id', 'name')), safe=False)


def load_districts(request):
   #Load districts based on selected province
    province_id = request.GET.get('province_id')
    districts = District.objects.filter(province_id=province_id).order_by('name')
    return JsonResponse(list(districts.values('id', 'name')), safe=False)


def load_sectors(request):
    #Load sectors based on selected district
    district_id = request.GET.get('district_id')
    sectors = Sector.objects.filter(district_id=district_id).order_by('name')
    return JsonResponse(list(sectors.values('id', 'name')), safe=False)


def load_cells(request):
   #Load cells based on selected sector
    sector_id = request.GET.get('sector_id')
    cells = Cell.objects.filter(sector_id=sector_id).order_by('name')
    return JsonResponse(list(cells.values('id', 'name')), safe=False)


def load_villages(request):
   #Load villages based on selected cell
    cell_id = request.GET.get('cell_id')
    villages = Village.objects.filter(cell_id=cell_id).order_by('name')
    return JsonResponse(list(villages.values('id', 'name')), safe=False)


def houses_by_location(request):
    #Filter houses by location hierarchy
    village_id = request.GET.get('village')
    cell_id = request.GET.get('cell')
    sector_id = request.GET.get('sector')
    district_id = request.GET.get('district')
    province_id = request.GET.get('province')
    
    houses = House.objects.filter(is_active=True)
    
    if village_id:
        houses = houses.filter(location_id=village_id)
    elif cell_id:
        houses = houses.filter(location__cell_id=cell_id)
    elif sector_id:
        houses = houses.filter(location__cell__sector_id=sector_id)
    elif district_id:
        houses = houses.filter(location__cell__sector__district_id=district_id)
    elif province_id:
        houses = houses.filter(location__cell__sector__district__province_id=province_id)
    
    context = {
        'properties': houses,
        'location_filter': True
    }
    return render(request, 'properties/house_list.html', context)


def available_house(request):
    #Display only available houses
    houses = House.objects.filter(status='Available', is_active=True).order_by('-date_of_listing')
    
    paginator = Paginator(houses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Available Houses',
        'total_count': houses.count()
    }
    return render(request, 'properties/house_list.html', context)


def house_by_type(request, house_type):
    #Display houses filtered by type
    houses = House.objects.filter(
        type=house_type,
        is_active=True
    ).order_by('-date_of_listing')
    
    paginator = Paginator(houses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': f'{house_type} Listings',
        'total_count': houses.count()
    }
    return render(request, 'properties/house_list.html', context)











