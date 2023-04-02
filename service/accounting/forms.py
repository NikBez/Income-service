from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Income, RegularOutcome

class IncomeForm(forms.ModelForm):
    description = forms.CharField(required=False)
    sum = forms.CharField()

    class Meta:
        model = Income
        fields = [
            'status',
            'date_of_operation',
            'source',
            'category',
            'sum',
            'currency',
            'user',
            'description',
            'sum_in_default_currency'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_operation'].widget = forms.DateInput()
        self.fields['sum_in_default_currency'].widget = forms.HiddenInput()
        self.fields['currency'].widget = forms.HiddenInput()
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 5})


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label = 'Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label = 'Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label = 'Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']



class RegularOutcomeForm(forms.ModelForm):
    class Meta:
        model = RegularOutcome
        exclude = ('sum_in_default_currency',)


