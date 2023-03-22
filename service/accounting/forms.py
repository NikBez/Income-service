from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Income

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['status', 'date_of_operation', 'source', 'category', 'sum', 'currency', 'user', 'description']
        widgets = {
            'date_of_operation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'},
                                                     format='%d-%m-%Y %H:%M:%S'),
        }


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label = 'Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label = 'Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label = 'Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']





