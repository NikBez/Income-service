from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta, MO, SU
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import dateformat, timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from rest_framework.response import Response
from rest_framework.views import APIView

from .assets import dictfetchall, dictfetchone, update_employee_penalty, translate_month_titles, create_wallet_outcome, \
    update_wallet_total, delete_wallet_transaction
from .forms import WBPaymentForm, PVZPaymentForm, EmployeeUpdateForm, OutcomeForm, WalletCreateForm, WalletUpdateForm, \
    WalletTransactionCreateForm
from .models import PVZ, Employee, WBPayment, PVZPaiment, Category, PVZOutcomes, Wallet, WalletTransaction
from .queries import month_total_by_pvz_query, week_total_by_pvz_query, week_employee_report, month_total_constructor, \
    weekly_pvz_outcomes, year_analitic_constructor, year_analitic_by_weeks
from .serializers import WBMonitorSerializer, PVZMonitorSerializer


def wb_monitor(request):
    source_date = request.GET.get('date', None)
    filter = request.GET.get('filter', None)

    if source_date:
        request_date = datetime.strptime(source_date, '%Y-%m-%d').date()
    else:
        request_date = timezone.now().date()

    params = {
        'date': request_date,
        'filter': filter
    }
    api_url = reverse('api_wb_monitor')
    response = requests.get(request.build_absolute_uri(api_url), params=params)
    response.raise_for_status()
    response = response.json()

    translated_month_titles = translate_month_titles(response.get('month_names'))

    context = {
        'static_data': response,
        'next_month': dateformat.format(request_date + relativedelta(months=1), 'Y-m-d'),
        'previous_month': dateformat.format(request_date - relativedelta(months=1), 'Y-m-d'),
        'current_month': request_date,
        'filter_state': filter,
        'pvz_list': PVZ.objects.all(),
        'wallets': Wallet.objects.filter(user=request.user.id),
        'avg_period_length': settings.AVERAGE_PERIOD_LENGTH,
        'profits': [float(value) for value in response.get('profits') if response.get('profits')],
        'income': [float(value) for value in response.get('income') if response.get('income')],
        'holded': [float(value) for value in response.get('holded') if response.get('holded')],
        'salary': [float(value) for value in response.get('salary') if response.get('salary')],
        'rent': [float(value) for value in response.get('rent') if response.get('rent')],
        'service': [float(value) for value in response.get('service') if response.get('service')],
        'month_names': translated_month_titles,
    }
    return render(request, 'wb/wb_monitor.html', context)


def pvz_monitor(request, pk):
    get_object_or_404(PVZ, pk=pk)

    source_date = request.GET.get('date', None)
    if source_date:
        request_date = datetime.strptime(source_date, '%Y-%m-%d').date()
    else:
        request_date = timezone.now().date()

    start_week = dateformat.format(request_date - relativedelta(weekday=MO(-1)), 'Y-m-d')
    end_week = dateformat.format(request_date - relativedelta(weekday=SU(+1)), 'Y-m-d')

    params = {
        'start_week': start_week,
        'end_week': end_week,
        'pvz_id': pk
    }
    api_url = reverse('api_pvz_monitor')
    response = requests.get(request.build_absolute_uri(api_url), params=params)
    response.raise_for_status()
    response = response.json()

    context = {
        'static_data': response,
        'next_week': dateformat.format(request_date + relativedelta(weeks=1), 'Y-m-d'),
        'previous_week': dateformat.format(request_date + relativedelta(weeks=-1), 'Y-m-d'),
        'start_week': dateformat.format(datetime.strptime(start_week, '%Y-%m-%d').date(), 'd/m/Y'),
        'end_week': dateformat.format(datetime.strptime(end_week, '%Y-%m-%d').date(), 'd/m/Y'),
        'cr_start_week': dateformat.format(datetime.strptime(start_week, '%Y-%m-%d').date(), 'd-m-Y'),
        'cr_end_week': dateformat.format(datetime.strptime(end_week, '%Y-%m-%d').date(), 'd-m-Y'),
        'avg_period_length': settings.AVERAGE_PERIOD_LENGTH,
        'pvz_id': pk,

        'profits': [float(value) for value in response.get('profits') if response.get('profits')],
        'income': [float(value) for value in response.get('income') if response.get('income')],
        'holded': [float(value) for value in response.get('holded') if response.get('holded')],
        'salary': [float(value) for value in response.get('salary') if response.get('salary')],
        'rent': [float(value) for value in response.get('rent') if response.get('rent')],
        'service': [float(value) for value in response.get('service') if response.get('service')],
        'week_titles': response.get('week_titles'),
    }
    return render(request, 'wb/pvz_monitor.html', context)


