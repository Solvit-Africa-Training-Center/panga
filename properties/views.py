from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Country, District, Reservation, VisitRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from utils.general_search import search_houses
from .forms import HouseForm, VisitRequestForm, ReservationForm


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


@login_required
def add_house(request):
    if request.user.role != "LANDLORD":
        return redirect("home")

    if request.method == "POST":
        form = HouseForm(request.POST, request.FILES)

        if form.is_valid():
            house = form.save(user=request.user)
            messages.success(request, "Property added successfully!")
            return redirect("landlord_properties")
        else:
            messages.error(request, "Please fix the errors.")
    else:
        form = HouseForm()
    countries = Country.objects.all()

    return render(request, "properties/landlord/add_house.html", {
        "form": form,
        'countries': countries,
        "edit_mode": False,
    })


@login_required
def edit_house(request, house_id):
    if request.user.role != "LANDLORD":
        return redirect("home")

    house = get_object_or_404(House, id=house_id, landlord=request.user)

    if request.method == "POST":
        form = HouseForm(
            request.POST,
            request.FILES,
            instance=house
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Property "{house.label or house.type}" updated successfully!'
            )
            return redirect("landlord_properties")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HouseForm(
            instance=house,
            initial={
                "property_type": house.type,
                "village": house.location,
                "bedrooms": house.n_bed_rooms,
                "bathrooms": house.n_bath_rooms,
                "wifi": house.has_wifi,
            }
        )

    village = house.location
    cell = village.cell
    sector = cell.sector
    district = sector.district
    city = district.city
    province = city.province
    country = province.country

    return render(request, "properties/landlord/add_house.html", {
        "form": form,
        "house": house,
        "edit_mode": True,
        "countries": Country.objects.all(),
        "selected_country": country,
        "selected_province": province,
        "selected_city": city,
        "selected_district": district,
        "selected_sector": sector,
        "selected_cell": cell,
        "selected_village": village,
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

    form = ReservationForm(request.POST, user=request.user, house=house)

    if form.is_valid():
        reservation = form.save(commit=False)
        reservation.house = house
        reservation.user = request.user
        reservation.status = 'Pending'
        reservation.save()
        messages.success(
            request,
            f'Your reservation for {house.label or house.type} has been submitted! '
            f'The landlord will contact you soon.'
        )
        return redirect('my_reservations')

    # Show form errors
    for error in form.non_field_errors():
        messages.error(request, error)
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, error)

    return redirect('house_detail', pk=house_id)


@login_required
@require_http_methods(["POST"])
def create_visit_request(request, house_id):
    house = get_object_or_404(House, id=house_id)

    if house.status != "Available":
        messages.error(request, "This property is not available for visits.")
        return redirect("house_detail", pk=house_id)

    if house.landlord == request.user:
        messages.error(
            request, "You cannot request a visit to your own property.")
        return redirect("house_detail", pk=house_id)

    form = VisitRequestForm(
        request.POST,
        user=request.user,
        house=house
    )

    if form.is_valid():
        visit_request = form.save(commit=False)
        visit_request.house = house
        visit_request.user = request.user
        visit_request.status = "Pending"
        visit_request.save()

        messages.success(
            request,
            f"Your visit request for {house.label or house.type} has been submitted!"
        )
        return redirect("my_visit_requests")

    for error in form.non_field_errors():
        messages.error(request, error)
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, error)

    return redirect("house_detail", pk=house_id)


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

    reservations = Reservation.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user').order_by('-created_at')

    return render(request, 'properties/landlord/landlord_reservations.html', {
        'reservations': reservations
    })


@login_required
def landlord_visit_requests(request):

    visit_requests = VisitRequest.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user').order_by('-created_at')

    return render(request, 'properties/landlord/landlord_visit_requests.html', {
        'visit_requests': visit_requests
    })


