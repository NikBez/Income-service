from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils import dateformat, timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from environs import Env
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import IncomeForm, RegisterUserForm, RegularOutcomeForm
from .models import Category, Income, RegularOutcome, Source
from .serializers import IncomeSummarySerializer
from .utils import convert_currency_by_fixer, get_sum_in_default_currency

from django.conf import settings

env = Env()
env.read_env()



class IncomesView(ListView):
    model = Income
    template_name = 'accounting/incomes_list.html'
    paginate_by = 10

    def get_queryset(self):
        period = self.request.GET.get('period')
        user = self.request.GET.get('user')
        category = self.request.GET.get('category')
        source = self.request.GET.get('source')
        month_filter = self.request.GET.get('month_filter')

        if month_filter:
            filter_month = datetime.strptime(month_filter, '%m_%Y').month
            filter_year = datetime.strptime(month_filter, '%m_%Y').year

        if period == 'month':
            beginning_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return Income.objects.filter(date_of_operation__gte=beginning_of_month).order_by('-date_of_operation')
        elif period == 'week':
            beginning_of_week = timezone.now() - timedelta(days=timezone.now().weekday())
            beginning_of_week = beginning_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            return Income.objects.filter(date_of_operation__gte=beginning_of_week).order_by('-date_of_operation')

        if user and month_filter:
            return Income.objects.filter(
                date_of_operation__month=filter_month,
                date_of_operation__year=filter_year,
                user__username=user
            ).order_by('-date_of_operation')

        if category and month_filter:
            return Income.objects.filter(
                date_of_operation__month=filter_month,
                date_of_operation__year=filter_year,
                category__title=category
            ).order_by('-date_of_operation')

        if source and month_filter:
            return Income.objects.filter(
                date_of_operation__month=filter_month,
                date_of_operation__year=filter_year,
                source__title=source
            ).order_by('-date_of_operation')

        return Income.objects.all().order_by('-date_of_operation', 'source')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show_periods = False if self.request.GET.get('month_filter') else True

        filters = self.request.GET

        if filters.get('period') == 'month':
            context['period'] = 'текущий месяц'
        elif filters.get('period') == 'week':
            context['period'] = 'текущую неделю'

        month_filter = filters.get('month_filter')

        if month_filter:
            month_filter = datetime.strptime(month_filter, '%m_%Y')
            context['month_name'] = month_filter

        filter_category = filters.get('category', None)
        filter_user = filters.get('user', None)
        filter_source = filters.get('source', None)

        if filter_category:
            context['period'] = f'в разрезе категории: {filter_category}'
            context['hide_col'] = 'category'
        elif filter_user:
            context['period'] = f'в разрезе пользователя: {filter_user}'
            context['hide_col'] = 'user'
        elif filter_source:
            context['period'] = f'в разрезе источника: {filter_source}'
            context['hide_col'] = 'source'

        context['show_periods'] = show_periods
        return context


class IncomeEditView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'accounting/incomes_edit.html'
    success_url = reverse_lazy('list_incomes')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_of_operation'].initial = self.object.date_of_operation
        return form

    def form_valid(self, form):
        form.instance.sum_in_default_currency = get_sum_in_default_currency(form.instance.sum, form.instance.source, form.instance.date_of_operation)
        return super().form_valid(form)


class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'accounting/income_delete.html'
    success_url = reverse_lazy('list_incomes')


class IncomeCreateView(CreateView):
    model = Income
    fields = ['status', 'date_of_operation', 'source', 'category', 'sum', 'description']
    template_name = 'accounting/income_create.html'
    success_url = reverse_lazy('list_incomes')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['description'].required = False
        form.fields['date_of_operation'].widget = forms.DateInput()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.currency = form.instance.source.currency
        form.instance.sum_in_default_currency = get_sum_in_default_currency(form.instance.sum, form.instance.source, form.instance.date_of_operation)
        return super().form_valid(form)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'register/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('main_page')


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = 'register/login.html'

    def get_success_url(self):
        return reverse_lazy('main_page')


def logout_user(request):
    logout(request)
    return redirect('login')