class GetWBAnalitic(APIView):

    def get(self, request):
        query_date = request.query_params.get('date')
        query_filter = request.query_params.get('filter')

        query_date = datetime.strptime(query_date, '%Y-%m-%d')

        start_date = query_date + relativedelta(day=1)
        end_date = query_date + relativedelta(day=31)

        # Собираем запрос с фильтром по ПВЗ или без
        month_total_query = month_total_constructor(query_filter)
        year_analitic_query = year_analitic_constructor(query_filter)

        with connection.cursor() as cursor:
            cursor.execute(month_total_by_pvz_query, {'start_date': start_date, 'end_date': end_date})
            pvz_total = dictfetchall(cursor)

            cursor.execute(month_total_query, {'start_date': start_date, 'end_date': end_date})
            month_results = dictfetchone(cursor)

            cursor.execute(year_analitic_query)
            year_results = dictfetchall(cursor)

        month_names = []
        profits = []
        income = []
        holded = []
        salary = []
        rent = []
        service = []

        for month in year_results:
            month_name = datetime.strptime(month.get('month'), '%Y-%m-%d').strftime('%B')
            month_names.append(month_name)
            profits.append(month.get('profit', 0))
            income.append(month.get('income', 0))
            holded.append(month.get('holded', 0))
            salary.append(month.get('salary', 0))
            rent.append(month.get('rent', 0))
            service.append(month.get('service', 0))

        serializer = WBMonitorSerializer({
            'pvz_total': pvz_total,
            'month_results': month_results,
            'month_names': month_names,
            'profits': profits,
            'income': income,
            'holded': holded,
            'salary': salary,
            'rent': rent,
            'service': service,
        })

        return Response(serializer.data)


class GetPVZAnalitic(APIView):

    def get(self, request):
        start_date = request.query_params.get('start_week')
        end_date = request.query_params.get('end_week')
        pvz_id = request.query_params.get('pvz_id')

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        year_analitic_query = year_analitic_by_weeks(pvz_id)

        with connection.cursor() as cursor:
            cursor.execute(week_total_by_pvz_query, {'start_date': start_date, 'end_date': end_date, 'pvz_id': pvz_id})
            pvz_total = dictfetchone(cursor)

            cursor.execute(week_employee_report, {'start_date': start_date, 'end_date': end_date, 'pvz_id': pvz_id})
            employees = dictfetchall(cursor)

            cursor.execute(weekly_pvz_outcomes, {'start_date': start_date, 'end_date': end_date, 'pvz_id': pvz_id})
            total_outcomes = dictfetchall(cursor)

            cursor.execute(year_analitic_query)
            year_results = dictfetchall(cursor)

        week_titles = []
        profits = []
        income = []
        holded = []
        salary = []
        rent = []
        service = []

        for week in year_results:
            week_titles.append(week.get('week'))
            profits.append(week.get('profit', 0))
            income.append(week.get('income', 0))
            holded.append(week.get('holded', 0))
            salary.append(week.get('salary', 0))
            rent.append(week.get('rent', 0))
            service.append(week.get('service', 0))

        pvz_outcomes = PVZOutcomes.objects.filter(
            Q(pvz=pvz_id) & Q(date__gte=start_date) & Q(date__lte=end_date)).values('pk', 'date', 'sum',
                                                                                    'category__title',
                                                                                    'description').order_by('-sum')
        serializer = PVZMonitorSerializer({
            'pvz_total': pvz_total,
            'employees': employees,
            'pvz_outcomes': pvz_outcomes,
            'total_outcomes': total_outcomes,

            'week_titles': week_titles,
            'profits': profits,
            'income': income,
            'holded': holded,
            'salary': salary,
            'rent': rent,
            'service': service,
        })
        return Response(serializer.data)


