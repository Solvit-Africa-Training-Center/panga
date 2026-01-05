from django.shortcuts import render, redirect, get_object_or_404
from properties.models import House, Country, District
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from utils.general_search import search_houses
from accounts.models import User
from properties.forms import HouseForm


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
    if request.user.role != User.LANDLORD:
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
    if request.user.role != User.LANDLORD:
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
    if request.user.role != User.LANDLORD:
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
    if request.user.role != User.LANDLORD:
        return redirect('home')
    houses = House.objects.filter(
        landlord=request.user).order_by('-date_of_listing')
    return render(request, 'properties/landlord/my_properties.html', {
        'houses': houses
    })
