from django import forms
from .models import *
from django.core.exceptions import ValidationError
from datetime import date


class HouseForm(forms.ModelForm):
    property_type = forms.ChoiceField(choices=House.housing_types)
    village = forms.ModelChoiceField(queryset=Village.objects.all())
    bedrooms = forms.IntegerField(min_value=0)
    bathrooms = forms.IntegerField(min_value=0)
    wifi = forms.BooleanField(required=False)

    class Meta:
        model = House
        fields = [
            "property_type", "status", "label",  "village", "street_address",
            "neighborhood", "description", "bedrooms", "bathrooms",
            "surface", "monthly_rent",  "wifi", "parkings", "on_map",
            "main_image", "image_one", "image_two", "image_three",
            "image_four",
        ]

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            "property_type", "status", "label",  "village", "street_address",
            "neighborhood", "description", "bedrooms", "bathrooms",
            "surface", "monthly_rent", "on_map",
            "main_image",
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")

        return cleaned_data

    def save(self, commit=True, user=None):
        house = super().save(commit=False)
        house.type = self.cleaned_data["property_type"]
        house.location = self.cleaned_data["village"]
        house.n_bed_rooms = self.cleaned_data["bedrooms"]
        house.n_bath_rooms = self.cleaned_data["bathrooms"]
        house.has_wifi = self.cleaned_data["wifi"]

        if user:
            house.landlord = user

        if commit:
            house.save()
        return house


class VisitRequestForm(forms.ModelForm):

    class Meta:
        model = VisitRequest
        fields = ["visit_date", "guests", "message"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.house = kwargs.pop("house", None)
        super().__init__(*args, **kwargs)

    def clean_visit_date(self):
        visit_date = self.cleaned_data["visit_date"]
        if visit_date < date.today():
            raise forms.ValidationError("Please select a future date.")
        return visit_date

    def clean_guests(self):
        guests = self.cleaned_data["guests"]
        if guests < 1:
            raise forms.ValidationError("Guests must be at least 1.")
        return guests

    def clean(self):
        cleaned = super().clean()

        if self.user and self.house:
            exists = VisitRequest.objects.filter(
                house=self.house,
                user=self.user,
                visit_date__gte=date.today(),
                status="Pending"
            ).exists()

            if exists:
                raise forms.ValidationError(
                    "You already have a pending visit request for this property."
                )

        return cleaned


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_date', 'guests']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'bg-surface-dark border border-border-dark rounded-lg px-4 h-12 text-white placeholder-text-secondary/50 focus:ring-2 focus:ring-primary outline-none'
            }),
            'guests': forms.NumberInput(attrs={
                'class': 'bg-surface-dark border border-border-dark rounded-lg px-4 h-12 text-white text-center focus:ring-2 focus:ring-primary outline-none',
                'min': '1'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.house = kwargs.pop('house', None)
        super().__init__(*args, **kwargs)

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < date.today():
            raise forms.ValidationError("Please select a future date.")
        return start_date

    def clean_guests(self):
        guests = self.cleaned_data.get('guests')
        if guests < 1:
            raise forms.ValidationError("Number of guests must be at least 1.")
        return guests

    def clean(self):
        cleaned_data = super().clean()
        if self.user and self.house:
            exists = Reservation.objects.filter(
                house=self.house,
                user=self.user,
                start_date__gte=date.today(),
                status='Pending'
            ).exists()
            if exists:
                raise forms.ValidationError(
                    "You already have a pending reservation for this property."
                )
        return cleaned_data