@login_required
@require_http_methods(["POST"])
def landlord_accept_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        house__landlord=request.user
    )

    try:
        house = reservation.house
        if house.status != 'Available':
            messages.error(request, 'This property is no longer available.')
            return redirect('landlord_reservations')

        house.status = 'Rented'
        house.save()

        reservation.status = "Accepted"
        reservation.save()

        messages.success(
            request,
            f'Reservation accepted! {house.label or house.type} is now marked as Rented. '
            f'Please contact {reservation.user.get_full_name() or reservation.user.email} on this phone number {reservation.user.phone} or this email {reservation.user.email} to finalize the details.'
        )
        other_reservations = Reservation.objects.filter(
            house=house
        ).exclude(id=reservation_id)

        count = other_reservations.count()
        if count > 0:
            other_reservations.delete()
            messages.info(
                request, f'{count} other pending reservation(s) have been automatically cancelled.')

    except Exception as e:
        messages.error(request, f'Error accepting reservation: {str(e)}')

    return redirect('landlord_reservations')


@login_required
@require_http_methods(["POST"])
def landlord_reject_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        house__landlord=request.user
    )
    try:
        house_label = reservation.house.label or reservation.house.type
        user_name = reservation.user.get_full_name() or reservation.user.username
        reservation.delete()

        messages.success(
            request,
            f'Reservation from {user_name} for {house_label} has been rejected.'
        )

    except Exception as e:
        messages.error(request, f'Error rejecting reservation: {str(e)}')

    return redirect('landlord_reservations')


@login_required
@require_http_methods(["POST"])
def landlord_accept_visit_request(request, visit_request_id):
    visit_request = get_object_or_404(
        VisitRequest, id=visit_request_id, house__landlord=request.user)
    try:
        house_label = visit_request.house.label or visit_request.house.type
        user_name = visit_request.user.get_full_name() or visit_request.user.username
        visit_request.status = "Accepted"
        visit_request.save()

        messages.success(
            request,
            f'Visit request accepted! Please contact {user_name} at {visit_request.user.email} or {visit_request.user.phone} '
            f'to confirm the visit to {house_label} on {visit_request.visit_date.strftime("%B %d, %Y")}.'
        )

    except Exception as e:
        messages.error(request, f'Error accepting visit request: {str(e)}')

    return redirect('landlord_visit_requests')


@login_required
@require_http_methods(["POST"])
def landlord_reject_visit_request(request, visit_request_id):
    visit_request = get_object_or_404(
        VisitRequest, id=visit_request_id, house__landlord=request.user)
    try:
        house_label = visit_request.house.label or visit_request.house.type
        user_name = visit_request.user.get_full_name() or visit_request.user.username
        visit_request.status = "Refused"
        visit_request.save()
        messages.success(
            request, f'Visit request from {user_name} for {house_label} has been rejected.')

    except Exception as e:
        messages.error(request, f'Error rejecting visit request: {str(e)}')

    return redirect('landlord_visit_requests')


@login_required
def landlord_dashboard(request):
    total_properties = House.objects.filter(landlord=request.user).count()
    available_properties = House.objects.filter(
        landlord=request.user,
        status='Available'
    ).count()
    rented_properties = House.objects.filter(
        landlord=request.user,
        status='Rented'
    ).count()

    pending_reservations = Reservation.objects.filter(
        house__landlord=request.user
    ).count()
    pending_visits = VisitRequest.objects.filter(
        house__landlord=request.user, status="Pending"
    ).count()

    recent_reservations = Reservation.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user').order_by('-created_at')[:5]

    recent_visits = VisitRequest.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user').order_by('-created_at')[:5]

    context = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'pending_reservations': pending_reservations,
        'pending_visits': pending_visits,
        'recent_reservations': recent_reservations,
        'recent_visits': recent_visits,
    }

    return render(request, 'properties/landlord/landlord_dashboard.html', context)


def about_us(request):
    return render(request, "properties/gukodesha/about.html", {})


def faq(request):
    return render(request, "properties/gukodesha/faq.html", {})


def contact(request):
    return render(request, "properties/gukodesha/contact_us.html", {})
