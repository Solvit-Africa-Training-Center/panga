from django.shortcuts import render, redirect, get_object_or_404
from properties.models import House, Country, District, Reservation, VisitRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from utils.general_search import search_houses
from accounts.models import User
from properties.forms import HouseForm, VisitRequestForm, ReservationForm


def about_us(request):
    return render(request, "properties/gukodesha/about.html", {})


def faq(request):
    return render(request, "properties/gukodesha/faq.html", {})


def contact(request):
    return render(request, "properties/gukodesha/contact_us.html", {})


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
