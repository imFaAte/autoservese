from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from serves.models import Car, CarBrand


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class CarForm(forms.ModelForm):
    brand = forms.ModelChoiceField(queryset=CarBrand.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    model = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    year = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    plate_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'plate_number', 'image']