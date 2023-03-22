from django import forms
from .models import Income

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date_of_operation', 'source', 'category', 'sum', 'currency', 'user']
        widgets = {
            'date_of_operation': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'},
                                                     format='%d-%m-%Y %H:%M:%S'),
        }