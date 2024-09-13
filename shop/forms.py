from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address']
        labels = {
            'address': 'Адрес доставки'
        }

class PaymentForm(forms.Form):
    card_number = forms.CharField(label = "Номер карты", max_length=16, widget=forms.TextInput(attrs={"class": "form-control", "placeHolder" : "Введите номер карты"}))
    cvc = forms.CharField(label = "CVС", max_length=3, widget=forms.TextInput(attrs={"class": "form-control", "placeHolder" : "Введите три цифры на обороте карты"}))
    expired_date = forms.CharField(label = "Дата истечения карты", max_length=4, widget=forms.TextInput(attrs={"class": "form-control", "placeHolder" : "Введите дату истечения карты"}))
