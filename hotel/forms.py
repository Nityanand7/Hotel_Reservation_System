# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Booking

User = get_user_model()

from django.contrib.auth.forms import AuthenticationForm
class UserSignUpForm(UserCreationForm):
    username = forms.CharField(max_length=10,label="Mobile Number")
    first_name = forms.CharField(max_length=60, required=True)
    last_name = forms.CharField(max_length=60, required=True)
    email = forms.EmailField(max_length=60, required=True)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(UserSignUpForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=10, label="Mobile Number", widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def __init__(self, request=None, *args, **kwargs):
        super(UserLoginForm, self).__init__(request, *args, **kwargs)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

from .models import BookingService, Service

class ServiceForm(forms.Form):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    quantity = forms.IntegerField(min_value=1, initial=0)

from .models import CreditCard

class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['cardholder_name', 'card_type', 'last_four_digits', 'expiration_month', 'expiration_year', 'billing_address']
        widgets = {
            'expiration_month': forms.NumberInput(attrs={'placeholder': 'MM', 'class': 'form-control'}),
            'expiration_year': forms.NumberInput(attrs={'placeholder': 'YYYY', 'class': 'form-control'}),
            'last_four_digits': forms.NumberInput(attrs={'placeholder': 'Last 4 digits', 'class': 'form-control'}),
        }

# forms.py

from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'capacity', 'price', 'is_available', 'image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

from .models import Service

class AddServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'price']

