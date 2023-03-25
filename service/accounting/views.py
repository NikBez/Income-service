from datetime import timedelta

from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect,reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Income
from .forms import IncomeForm, RegisterUserForm
from django.utils import timezone
from django.db.models import Sum
from .serializers import IncomeSummarySerializer

from rest_framework.views import APIView
from rest_framework.response import Response
import requests


class IncomesView(ListView):
    model = Income
    template_name = 'accounting/incomes_list.html'
    paginate_by = 5


    def get_queryset(self):
        period = self.request.GET.get('period')
        if period == 'month':
            beginning_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return Income.objects.filter(date_of_operation__gte=beginning_of_month).order_by('-date_of_operation')
        elif period == 'week':
            beginning_of_week = timezone.now() - timedelta(days=timezone.now().weekday())
            beginning_of_week = beginning_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            return Income.objects.filter(date_of_operation__gte=beginning_of_week).order_by('-date_of_operation')
        return Income.objects.all().order_by('-date_of_operation')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('period') == 'month':
            context['period'] = 'текущий месяц'
        elif self.request.GET.get('period') == 'week':
            context['period'] = 'текущую неделю'
        else:
            context['period'] = 'все время'
        return context


class IncomeEditView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'accounting/incomes_edit.html'
    success_url = reverse_lazy('list_incomes')

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
    api_url = reverse('api_incomes')
    response = requests.get(request.build_absolute_uri(api_url))
    response.raise_for_status()
    response = response.json()

    dept_pks = response['list_of_debt_operations']['pk']
    dept_operations = Income.objects.filter(pk__in=dept_pks).select_related('source', 'currency')

    context = {
        'static_data': response,
        'dept_operations': dept_operations
    }
    return render(request,  'accounting/main_page.html', context)


class IncomeSummaryView(APIView):
    def get(self, request):
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Получаем сумму доходов за текущий месяц
        sum_of_income = Income.objects.filter(
            status=True,
            date_of_operation__month=current_month,
            date_of_operation__year=current_year
        ).aggregate(sum_of_income=Sum('sum'))['sum_of_income'] or 0.0

        # Получаем сумму доходов за текущий месяц в разрезе источника
        sum_of_income_by_source = Income.objects.filter(
            status=True,
            date_of_operation__month=current_month,
            date_of_operation__year=current_year
        ).values('source__title').annotate(sum_of_income=Sum('sum'))

        # Получаем сумму доходов за текущий месяц в разрезе категории
        sum_of_income_by_category = Income.objects.filter(
            status=True,
            date_of_operation__month=current_month,
            date_of_operation__year=current_year
        ).values('category__title').annotate(sum_of_income=Sum('sum'))

        # Получаем сумму доходов за текущий месяц в разрезе пользователей
        sum_of_income_by_user = Income.objects.filter(
            status=True,
            date_of_operation__month=current_month,
            date_of_operation__year=current_year
        ).values('user__username').annotate(sum_of_income=Sum('sum'))

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









