from datetime import timedelta, datetime

from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect,reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Income, RegularOutcome
from .forms import IncomeForm, RegisterUserForm
from django.utils import timezone, dateformat
from django.db.models import Sum
from .serializers import IncomeSummarySerializer

from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from dateutil.relativedelta import relativedelta


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

        return Income.objects.all().order_by('-date_of_operation')


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
    success_url = reverse_lazy('main_page')

    def get_form(self, form_class=IncomeForm):
        form = super().get_form(form_class)
        form.fields['date_of_operation'].initial = self.object.date_of_operation
        return form


class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'accounting/income_delete.html'
    success_url = reverse_lazy('list_incomes')


class IncomeCreateView(CreateView):
    model = Income
    fields = ['date_of_operation', 'source', 'category', 'sum', 'description', 'status']
    template_name = 'accounting/income_create.html'
    success_url = reverse_lazy('main_page')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['description'].required = False
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.currency = form.instance.source.currency
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
        month_and_year = datetime.strptime(source_date, '%Y-%m-%d')
    else:
        month_and_year = timezone.now().date()

    params = {
        'month': month_and_year.month,
        'year': month_and_year.year,
    }

    api_url = reverse('api_incomes')
    response = requests.get(request.build_absolute_uri(api_url), params=params)
    response.raise_for_status()
    response = response.json()

    dept_pks = response['list_of_debt_operations']['pk']
    dept_operations = Income.objects.filter(pk__in=dept_pks).select_related('source', 'currency').order_by('date_of_operation')

    context = {
        'static_data': response,
        'dept_operations': dept_operations,
        'next_month': dateformat.format(month_and_year + relativedelta(months=1), 'Y-m-d'),
        'previous_month': dateformat.format(month_and_year - relativedelta(months=1), 'Y-m-d'),
        'current_month': month_and_year,
    }
    return render(request,  'accounting/main_page.html', context)


class IncomeSummaryView(APIView):

    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        # Получаем сумму доходов за текущий месяц
        sum_of_income = Income.objects.filter(
            status=True,
            date_of_operation__month=month,
            date_of_operation__year=year
        ).aggregate(sum_of_income=Sum('sum'))['sum_of_income'] or 0.0

        # Получаем сумму доходов за текущий месяц в разрезе источника
        sum_of_income_by_source = Income.objects.filter(
            status=True,
            date_of_operation__month=month,
            date_of_operation__year=year
        ).values('source__title').annotate(sum_of_income=Sum('sum')).order_by('-sum_of_income')

        # Получаем сумму доходов за текущий месяц в разрезе категории
        sum_of_income_by_category = Income.objects.filter(
            status=True,
            date_of_operation__month=month,
            date_of_operation__year=year
        ).values('category__title').annotate(sum_of_income=Sum('sum')).order_by('-sum_of_income')

        # Получаем сумму доходов за текущий месяц в разрезе пользователей
        sum_of_income_by_user = Income.objects.filter(
            status=True,
            date_of_operation__month=month,
            date_of_operation__year=year
        ).values('user__username').annotate(sum_of_income=Sum('sum')).order_by('-sum_of_income')

        # Получаем сумму невыплаченных операций
        sum_of_debt = Income.objects.filter(
            status=False
        ).aggregate(sum_of_debt=Sum('sum'))['sum_of_debt'] or 0.0

        # Получаем список операций без проведенной оплаты
        debt_operations = Income.objects.filter(status=False).values('pk')

        serializer = IncomeSummarySerializer({
            'sum_of_income': sum_of_income,
            'sum_of_debt': sum_of_debt,
            'sum_of_income_by_source': sum_of_income_by_source,
            'sum_of_income_by_category': sum_of_income_by_category,
            'sum_of_income_by_user': sum_of_income_by_user,
            'list_of_debt_operations': {'pk': [item['pk'] for item in debt_operations]},
        })
        return Response(serializer.data)


class OutcomeCreateView(CreateView):
    model = RegularOutcome
    fields = '__all__'
    template_name = 'accounting/income_create.html'
    success_url = reverse_lazy('main_page')