def main_page_view(request):

    source_date = request.GET.get('date', None)
    if source_date:
        month_and_year = datetime.strptime(source_date, '%Y-%m-%d').date()
    else:
        month_and_year = timezone.now().date()
    params = {
        'date': month_and_year,
    }

    api_url = reverse('api_incomes')
    response = requests.get(request.build_absolute_uri(api_url), params=params)
    response.raise_for_status()
    response = response.json()

    context = {
        'static_data': response,
        'next_month': dateformat.format(month_and_year + relativedelta(months=1), 'Y-m-d'),
        'previous_month': dateformat.format(month_and_year - relativedelta(months=1), 'Y-m-d'),
        'current_month': month_and_year,
        'avg_period_length': settings.AVERAGE_PERIOD_LENGTH,
        'default_currency': settings.DEFAULT_CURRENCY
    }
    return render(request,  'accounting/main_page.html', context)


class IncomeSummaryView(APIView):

    def get(self, request):
        path_date = request.query_params.get('date')
        path_date = datetime.strptime(path_date, '%Y-%m-%d')
        prev_month = path_date - relativedelta(months=1)

        # Получаем сумму доходов за текущий месяц
        sum_of_income = Income.objects.filter(
            status=True,
            date_of_operation__month=path_date.month,
            date_of_operation__year=path_date.year
        ).aggregate(sum_of_income=Sum('sum_in_default_currency'))['sum_of_income'] or 0.0

        # Получаем сумму доходов за текущий месяц в разрезе источника
        sum_of_income_by_source = Income.objects.filter(
            status=True,
            date_of_operation__month=path_date.month,
            date_of_operation__year=path_date.year
        ).values('source__title').annotate(sum_of_income=Sum('sum_in_default_currency')).order_by('-sum_of_income')

        # Получаем сумму доходов за текущий месяц в разрезе категории
        sum_of_income_by_category = Income.objects.filter(
            status=True,
            date_of_operation__month=path_date.month,
            date_of_operation__year=path_date.year
        ).values('category__title').annotate(sum_of_income=Sum('sum_in_default_currency')).order_by('-sum_of_income')

        # Получаем сумму доходов за текущий месяц в разрезе пользователей
        sum_of_income_by_user = Income.objects.filter(
            status=True,
            date_of_operation__month=path_date.month,
            date_of_operation__year=path_date.year
        ).values('user__username').annotate(sum_of_income=Sum('sum_in_default_currency')).order_by('-sum_of_income')

        # Получаем сумму невыплаченных операций
        sum_of_debt = Income.objects.filter(
            status=False
        ).aggregate(sum_of_debt=Sum('sum_in_default_currency'))['sum_of_debt'] or 0.0

        # Получаем список операций без проведенной оплаты
        debt_operations = Income.objects.filter(status=False).order_by('date_of_operation')
        test_date = path_date + relativedelta(months=1, day=1)
        # Получаем среднюю сумму заработка за последние N месяцев
        average_income = Income.objects.filter(
            date_of_operation__gte=path_date - relativedelta(months=settings.AVERAGE_PERIOD_LENGTH),
            date_of_operation__lt=path_date + relativedelta(months=1, day=1),
            status=True,
        ).aggregate(average_income=Sum('sum_in_default_currency')/settings.AVERAGE_PERIOD_LENGTH)['average_income'] or 0.0

        # Коэффициент изменения прибыли
        prev_month_income = Income.objects.filter(
            status=True,
            date_of_operation__month=prev_month.month,
            date_of_operation__year=prev_month.year
        ).aggregate(prev_month_income=Sum('sum_in_default_currency'))['prev_month_income'] or 0.0

        if prev_month_income:
            income_change_rate = sum_of_income / prev_month_income * 100 - 100
        else:
            income_change_rate = 100

        # Сумма ежемесячных расходов в пересчете на дефолтную валюту
        actual_outcomes_sum = RegularOutcome.objects.filter(
                Q(start_date__lte=path_date) & (Q(end_date__gte=path_date) | Q(end_date__isnull=True))
            ).aggregate(sum_of_reg_outcomes=Sum('sum_in_default_currency'))['sum_of_reg_outcomes'] or 0.0

        # Получаем сумму доходов за текущий месяц в разрезе категории
        actual_outcomes_by_category = RegularOutcome.objects.filter(
            Q(start_date__lte=path_date) & (Q(end_date__gte=path_date) | Q(end_date__isnull=True))
        ).values('category__title').annotate(sum_of_outcome=Sum('sum_in_default_currency')).order_by('-sum_of_outcome')

        serializer = IncomeSummarySerializer({
            'sum_of_income': sum_of_income,
            'sum_of_debt': sum_of_debt,
            'sum_of_income_by_source': sum_of_income_by_source,
            'sum_of_income_by_category': sum_of_income_by_category,
            'sum_of_income_by_user': sum_of_income_by_user,
            'debt_operations': debt_operations,
            'average_income': average_income,
            'income_change_rate': income_change_rate,
            'sum_of_outcomes': actual_outcomes_sum,
            'actual_outcomes_by_category': actual_outcomes_by_category,
            'total_profit': sum_of_income - actual_outcomes_sum,

        })
        return Response(serializer.data)


