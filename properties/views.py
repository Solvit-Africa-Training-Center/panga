from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Country, Province, City, District, Sector, Cell, Village, Reservation, VisitRequest
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from utils.general_search import search_houses
from datetime import datetime, date


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
        .order_by("-date_of_listing")[:3]
    )
    housing_types = House.housing_types,

    districts = District.objects.all()
    context = {
        "houses": houses,
        "districts": districts,
        "housing_types": housing_types,
    }

    return render(request, "properties/homepage.html", context)


def all_houses(request):

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


@login_required
def add_house(request):
    if request.user.role != "LANDLORD":
        return redirect('home')
    if request.method == 'POST':
        try:
            house_type = request.POST.get('property_type')
            street_address = request.POST.get('street_address')
            neighborhood = request.POST.get('neighborhood')
            village_id = request.POST.get('village')
            n_bed_rooms = request.POST.get('bedrooms')
            n_bath_rooms = request.POST.get('bathrooms')
            surface = request.POST.get('surface')
            description = request.POST.get('description')
            monthly_rent = request.POST.get('monthly_rent')
            label = request.POST.get('label')

            has_wifi = request.POST.get('wifi') == 'on'
            parkings = int(request.POST.get('parkings', 0))

            on_map = request.POST.get('on_map', '')

            if not all([house_type, village_id, n_bed_rooms, n_bath_rooms, surface, description, monthly_rent]):
                messages.error(request, 'Please fill all required fields.')
                return redirect('add_house')

            village = get_object_or_404(Village, id=village_id)

            house = House.objects.create(
                type=house_type,
                landlord=request.user,
                location=village,
                street_address=street_address,
                neighborhood=neighborhood,
                n_bed_rooms=int(n_bed_rooms),
                n_bath_rooms=int(n_bath_rooms),
                surface=int(surface),
                description=description,
                monthly_rent=float(monthly_rent),
                label=label,
                has_wifi=has_wifi,
                parkings=parkings,
                on_map=on_map,
                status='Available'
            )

            if 'main_image' in request.FILES:
                house.main_image = request.FILES['main_image']
            if 'image_one' in request.FILES:
                house.image_one = request.FILES['image_one']
            if 'image_two' in request.FILES:
                house.image_two = request.FILES['image_two']
            if 'image_three' in request.FILES:
                house.image_three = request.FILES['image_three']
            if 'image_four' in request.FILES:
                house.image_four = request.FILES['image_four']

            house.save()

            messages.success(
                request, f'Property "{house.label or house.type}" has been added successfully!')
            return redirect('landlord_properties')

        except Exception as e:
            messages.error(request, f'Error adding property: {str(e)}')
            return redirect('add_house')

    countries = Country.objects.all()
    return render(request, 'properties/landlord/add_house.html', {
        'countries': countries,
        'edit_mode': False
    })


@login_required
def edit_house(request, house_id):
    if request.user.role != "LANDLORD":
        return redirect('home')
    house = get_object_or_404(House, id=house_id, landlord=request.user)

    if request.method == 'POST':
        try:
            house.type = request.POST.get('property_type')
            house.street_address = request.POST.get('street_address')
            house.neighborhood = request.POST.get('neighborhood')
            house.n_bed_rooms = int(request.POST.get('bedrooms'))
            house.n_bath_rooms = int(request.POST.get('bathrooms'))
            house.surface = int(request.POST.get('surface'))
            house.description = request.POST.get('description')
            house.monthly_rent = float(request.POST.get('monthly_rent'))
            house.label = request.POST.get('label')
            house.has_wifi = request.POST.get('wifi') == 'on'
            house.parkings = int(request.POST.get('parkings', 0))
            house.on_map = request.POST.get('on_map', '')

            village_id = request.POST.get('village')
            if village_id:
                house.location = get_object_or_404(Village, id=village_id)

            if 'main_image' in request.FILES:
                house.main_image = request.FILES['main_image']
            if 'image_one' in request.FILES:
                house.image_one = request.FILES['image_one']
            if 'image_two' in request.FILES:
                house.image_two = request.FILES['image_two']
            if 'image_three' in request.FILES:
                house.image_three = request.FILES['image_three']
            if 'image_four' in request.FILES:
                house.image_four = request.FILES['image_four']

            house.save()

            messages.success(
                request, f'Property "{house.label or house.type}" has been updated successfully!')
            return redirect('landlord_properties')

        except Exception as e:
            messages.error(request, f"Error updating property: {str(e)}")
            return redirect("edit_house", house_id=house_id)

    countries = Country.objects.all()

    village = house.location
    cell = village.cell
    sector = cell.sector
    district = sector.district
    city = district.city
    province = city.province
    country = province.country

    return render(request, 'properties/landlord/add_house.html', {
        'house': house,
        'countries': countries,
        'edit_mode': True,
        'selected_country': country,
        'selected_province': province,
        'selected_city': city,
        'selected_district': district,
        'selected_sector': sector,
        'selected_cell': cell,
        'selected_village': village,
    })


