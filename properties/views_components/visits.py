from django.shortcuts import render, redirect, get_object_or_404
from properties.models import House, VisitRequest
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.models import User
from properties.forms import VisitRequestForm


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
def my_visit_requests(request):

    visit_requests = VisitRequest.objects.filter(
        user=request.user
    ).select_related('house').order_by('-created_at')

    return render(request, 'properties/all/my_visit_requests.html', {
        'visit_requests': visit_requests
    })


@login_required
@require_http_methods(["POST"])
def cancel_visit_request(request, visit_request_id):
    if request.user.role != User.LANDLORD:
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
def landlord_visit_requests(request):

    visit_requests = VisitRequest.objects.filter(
        house__landlord=request.user
    ).select_related('house', 'user').order_by('-created_at')

    return render(request, 'properties/landlord/landlord_visit_requests.html', {
        'visit_requests': visit_requests
    })


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
