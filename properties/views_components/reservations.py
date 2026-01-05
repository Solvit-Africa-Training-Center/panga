from django.shortcuts import render, redirect, get_object_or_404
from properties.models import House, Country, District, Reservation, VisitRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from utils.general_search import search_houses
from accounts.models import User
from properties.forms import HouseForm, VisitRequestForm, ReservationForm


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

    for error in form.non_field_errors():
        messages.error(request, error)
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, error)

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
def landlord_reservations(request):

    reservations = Reservation.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user').order_by('-created_at')

    return render(request, 'properties/landlord/landlord_reservations.html', {
        'reservations': reservations
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