@login_required
@require_http_methods(["POST"])
def delete_house(request, house_id):
    if request.user.role != "LANDLORD":
        return redirect('home')
    house = get_object_or_404(House, id=house_id, landlord=request.user)

    try:
        house_label = house.label or house.type
        house.delete()
        messages.success(
            request, f'Property "{house_label}" has been deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting property: {str(e)}')

    return redirect('landlord_properties')


@require_http_methods(["GET"])
def get_provinces(request):
    country_id = request.GET.get('country_id')
    if country_id:
        provinces = Province.objects.filter(
            country_id=country_id).values('id', 'name')
        return JsonResponse({'provinces': list(provinces)})
    return JsonResponse({'provinces': []})


@require_http_methods(["GET"])
def get_cities(request):
    province_id = request.GET.get('province_id')
    if province_id:
        cities = City.objects.filter(
            province_id=province_id).values('id', 'name')
        return JsonResponse({'cities': list(cities)})
    return JsonResponse({'cities': []})


@require_http_methods(["GET"])
def get_districts(request):
    city_id = request.GET.get('city_id')
    if city_id:
        districts = District.objects.filter(
            city_id=city_id).values('id', 'name')
        return JsonResponse({'districts': list(districts)})
    return JsonResponse({'districts': []})


@require_http_methods(["GET"])
def get_sectors(request):
    district_id = request.GET.get('district_id')
    if district_id:
        sectors = Sector.objects.filter(
            district_id=district_id).values('id', 'name')
        return JsonResponse({'sectors': list(sectors)})
    return JsonResponse({'sectors': []})


@require_http_methods(["GET"])
def get_cells(request):
    sector_id = request.GET.get('sector_id')
    if sector_id:
        cells = Cell.objects.filter(sector_id=sector_id).values('id', 'name')
        return JsonResponse({'cells': list(cells)})
    return JsonResponse({'cells': []})


@require_http_methods(["GET"])
def get_villages(request):
    cell_id = request.GET.get('cell_id')
    if cell_id:
        villages = Village.objects.filter(cell_id=cell_id).values('id', 'name')
        return JsonResponse({'villages': list(villages)})
    return JsonResponse({'villages': []})


@login_required
def landlord_properties(request):
    if request.user.role != "LANDLORD":
        return redirect('home')
    houses = House.objects.filter(
        landlord=request.user).order_by('-date_of_listing')
    return render(request, 'properties/landlord/my_properties.html', {
        'houses': houses
    })


@login_required
@require_http_methods(["POST"])
def create_reservation(request, house_id):

    house = get_object_or_404(House, id=house_id)
    if house.status != 'Available':
        messages.error(
            request, 'This property is not available for reservation.')
        return redirect('house_detail', pk=house_id)

    if house.landlord == request.user:
        messages.error(request, 'You cannot reserve your own property.')
        return redirect('house_detail', pk=house_id)

    try:
        start_date_str = request.POST.get('start_date')
        guests = request.POST.get('guests')

        if not start_date_str or not guests:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('house_detail', pk=house_id)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('house_detail', pk=house_id)

        if start_date < date.today():
            messages.error(request, 'Please select a future date.')
            return redirect('house_detail', pk=house_id)

        try:
            guests = int(guests)
            if guests < 1:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Please enter a valid number of guests.')
            return redirect('house_detail', pk=house_id)

        existing_reservation = Reservation.objects.filter(
            house=house,
            user=request.user,
            start_date__gte=date.today()
        ).exists()

        if existing_reservation:
            messages.warning(
                request, 'You already have a pending reservation for this property.')
            return redirect('house_detail', pk=house_id)

        reservation = Reservation.objects.create(
            house=house,
            user=request.user,
            start_date=start_date,
            guests=guests
        )

        messages.success(
            request,
            f'Your reservation for {house.label or house.type} has been submitted! '
            f'The landlord will contact you soon.'
        )
        return redirect('my_reservations')

    except Exception as e:
        messages.error(request, f'Error creating reservation: {str(e)}')
        return redirect('house_detail', pk=house_id)


