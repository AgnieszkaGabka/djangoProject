from django import forms

from AutoCar.models import CHANGE, FUEL, REPLENISHMENT, Car
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AddCarForm(forms.ModelForm): #dodawanie samochodu

    class Meta:
        model = Car
        exclude = ("user",)

    production_date = forms.DateField(input_formats=["%Y-%m-%d"])
    brand = forms.CharField()
    color = forms.CharField()
    purchase_date = forms.DateField(input_formats=["%Y-%m-%d"])


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class AddChangeForm(forms.Form): #dodawanie zmiany/naprawy w samochodzie
    change_type = forms.MultipleChoiceField(choices=CHANGE, widget=forms.SelectMultiple())
    change_date = forms.DateField(input_formats=["%Y-%m-%d"])
    change_cost = forms.DecimalField()


class RefuelForm(forms.Form): #dodawanie tankowania paliwa
    fuel_type = forms.MultipleChoiceField(choices=FUEL, widget=forms.SelectMultiple())
    amount_fueled = forms.FloatField()
    amount_paid = forms.DecimalField()
    kilometers_traveled = forms.IntegerField()
    fuel_date = forms.DateField(input_formats=["%Y-%m-%d"])


class ReplenishForm(forms.Form): #dodawanie zakupów do samochodu
    fluid_type = forms.MultipleChoiceField(choices=REPLENISHMENT, widget=forms.SelectMultiple())
    price = forms.DecimalField()
    date = forms.DateField(input_formats=["%Y-%m-%d"])


class LoginForm(forms.Form): #logowanie do aplikacji
    username = forms.CharField()
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)