class PVZPaimentList(ListView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = self.kwargs.get('employee_id')
        start_date = self.kwargs.get('cr_start_week')
        end_date = self.kwargs.get('cr_end_week')
        context['start_date'] = start_date
        context['end_date'] = end_date

        context['employee'] = get_object_or_404(Employee, pk=employee_id)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        employee_id = self.kwargs.get('employee_id')
        start_week = self.kwargs.get('cr_start_week')
        end_week = self.kwargs.get('cr_end_week')
        doc_id = self.kwargs.get('doc_id')

        if doc_id:
            payment_doc = PVZPaiment.objects.get(pk=doc_id)
            if payment_doc.is_closed:
                payment_doc.is_closed = False
                delete_wallet_transaction(doc_id)
            else:
                payment_doc.is_closed = True
                current_user = self.request.user
                create_wallet_outcome(current_user, payment_doc.total, payment_doc.employee_id.name, doc_id)
            payment_doc.save()

        converted_start_week = datetime.strptime(start_week, "%d-%m-%Y")
        converted_end_week = datetime.strptime(end_week, "%d-%m-%Y")

        if employee_id is not None:
            queryset = queryset.filter(Q(date__gte=converted_start_week) & Q(date__lte=converted_end_week),
                                       employee_id=employee_id).order_by('-date')
        return queryset


class PVZPaimentUpdate(UpdateView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_edit.html'
    success_url = reverse_lazy('wb_monitor')
    form_class = PVZPaymentForm

    def get_success_url(self):
        employee_id = self.object.employee_id_id

        start_week = self.kwargs.get('start_week')
        end_week = self.kwargs.get('end_week')
        return reverse_lazy('list_pvz_payment',
                            kwargs={'employee_id': employee_id, 'cr_start_week': start_week, 'cr_end_week': end_week,
                                    'doc_id': 0})

    def get_initial(self):
        initial = super().get_initial()
        employee = self.object.employee_id
        date_of_operation = dateformat.format(self.object.date, 'd-m-Y')

        initial['date'] = date_of_operation
        initial['pvz_id'] = employee.pvz_id
        initial['employee_id'] = employee
        initial['bet'] = employee.salary
        initial['penalty'] = employee.penalty
        return initial

    def form_valid(self, form):
        instance = form.save(commit=False)
        employee = instance.employee_id
        current_data = get_object_or_404(PVZPaiment, pk=self.object.id)
        instance.pvz_id = employee.pvz_id

        update_employee_penalty(employee,
                                instance.add_penalty - current_data.add_penalty,
                                instance.surcharge_penalty - current_data.surcharge_penalty,
                                create=True
                                )
        if form.instance.is_closed:
            update = True
            current_user = self.request.user
            create_wallet_outcome(current_user, form.instance.total, form.instance.employee_id.name, form.instance.id, update)
        else:
            delete_wallet_transaction(form.instance.id)

        instance.save()
        return super().form_valid(form)


class PVZPaimentDelete(DeleteView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_delete.html'

    def form_valid(self, form):
        employee_id = self.object.employee_id
        add_penalty = self.object.add_penalty
        surcharge_penalty = self.object.surcharge_penalty
        update_employee_penalty(employee_id, add_penalty, surcharge_penalty, create=False)
        if self.object.is_closed:
            delete_wallet_transaction(self.object.id)
        return super().form_valid(form)

    def get_success_url(self):
        employee_id = self.object.employee_id_id
        start_week = self.kwargs.get('start_week')
        end_week = self.kwargs.get('end_week')
        return reverse_lazy('list_pvz_payment',
                            kwargs={'employee_id': employee_id, 'cr_start_week': start_week, 'cr_end_week': end_week,
                                    'doc_id': 0})


class PVZPaimentCreate(CreateView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_create.html'
    form_class = PVZPaymentForm

    def get_initial(self):
        initial = super().get_initial()
        employee_id = self.kwargs.get('employee_id')
        current_date = dateformat.format(datetime.utcnow().date(), 'd-m-Y')
        employee = get_object_or_404(Employee, pk=employee_id)

        initial['pvz_id'] = employee.pvz_id
        initial['date'] = current_date
        initial['employee_id'] = employee.pk
        initial['bet'] = employee.salary
        initial['penalty'] = employee.penalty
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_id = self.kwargs.get('employee_id')
        start_date = self.kwargs.get('cr_start_week')
        end_date = self.kwargs.get('cr_end_week')
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['employee'] = get_object_or_404(Employee, pk=employee_id)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        employee_id = self.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, pk=employee_id)
        instance.pvz_id = employee.pvz_id
        instance.employee_id = employee
        update_employee_penalty(employee, instance.add_penalty, instance.surcharge_penalty)
        instance.save()
        if form.instance.is_closed:
            current_user = self.request.user
            create_wallet_outcome(current_user, instance.total, instance.employee_id.name, instance.id)
        return super().form_valid(form)

    def get_success_url(self):
        employee_id = self.object.employee_id_id
        start_week = self.kwargs.get('cr_start_week')
        end_week = self.kwargs.get('cr_end_week')
        return reverse_lazy('list_pvz_payment',
                            kwargs={'employee_id': employee_id, 'cr_start_week': start_week, 'cr_end_week': end_week,
                                    'doc_id': 0})


class WBPaymentList(ListView):
    model = WBPayment
    template_name = 'wb/wb_payment_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pvz_id = self.kwargs.get('pvz_id')
        context['pvz_id'] = pvz_id
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        pvz_id = self.kwargs.get('pvz_id')

        if pvz_id is not None:
            queryset = queryset.filter(pvz_id=pvz_id).order_by('from_date')
        return queryset


class WBPaymentUpdate(UpdateView):
    model = WBPayment
    template_name = 'wb/wb_payment_edit.html'
    form_class = WBPaymentForm

    def get_initial(self):
        initial = super().get_initial()
        pvz_id = self.kwargs.get('pvz_id')

        start_week = dateformat.format(self.object.from_date, 'd-m-Y')
        end_week = dateformat.format(self.object.to_date, 'd-m-Y')

        initial['pvz_id'] = pvz_id
        initial['from_date'] = start_week
        initial['to_date'] = end_week

        return initial

    def get_success_url(self):
        pvz_id = self.kwargs.get('pvz_id')
        return reverse_lazy('list_wb_payment', kwargs={'pvz_id': pvz_id})


class WBPaymentDelete(DeleteView):
    model = WBPayment
    template_name = 'wb/wb_payment_delete.html'

    def get_success_url(self):
        pvz_id = self.kwargs.get('pvz_id')
        return reverse_lazy('list_wb_payment', kwargs={'pvz_id': pvz_id})


class WBPaymentCreate(CreateView):
    model = WBPayment
    template_name = 'wb/wb_payment_create.html'
    form_class = WBPaymentForm

    def get_initial(self):
        initial = super().get_initial()
        pvz_id = self.kwargs.get('pvz_id')
        start_week = self.kwargs.get('cr_start_week')
        end_week = self.kwargs.get('cr_end_week')

        start_week = dateformat.format(datetime.strptime(start_week, '%d-%m-%Y').date(), 'd-m-Y')
        end_week = dateformat.format(datetime.strptime(end_week, '%d-%m-%Y').date(), 'd-m-Y')

        initial['pvz_id'] = pvz_id
        initial['from_date'] = start_week
        initial['to_date'] = end_week

        return initial

    def get_success_url(self):
        pvz_id = self.kwargs.get('pvz_id')
        return reverse_lazy('pvz_monitor', kwargs={'pk': pvz_id})


class EmployeeList(ListView):
    model = Employee

    template_name = 'wb/employee_list.html'
    paginate_by = 10


class EmployeeUpdate(UpdateView):
    model = Employee
    template_name = 'wb/employee_edit.html'
    success_url = reverse_lazy('list_employee')
    form_class = EmployeeUpdateForm


class EmployeeDelete(DeleteView):
    model = Employee
    template_name = 'wb/employee_delete.html'
    success_url = reverse_lazy('list_employee')


class EmployeeCreate(CreateView):
    model = Employee
    template_name = 'wb/employee_create.html'
    success_url = reverse_lazy('list_employee')
    fields = '__all__'


class PVZList(ListView):
    model = PVZ
    template_name = 'wb/pvz_list.html'
    paginate_by = 10


class PVZUpdate(UpdateView):
    model = PVZ
    template_name = 'wb/pvz_edit.html'
    success_url = reverse_lazy('list_pvz')
    fields = '__all__'


class PVZDelete(DeleteView):
    model = PVZ
    template_name = 'wb/pvz_delete.html'
    success_url = reverse_lazy('list_pvz')


class PVZCreate(CreateView):
    model = PVZ
    template_name = 'wb/pvz_create.html'
    success_url = reverse_lazy('list_pvz')
    fields = '__all__'


class OutcomeList(ListView):
    model = PVZOutcomes
    template_name = 'wb/outcome_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pvz_id = self.kwargs.get('pvz_id')
        start_date = self.kwargs.get('start_week')
        end_date = self.kwargs.get('end_week')
        context['start_date'] = start_date
        context['end_date'] = end_date

        context['pvz'] = get_object_or_404(PVZ, pk=pvz_id)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        pvz_id = self.kwargs.get('pvz_id')
        start_week = self.kwargs.get('start_week')
        end_week = self.kwargs.get('end_week')

        converted_start_week = datetime.strptime(start_week, "%d-%m-%Y")
        converted_end_week = datetime.strptime(end_week, "%d-%m-%Y")

        if pvz_id is not None:
            queryset = queryset.filter(Q(date__gte=converted_start_week) & Q(date__lte=converted_end_week),
                                       pvz=pvz_id).order_by('-date')
        return queryset


class OutcomeCreate(CreateView):
    model = PVZOutcomes
    template_name = 'wb/outcome_create.html'
    form_class = OutcomeForm

    def get_initial(self):
        initial = super().get_initial()
        pvz_id = self.kwargs.get('pvz_id')
        initial['pvz'] = pvz_id
        return initial

    def get_success_url(self):
        pvz_id = self.kwargs.get('pvz_id')
        return reverse_lazy('pvz_monitor', kwargs={'pk': pvz_id})


class OutcomeUpdate(UpdateView):
    model = PVZOutcomes
    template_name = 'wb/outcome_edit.html'
    form_class = OutcomeForm

    def get_success_url(self):
        pvz_id = self.kwargs.get('pvz_id')
        return reverse_lazy('pvz_monitor', kwargs={'pk': pvz_id})


class OutcomeDelete(DeleteView):
    model = PVZOutcomes
    template_name = 'wb/outcome_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pvz_id'] = self.kwargs.get('pvz_id')
        return context

    def get_success_url(self):
        pvz_id = self.kwargs.get('pvz_id')
        return reverse_lazy('pvz_monitor', kwargs={'pk': pvz_id})


class CategoryList(ListView):
    model = Category
    template_name = 'wb/category_list.html'
    paginate_by = 10


class CategoryCreate(CreateView):
    model = Category
    template_name = 'wb/category_create.html'
    success_url = reverse_lazy('list_categories')
    fields = '__all__'


class CategoryUpdate(UpdateView):
    model = Category
    template_name = 'wb/category_edit.html'
    success_url = reverse_lazy('list_categories')
    fields = '__all__'


class CategoryDelete(DeleteView):
    model = Category
    template_name = 'wb/category_delete.html'
    success_url = reverse_lazy('list_categories')


class WalletList(ListView):
    model = Wallet
    template_name = 'wb/wallet_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user.id).order_by('is_archived')
        return queryset


class WalletCreate(CreateView):
    model = Wallet
    template_name = 'wb/wallet_create.html'
    form_class = WalletCreateForm

    def get_success_url(self):
        return reverse_lazy('list_wallets')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_salary_wallet = Wallet.objects.filter(user=self.request.user, is_archived=False, for_salary=True)
        context['has_salary_wallet'] = has_salary_wallet.exists()
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()
        return super().form_valid(form)


class WalletUpdate(UpdateView):
    model = Wallet
    template_name = 'wb/wallet_edit.html'
    form_class = WalletUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        has_salary_wallet = Wallet.objects.filter(user=self.request.user, is_archived=False, for_salary=True).exclude(
            pk=self.object.pk)
        context['has_salary_wallet'] = has_salary_wallet.exists()
        return context

    def get_success_url(self):
        return reverse_lazy('list_wallets')


class WalletDelete(DeleteView):
    model = Wallet
    template_name = 'wb/wallet_delete.html'

    def get_success_url(self):
        return reverse_lazy('list_wallets')


class WalletTransactionsList(ListView):
    model = WalletTransaction
    template_name = 'wb/wallet_transaction_list.html'
    paginate_by = 10
    ordering = ('-operation_date',)

    def get_queryset(self):
        queryset = super().get_queryset()
        wallet_id = self.request.GET.get('wallet_id')
        if wallet_id:
            queryset = queryset.filter(wallet_id=int(wallet_id))
            print(queryset)
        else:
            queryset = queryset.filter(wallet_id__user=self.request.user.id)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = datetime.now()
        day_of_week = current_date.weekday()
        days_until_start_of_week = (day_of_week + 1) % 7
        days_until_end_of_week = 6 - day_of_week

        start_of_week = current_date - timedelta(days=days_until_start_of_week)
        end_of_week = current_date + timedelta(days=days_until_end_of_week)

        context['start_of_week'] = start_of_week.strftime('%d-%m-%Y')
        context['end_of_week'] = end_of_week.strftime('%d-%m-%Y')

        return context


class WalletTransactionCreate(CreateView):
    model = WalletTransaction
    template_name = 'wb/wallet_transaction_create.html'
    form_class = WalletTransactionCreateForm

    def get_success_url(self):
        wallet_id = self.request.GET.get('wallet_id')
        reverse_url = reverse_lazy('list_wallet_transactions')
        return reverse_url + f'?wallet_id={wallet_id}'

    def get_initial(self):
        initial = super().get_initial()
        wallet_id = self.request.GET.get('wallet_id')
        transaction_type = self.request.GET.get('type')

        if transaction_type == 'in':
            transaction_type_choice = WalletTransaction.TransactionType.INCOME
        elif transaction_type == 'out':
            transaction_type_choice = WalletTransaction.TransactionType.OUTCOME
        else:
            return HttpResponseBadRequest("Invalid transaction_type parameter")

        initial['wallet_id'] = Wallet.objects.get(pk=wallet_id)
        initial['transaction_type'] = transaction_type_choice
        initial['operation_date'] = datetime.utcnow()
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet_id = self.request.GET.get('wallet_id')
        wallet = Wallet.objects.get(pk=wallet_id)
        context['wallet_title'] = wallet.title
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        update_wallet_total(instance.wallet_id.id, instance.transaction_type, instance.transaction_sum)
        instance.save()
        return super().form_valid(form)


class WalletTransactionUpdate(UpdateView):
    model = WalletTransaction
    template_name = 'wb/wallet_transaction_create.html'
    form_class = WalletTransactionCreateForm

    def get_success_url(self):
        wallet_id = self.request.GET.get('wallet')
        reverse_url = reverse_lazy('list_wallet_transactions')
        return reverse_url + f'?wallet_id={wallet_id}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet_id = self.request.GET.get('wallet')
        wallet = Wallet.objects.get(pk=wallet_id)
        context['wallet_title'] = wallet.title
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        current_wallet_id = self.object.wallet_id.id
        wallet = Wallet.objects.get(pk=current_wallet_id)
        transaction_sum = form.initial.get('transaction_sum')
        if instance.transaction_type == 'IN':
            new_balance = wallet.balance - transaction_sum + instance.transaction_sum
        elif instance.transaction_type == 'OUT':
            new_balance = wallet.balance + transaction_sum - instance.transaction_sum
        wallet.balance = new_balance
        wallet.save()
        instance.save()
        return super().form_valid(form)


class WalletTransactionDelete(DeleteView):
    model = WalletTransaction
    template_name = 'wb/wallet_transaction_delete.html'

    def get_success_url(self):
        return reverse_lazy('list_wallet_transactions')

    def form_valid(self, form):
        current_wallet_id = self.object.wallet_id.id
        wallet = Wallet.objects.get(pk=current_wallet_id)
        transaction_sum = self.object.transaction_sum
        if self.object.transaction_type == 'IN':
            new_balance = wallet.balance - transaction_sum
        elif self.object.transaction_type == 'OUT':
            new_balance = wallet.balance + transaction_sum
        wallet.balance = new_balance
        wallet.save()

        return super().form_valid(form)
