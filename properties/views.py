from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 
from decimal import Decimal
from .models import House, Village, Cell, Sector, District, Province, City, Country
from utils.general_search import search_houses


def search_results(request):
    houses = search_houses(request)
    number = houses.count()
    paginator = Paginator(houses, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    districts = District.objects.all()

    context = {
        "houses": page_obj,
        "districts": districts,
        "total_results": paginator.count,
        "query": request.GET.get("q"),
        "number": number
    }

    return render(request, "properties/all/search_results.html", context)


def home(request):
    houses = (
        House.objects
        .filter(is_active=True, status="Available")
        .order_by("-date_of_listing")[:6]
    )
    housing_types = House.housing_types,

    districts = District.objects.all()
    context = {
        "houses": houses,
        "districts": districts,
        "housing_types": housing_types,
    }

    return render(request, "properties/homepage.html", context)

def house_create(request):
    if request.method == 'POST':
        # Get location names from form (users typed these in)
        village_name = request.POST.get('village')
        cell_name = request.POST.get('cell')
        sector_name = request.POST.get('sector')
        district_name = request.POST.get('district')
        city_name = request.POST.get('city')
        province_name = request.POST.get('province')
        country_name = request.POST.get('country')
        
        if not all([village_name, cell_name, sector_name, district_name, city_name, province_name, country_name]):
            messages.error(request, 'Please enter all location fields')
            return redirect('house_create')
        
        # Create location objects if they don't exist (bottom-up approach)
        country, _ = Country.objects.get_or_create(name=country_name)
        province, _ = Province.objects.get_or_create(name=province_name, country=country)
        city, _ = City.objects.get_or_create(name=city_name, province=province)
        district, _ = District.objects.get_or_create(name=district_name, city=city)
        sector, _ = Sector.objects.get_or_create(name=sector_name, district=district)
        cell, _ = Cell.objects.get_or_create(name=cell_name, sector=sector)
        village, _ = Village.objects.get_or_create(name=village_name, cell=cell)
        
        # Get house data
        type = request.POST.get('type')
        status = request.POST.get('status', 'Available')
        label = request.POST.get('label')
        monthly_rent = request.POST.get('monthly_rent', '0.00')
        neighborhood = request.POST.get('neighborhood')
        street_address = request.POST.get('street_address', 'KG 702 St')
        description = request.POST.get('description', '')
        n_bed_rooms = request.POST.get('n_bed_rooms', '1')
        n_bath_rooms = request.POST.get('n_bath_rooms', '1')
        surface = request.POST.get('surface', '1')
        parkings = request.POST.get('parkings', '0')
        has_wifi = request.POST.get('has_wifi') == 'on'
        on_map = request.POST.get('on_map')
        
        # Create house
        house = House.objects.create(
            type=type,
            status=status,
            label=label,
            location=village,
            monthly_rent=Decimal(monthly_rent),
            neighborhood=neighborhood,
            street_address=street_address,
            description=description,
            n_bed_rooms=int(n_bed_rooms),
            n_bath_rooms=int(n_bath_rooms),
            surface=int(surface),
            parkings=int(parkings),
            has_wifi=has_wifi,
            on_map=on_map,
            main_image=request.FILES.get('main_image'),
            image_one=request.FILES.get('image_one'),
            image_two=request.FILES.get('image_two'),
            image_three=request.FILES.get('image_three'),
            image_four=request.FILES.get('image_four'),
        )
        
        messages.success(request, 'House is listed successfully!')
        return redirect('landlord')
    
    # GET request - show all houses
    houses = House.objects.all().order_by('-date_of_listing')
    
    context = {
        'title': 'List Your Property',
        'houses': houses,
    }
    return render(request, 'properties/house_create.html', context)  


def all_houses(request):
    """houses = (
        House.objects
        .filter(is_active=True, status="Available")
        .select_related(
            "location",
            "location__cell",
            "location__cell__sector",
            "location__cell__sector__district",
        )

    )"""
    houses = search_houses(request)
    number = houses.count()
    paginator = Paginator(houses, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    districts = District.objects.all()

    context = {
        "houses": page_obj,
        "districts": districts,
        "total_results": paginator.count,
        "query": request.GET.get("q"),
        "number": number
    }

    return render(request, "properties/all/all_houses.html", context)

# =======


def house_detail(request, pk):
    house = get_object_or_404(
        House.objects
        .select_related(
            "location",
            "location__cell",
            "location__cell__sector",
            "location__cell__sector__district",
        ),
        pk=pk,
        is_active=True
    )
    context = {
        "house": house
    }

    return render(request, "properties/all/details_house.html", context)


def about_us(request):
    return render(request, "properties/gukodesha/about.html", {})


def faq(request):
    return render(request, "properties/gukodesha/faq.html", {})


def contact(request):
    return render(request, "properties/gukodesha/contact_us.html", {})


def see_results(request):
    return render(request, 'properties/all/search_results.html', {})

def landlord(request):
    houses = House.objects.all().order_by('-date_of_listing')
    districts= District.objects.all().order_by('name')
    
    # Calculate stats
    total_properties = houses.count()
    vacant_units = houses.filter(status='Available').count()
    rented_units = houses.filter(status='Rented').count()
    total_revenue = sum(house.monthly_rent for house in houses.filter(status='Rented'))

    
    # Calculate vacancy rate
    if total_properties > 0:
        vacancy_rate = (vacant_units / total_properties) * 100
    else:
        vacancy_rate = 0
    
    context = {
        'houses': houses,
        'districts': districts,
        'total_properties': total_properties,
        'vacant_units': vacant_units,
        'rented_units': rented_units,
        'total_revenue': total_revenue,
        'vacancy_rate': vacancy_rate,
    }
    
    return render(request, 'properties/landlord/my_properties.html', context)
"""
@login_required
def house_list(request):
    # Display list of all houses with search and filtering
    houses = House.objects.filter(is_active=True).select_related(
        'location').order_by('-date_of_listing')

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


@login_required
def house_create(request):
    #Create a new house listing
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        image_formset = ListingImageFormSet(request.POST, request.FILES)

        if form.is_valid() and image_formset.is_valid():
            house = form.save(commit=False)

            location_text = form.cleaned_data.get('location_text')
            if location_text:
                village = Village.objects.filter(
                    name__iexact=location_text).first()
                if not village:

                    country, _ = Country.objects.get_or_create(
                        name="Rwanda",
                        defaults={'code': 'RW'}
                    )
                    province, _ = Province.objects.get_or_create(
                        name="User Specified",
                        country=country
                    )
                    district, _ = District.objects.get_or_create(
                        name="User Specified",
                        province=province
                    )
                    sector, _ = Sector.objects.get_or_create(
                        name="User Specified",
                        district=district
                    )
                    cell, _ = Cell.objects.get_or_create(
                        name="User Specified",
                        sector=sector
                    )

                    village = Village.objects.create(
                        name=location_text,
                        cell=cell
                    )

                house.location = village

            house.save()

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


@login_required
def house_detail(request, pk):
    #Display details of a specific house listing
    house = get_object_or_404(House, pk=pk, is_active=True)
    images = ListingImage.objects.filter(listing=house)

    context = {
        'house': house,
        'images': images
    }
    return render(request, 'properties/house_detail.html', context)


@login_required
def house_update(request, pk):
    #Update an existing house listing
    house = get_object_or_404(House, pk=pk)

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES, instance=house)
        image_formset = ListingImageFormSet(
            request.POST, request.FILES, instance=house)

        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()

            messages.success(request, 'House listing updated successfully!')
            return redirect('properties:house_create', pk=house.pk)
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


@login_required
def house_delete(request, pk):
    #Delete a house listing
    house = get_object_or_404(House, pk=pk)

    if request.method == 'POST':
        house.delete()
        messages.success(request, 'House listing deleted successfully!')
        return redirect('properties:house_list')

    context = {'house': house}
    return render(request, 'properties/house_confirm_delete.html', context)


@login_required
def house_search(request):
    #Search houses by query text
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


@login_required
def available_house(request):
    # Display only available houses
    houses = House.objects.filter(
        status='Available', is_active=True).order_by('-date_of_listing')

    paginator = Paginator(houses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Available Houses',
        'total_count': houses.count()
    }
    return render(request, 'properties/house_list.html', context)


@login_required
def house_by_type(request, house_type):
    # Display houses filtered by type
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
"""
