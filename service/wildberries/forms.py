from django import forms
from .models import PVZ, WBPayment, PVZPaiment, Employee, PVZOutcomes, Wallet

import calculation


class WBPaymentForm(forms.ModelForm):
    class Meta:
        model = WBPayment
        fields = '__all__'
   
    from_date = forms.DateField(input_formats=['%d-%m-%Y'], label='от', widget=forms.DateInput(attrs={'id': 'from_date'}))
    to_date = forms.DateField(input_formats=['%d-%m-%Y'], label='до', widget=forms.DateInput(attrs={'id': 'to_date'}))
    pvz_id = forms.ModelChoiceField(queryset=PVZ.objects.all(), label='ПВЗ', empty_label='Выберите...', widget=forms.Select(attrs={'class': 'form-select', 'id': "PVZ_selector"}))
    charged_rate = forms.FloatField(label='Начислено по тарифу', required=False, widget=forms.NumberInput(attrs={'class': 'form-select form-select-lg', 'value': 0}))
    charged_courier = forms.FloatField(label='Доплата за выданное через курьера', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    surcharge_motivation = forms.FloatField(label='Доплата за мотивацию', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_motivation = forms.FloatField(label='за мотивацию', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_rating = forms.FloatField(label='за рейтинг', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    surcharge_signage = forms.FloatField(label='Доплата за вывеску', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    surcharge_goods = forms.FloatField(label='Доплата за товары', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_goods = forms.FloatField(label='за товары', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_substitution = forms.FloatField(label='за подмену товара', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_furniture = forms.FloatField(label='за мебель', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_for_defects = forms.FloatField(label='за брак', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    subsidies = forms.FloatField(label='Субсидии', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    debt = forms.FloatField(label='Долг', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    penalty = forms.FloatField(label='Штраф', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    supplier_returns = forms.FloatField(label='Возвраты поставщику', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    extra_motivation = forms.FloatField(label='Дополнительная мотивация', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    zero_substitution_effect = forms.FloatField(label='Нулевой эффект подмены', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    return_incorrect_mark = forms.FloatField(label='Возврат удержаний за некорректную отметку о браке', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    extra_nds = forms.FloatField(label='Доплата НДС', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    package_compensation = forms.FloatField(label='Компенсация за пакеты', required=False, widget=forms.NumberInput(attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    hold_non_returned = forms.FloatField(label='за невозврат товара', required=False, widget=forms.NumberInput(attrs={'class': 'form-select form-select-lg', 'value': 0}))
    total_charge = forms.FloatField(label='Всего начислено', required=False, widget=calculation.FormulaInput('charged_rate + charged_courier + surcharge_motivation + '
                                                                                                             'surcharge_signage + surcharge_goods + subsidies + extra_motivation +'
                                                                                                             ' return_incorrect_mark + extra_nds + package_compensation + debt +'
                                                                                                             ' zero_substitution_effect + penalty + supplier_returns', attrs={'readonly': True}))
    total_hold = forms.FloatField(label='Всего удержано', required=False, widget=calculation.FormulaInput('hold_motivation + hold_rating + hold_goods + hold_substitution + '
                                                                                                          'hold_furniture + hold_for_defects + penalty + hold_non_returned', attrs={'readonly': True}))
    total = forms.FloatField(label='Доход', required=False, widget=calculation.FormulaInput('total_charge - total_hold', attrs={'class': 'form-control', 'readonly': True}))


class PVZPaymentForm(forms.ModelForm):
    class Meta:
        model = PVZPaiment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pvz_id'].required = False
        self.fields['employee_id'].required = False

    date = forms.DateField(label='Дата', input_formats=['%d-%m-%Y'], widget=forms.DateInput(attrs={'id': 'date'}))

    number_days = forms.IntegerField(label='Смен', required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select form-select-lg', 'value': 0}))
    boxes_count = forms.IntegerField(label='Коробки', required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    extra_payment = forms.FloatField(label='Премия', required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select form-select-lg', 'value': 0}))
    add_penalty = forms.FloatField(label='Добавить штраф', required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    surcharge_penalty = forms.FloatField(label='Удержать штраф', required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    bet = forms.FloatField(label='bet', required=False, widget=forms.HiddenInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0}))
    penalty = forms.FloatField(label='Остаток штрафа', required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0, 'readonly': True}))
    is_closed = forms.BooleanField(label='Оплатить', required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}))

    total = forms.FloatField(label='Итого к выплате', widget=calculation.FormulaInput('number_days * bet + extra_payment + (boxes_count * 100) - surcharge_penalty',
                                                                                            attrs={
                                                                                                'class': 'form-control',
                                                                                                'readonly': False}))


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['penalty',]


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = PVZOutcomes
        fields = '__all__'

    pvz = forms.ModelChoiceField(queryset=PVZ.objects.all(), label='ПВЗ', widget=forms.HiddenInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0}))

class WalletCreateForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('title', 'balance', 'for_salary')

    title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg', 'placeholder': 'Название', 'aria-label': 'Название'}))
    balance = forms.DecimalField(label='Начальный остаток', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0, 'aria-label': '100000'}))
    for_salary = forms.BooleanField(label='Зарплатный', disabled=True,  required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}))


class WalletUpdateForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('title', 'balance', 'for_salary', 'is_archived')

    title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control form-control-lg', 'placeholder': 'Название', 'aria-label': 'Название'}))
    balance = forms.DecimalField(label='Текущий баланс', max_digits=10, decimal_places=2, disabled=True, required=False, widget=forms.NumberInput(
        attrs={'class': 'form-select  form-select-lg', 'value': 0, 'aria-label': '100000'}))
    for_salary = forms.BooleanField(label='Зарплатный',  required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}))
    is_archived = forms.BooleanField(label='В архиве', required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}))