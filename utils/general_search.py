from django.db.models import Q
from properties.models import House


def search_houses(request):
    houses = (
        House.objects
        .filter(is_active=True, status="Available")
        .select_related(
            "location",
            "location__cell",
            "location__cell__sector",
            "location__cell__sector__district",
        )

    )

    query = request.GET.get("q")
    if query:
        houses = houses.filter(
            Q(label__icontains=query) |
            Q(description__icontains=query) |
            Q(neighborhood__icontains=query) |
            Q(street_address__icontains=query) |
            Q(location__name__icontains=query) |
            Q(location__cell__name__icontains=query) |
            Q(location__cell__sector__name__icontains=query) |
            Q(location__cell__sector__district__name__icontains=query)
        )

    house_type = request.GET.get("type")
    if house_type and house_type != "Any":
        houses = houses.filter(type=house_type)

    district = request.GET.get("district")
    if district:
        houses = houses.filter(location__cell__sector__district__id=district)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        houses = houses.filter(monthly_rent__gte=min_price)
    if max_price:
        houses = houses.filter(monthly_rent__lte=max_price)

    bedrooms = request.GET.get("bedrooms")
    if bedrooms:
        if bedrooms == "3+":
            houses = houses.filter(n_bed_rooms__gte=3)
        else:
            houses = houses.filter(n_bed_rooms=bedrooms)

    if request.GET.get("wifi"):
        houses = houses.filter(has_wifi=True)

    if request.GET.get("parking"):
        houses = houses.filter(parkings__gt=0)

    sort = request.GET.get("sort", "newest")
    if sort == "price_low":
        houses = houses.order_by("monthly_rent")
    elif sort == "price_high":
        houses = houses.order_by("-monthly_rent")
    else:
        houses = houses.order_by("-date_of_listing")

    return houses
