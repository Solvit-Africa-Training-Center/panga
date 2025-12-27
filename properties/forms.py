from django import forms
from .models import House, ListingImage, Country, Province, District, Sector, Cell, Village

class HouseForm(forms.ModelForm): 
    location_text = forms.CharField(
        required=True,
        label='Location',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white placeholder-text-secondary',
            'placeholder': ' Kacyiru, Kigali or enter your village/area'
        })
    )
    
    class Meta:
        model = House
        fields = ['name', 'type', 'status', 'monthly_rent', 'description', 
                  'neighborhood', 'street_address', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white placeholder-text-secondary',
                'placeholder': 'Enter house name'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white',
                'style': 'color-scheme: dark;'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white',
                'style': 'color-scheme: dark;'
            }),
            'monthly_rent': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white placeholder-text-secondary',
                'placeholder': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white placeholder-text-secondary',
                'rows': 4,
                'placeholder': 'Describe the property...'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white placeholder-text-secondary',
                'placeholder': 'Enter neighborhood'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white placeholder-text-secondary',
                'placeholder': 'Enter street address'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-dark border border-border-dark rounded-lg focus:ring-2 focus:ring-primary/50 focus:border-primary text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-background-dark hover:file:bg-primary-hover',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-primary bg-background-dark border-border-dark rounded focus:ring-2 focus:ring-primary/50'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     
        if self.instance and self.instance.pk and hasattr(self.instance, 'location'):
            if self.instance.location:
                self.initial['location_text'] = str(self.instance.location)

ListingImageFormSet = forms.inlineformset_factory(
    House,
    ListingImage,
    fields=['image', 'is_main'],
    extra=6,
    can_delete=True,
    widgets={
        'image': forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 bg-background-dark border border-border-dark rounded-lg text-white text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-background-dark hover:file:bg-primary-hover',
            'accept': 'image/*'
        }),
        'is_main': forms.CheckboxInput(attrs={
            'class': 'w-5 h-5 text-primary bg-background-dark border-border-dark rounded focus:ring-2 focus:ring-primary/50'
        }),
    }
)

class ListingImageForm(forms.ModelForm):
    """Form for adding additional images to a house listing"""
    
    class Meta:
        model = ListingImage
        fields = ['image', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


ListingImageFormSet = forms.inlineformset_factory(
    House,
    ListingImage,
    form=ListingImageForm,
    extra=6,
    can_delete=True
)


class HouseSearchForm(forms.Form):
    """Form for searching and filtering house listings"""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, description, or location...'
        })
    )
    
    type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + House.housing_types,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + House.house_status,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_rent = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min rent',
            'step': '0.01'
        })
    )
    
    max_rent = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max rent',
            'step': '0.01'
        })
    )
    
    province = forms.ModelChoiceField(
        queryset=Province.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Provinces'
    )
    
    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Districts'
    )
    
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='All Sectors'
    )


class LocationForm(forms.Form):
    """Form for cascading location selection"""
    
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=Country.objects.filter(name="Rwanda").first()
    )
    
    province = forms.ModelChoiceField(
        queryset=Province.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select Province'
    )
    
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select District'
    )
    
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select Sector'
    )
    
    cell = forms.ModelChoiceField(
        queryset=Cell.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select Cell'
    )
    
    village = forms.ModelChoiceField(
        queryset=Village.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select Village'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['province'].queryset = Province.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('country'):
            self.fields['province'].queryset = self.initial['country'].province_set.all()
        
        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['district'].queryset = District.objects.filter(province_id=province_id)
            except (ValueError, TypeError):
                pass
        
        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['sector'].queryset = Sector.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                pass
        
        if 'sector' in self.data:
            try:
                sector_id = int(self.data.get('sector'))
                self.fields['cell'].queryset = Cell.objects.filter(sector_id=sector_id)
            except (ValueError, TypeError):
                pass
        
        if 'cell' in self.data:
            try:
                cell_id = int(self.data.get('cell'))
                self.fields['village'].queryset = Village.objects.filter(cell_id=cell_id)
            except (ValueError, TypeError):
                pass