@login_required
@require_http_methods(["POST"])
def create_visit_request(request, house_id):
    house = get_object_or_404(House, id=house_id)

    if house.status != 'Available':
        messages.error(request, 'This property is not available for visits.')
        return redirect('house_detail', pk=house_id)

    if house.landlord == request.user:
        messages.error(
            request, 'You cannot request a visit to your own property.')
        return redirect('house_detail', pk=house_id)

    try:
        visit_date_str = request.POST.get('visit_date')
        guests = request.POST.get('guests')
        message = request.POST.get('message', '')

        if not visit_date_str or not guests:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('house_detail', pk=house_id)

        try:
            visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('house_detail', pk=house_id)

        if visit_date < date.today():
            messages.error(request, 'Please select a future date.')
            return redirect('house_detail', pk=house_id)

        try:
            guests = int(guests)
            if guests < 1:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Please enter a valid number of guests.')
            return redirect('house_detail', pk=house_id)

        existing_request = VisitRequest.objects.filter(
            house=house,
            user=request.user,
            visit_date__gte=date.today()
        ).exists()

        if existing_request:
            messages.warning(
                request, 'You already have a pending visit request for this property.')
            return redirect('house_detail', pk=house_id)

        visit_request = VisitRequest.objects.create(
            house=house,
            user=request.user,
            visit_date=visit_date,
            guests=guests,
            message=message
        )

        messages.success(
            request,
            f'Your visit request for {house.label or house.type} has been submitted! '
            f'The landlord will contact you to confirm the visit.'
        )
        return redirect('my_visit_requests')

    except Exception as e:
        messages.error(request, f'Error creating visit request: {str(e)}')
        return redirect('house_detail', pk=house_id)


@login_required
def my_reservations(request):

    reservations = Reservation.objects.filter(
        user=request.user
    ).select_related('house').order_by('-created_at')

    return render(request, 'properties/all/my_reservations.html', {
        'reservations': reservations
    })


@login_required
def my_visit_requests(request):

    visit_requests = VisitRequest.objects.filter(
        user=request.user
    ).select_related('house').order_by('-created_at')

    return render(request, 'properties/all/my_visit_requests.html', {
        'visit_requests': visit_requests
    })


@login_required
@require_http_methods(["POST"])
def cancel_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation, id=reservation_id, user=request.user)

    try:
        house_label = reservation.house.label or reservation.house.type
        reservation.delete()
        messages.success(
            request, f'Your reservation for {house_label} has been cancelled.')
    except Exception as e:
        messages.error(request, f'Error cancelling reservation: {str(e)}')

    return redirect('my_reservations')


@login_required
@require_http_methods(["POST"])
def cancel_visit_request(request, visit_request_id):
    if request.user.role != "LANDLORD":
        return redirect("home")
    visit_request = get_object_or_404(
        VisitRequest, id=visit_request_id, user=request.user)

    try:
        house_label = visit_request.house.label or visit_request.house.type
        visit_request.delete()
        messages.success(
            request, f'Your visit request for {house_label} has been cancelled.')
    except Exception as e:
        messages.error(request, f'Error cancelling visit request: {str(e)}')

    return redirect('my_visit_requests')


@login_required
def landlord_reservations(request):
    if request.user.role != "LANDLORD":
        return redirect("home")
    reservations = Reservation.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user')

    return render(request, 'properties/landlord/reservations.html', {
        'reservations': reservations
    })


@login_required
def landlord_visit_requests(request):
    if request.user.role != "LANDLORD":
        return redirect("home")
    visit_requests = VisitRequest.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user')

    return render(request, 'properties/landlord/visit_requests.html', {
        'visit_requests': visit_requests
    })