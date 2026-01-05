from .models import Province, City, District, Sector, Cell, Village
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


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