class OutcomeCreateView(CreateView):
    model = RegularOutcome
    form_class = RegularOutcomeForm
    template_name = 'accounting/income_create.html'
    success_url = reverse_lazy('list_outcomes')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        if form.instance.currency.short_name == settings.DEFAULT_CURRENCY:
            form.instance.sum_in_default_currency = form.instance.sum * settings.PERIOD_MULTIPLIERS.get(form.instance.period, 1)
        else:
            converted_sum = convert_currency_by_fixer(form.instance.sum, form.instance.currency.short_name)
            form.instance.sum_in_default_currency = converted_sum * settings.PERIOD_MULTIPLIERS.get(form.instance.period, 1)
        return super().form_valid(form)


class RegularOutcomesView(ListView):
    model = RegularOutcome
    template_name = 'accounting/outcomes_list.html'
    paginate_by = 10
    ordering = ('end_date', 'start_date')


class OutcomeEditView(UpdateView):
    model = RegularOutcome
    template_name = 'accounting/incomes_edit.html'
    success_url = reverse_lazy('list_outcomes')
    form_class = RegularOutcomeForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        return form

    def form_valid(self, form):
        if form.instance.currency.short_name == settings.DEFAULT_CURRENCY:
            form.instance.sum_in_default_currency = form.instance.sum * settings.PERIOD_MULTIPLIERS.get(form.instance.period, 1)
        else:
            converted_sum = convert_currency_by_fixer(form.instance.sum, form.instance.currency.short_name)
            form.instance.sum_in_default_currency = converted_sum * settings.PERIOD_MULTIPLIERS.get(form.instance.period, 1)
        return super().form_valid(form)


class OutcomeDeleteView(DeleteView):
    model = RegularOutcome
    template_name = 'accounting/income_delete.html'
    success_url = reverse_lazy('list_outcomes')


def income_copy_view(request, pk):
    new_item = get_object_or_404(Income, pk=pk)
    new_item.pk = None  # autogen a new pk (item_id)

    form = IncomeForm(request.POST or None, instance=new_item)

    if form.is_valid():
        form.save()
        return redirect('list_incomes')

    context = {
        "form": form,
    }
    return render(request, "accounting/income_create.html", context)


def list_of_vocabularies(request):
    context = {
        'title': 'Список доступных словарей',
        'vocabularies': [
            ('categories', 'Категории доходов/расходов'),
            ('sources', 'Источники доходов'),
        ],
    }
    return render(request, 'accounting/vocabularies.html', context=context)


class CategoriesView(ListView):
    model = Category
    template_name = 'accounting/categories.html'
    paginate_by = 10


class CategoryEditView(UpdateView):
    model = Category
    template_name = 'accounting/category_edit.html'
    success_url = reverse_lazy('categories')
    fields = '__all__'


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'accounting/category_delete.html'
    success_url = reverse_lazy('categories')


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'accounting/category_create.html'
    success_url = reverse_lazy('categories')
    fields = '__all__'


class SourcesView(ListView):
    model = Source
    template_name = 'accounting/sources.html'
    paginate_by = 10


class SourceEditView(UpdateView):
    model = Source
    template_name = 'accounting/source_edit.html'
    success_url = reverse_lazy('sources')
    fields = '__all__'


class SourceDeleteView(DeleteView):
    model = Source
    template_name = 'accounting/source_delete.html'
    success_url = reverse_lazy('sources')


class SourceCreateView(CreateView):
    model = Source
    template_name = 'accounting/source_create.html'
    success_url = reverse_lazy('sources')
    fields = '__all__'
