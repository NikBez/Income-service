from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta, MO, SU
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import dateformat, timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from rest_framework.response import Response
from rest_framework.views import APIView

from .assets import dictfetchall, dictfetchone, update_employee_penalty
from .forms import WBPaymentForm, PVZPaymentForm, EmployeeUpdateForm, OutcomeForm
from .models import PVZ, Employee, WBPayment, PVZPaiment, Category, PVZOutcomes
from .queries import month_total_by_pvz_query, week_total_by_pvz_query, week_employee_report, month_total_constructor, \
    weekly_pvz_outcomes, year_analitic_constructor
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

    context = {
        'static_data': response,
        'next_month': dateformat.format(request_date + relativedelta(months=1), 'Y-m-d'),
        'previous_month': dateformat.format(request_date - relativedelta(months=1), 'Y-m-d'),
        'current_month': request_date,
        'filter_state': filter,
        'pvz_list': PVZ.objects.all(),
        'avg_period_length': settings.AVERAGE_PERIOD_LENGTH,
        'profits': [float(value) for value in response.get('profits') if response.get('profits')],
        'income': [float(value) for value in response.get('income') if response.get('income')],
        'salary': [float(value) for value in response.get('salary') if response.get('salary')],
        'rent': [float(value) for value in response.get('rent') if response.get('rent')],
        'service': [float(value) for value in response.get('service') if response.get('service')],
        'month_names': response.get('month_names'),
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
        'pvz_id': pk
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
        salary = []
        rent = []
        service = []

        for month in year_results:
            month_name = datetime.strptime(month.get('month'), '%Y-%m-%d').strftime('%B')
            month_names.append(month_name)
            profits.append(month.get('profit', 0))
            income.append(month.get('income', 0))
            salary.append(month.get('salary', 0))
            rent.append(month.get('rent', 0))
            service.append(month.get('service', 0))


        serializer = WBMonitorSerializer({
            'pvz_total': pvz_total,
            'month_results': month_results,
            'month_names': month_names,
            'profits': profits,
            'income': income,
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

        with connection.cursor() as cursor:
            cursor.execute(week_total_by_pvz_query, {'start_date': start_date, 'end_date': end_date, 'pvz_id': pvz_id})
            pvz_total = dictfetchone(cursor)

            cursor.execute(week_employee_report, {'start_date': start_date, 'end_date': end_date, 'pvz_id': pvz_id})
            employees = dictfetchall(cursor)

            cursor.execute(weekly_pvz_outcomes, {'start_date': start_date, 'end_date': end_date, 'pvz_id': pvz_id})
            total_outcomes = dictfetchall(cursor)

        pvz_outcomes = PVZOutcomes.objects.filter(
            Q(pvz=pvz_id) & Q(date__gte=start_date) & Q(date__lte=end_date)).values('pk', 'date', 'sum', 'category__title',
                                                                                    'description').order_by('-sum')
        serializer = PVZMonitorSerializer({
            'pvz_total': pvz_total,
            'employees': employees,
            'pvz_outcomes': pvz_outcomes,
            'total_outcomes': total_outcomes,
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
            payment_doc.is_closed = True if payment_doc.is_closed == False else False
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
                            kwargs={'employee_id': employee_id, 'cr_start_week': start_week, 'cr_end_week': end_week, 'doc_id': 0})

    def get_initial(self):
        initial = super().get_initial()
        employee_id = self.kwargs.get('employee_id')
        date_of_operation = dateformat.format(self.object.date, 'd-m-Y')
        employee = get_object_or_404(Employee, pk=employee_id)

        initial['date'] = date_of_operation
        initial['pvz_id'] = employee.pvz_id
        initial['employee_id'] = employee
        initial['bet'] = employee.salary
        initial['penalty'] = employee.penalty
        return initial

    def form_valid(self, form):
        instance = form.save(commit=False)
        employee_id = self.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, pk=employee_id)
        current_data = get_object_or_404(PVZPaiment, pk=self.object.id)
        instance.pvz_id = employee.pvz_id
        instance.employee_id = employee

        update_employee_penalty(employee,
                                instance.add_penalty - current_data.add_penalty,
                                instance.surcharge_penalty - current_data.surcharge_penalty,
                                create=True
                                )

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
        return super().form_valid(form)

    def get_success_url(self):
        employee_id = self.object.employee_id_id
        start_week = self.kwargs.get('start_week')
        end_week = self.kwargs.get('end_week')
        return reverse_lazy('list_pvz_payment',
                            kwargs={'employee_id': employee_id, 'cr_start_week': start_week, 'cr_end_week': end_week, 'doc_id': 0})


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
        return super().form_valid(form)

    def get_success_url(self):
        employee_id = self.object.employee_id_id
        start_week = self.kwargs.get('cr_start_week')
        end_week = self.kwargs.get('cr_end_week')
        return reverse_lazy('list_pvz_payment',
                            kwargs={'employee_id': employee_id, 'cr_start_week': start_week, 'cr_end_week': end_week, 'doc_id': 0})


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
