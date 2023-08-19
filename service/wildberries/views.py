from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta, MO, SU
from django.conf import settings
from django.db import connection
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import dateformat, timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from rest_framework.response import Response
from rest_framework.views import APIView

from .assets import dictfetchall, dictfetchone
from .forms import WBPaymentForm, PVZPaymentForm, EmployeeUpdateForm
from .models import PVZ, Employee, WBPayment, PVZPaiment
from .queries import month_total_by_pvz_query, week_total_by_pvz_query, week_employee_report, month_total_constructor
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
        'pvz_list':  PVZ.objects.all(),
        'avg_period_length': settings.AVERAGE_PERIOD_LENGTH,
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

        month_total_query = month_total_constructor(query_filter)

        with connection.cursor() as cursor:
            cursor.execute(month_total_by_pvz_query, {'start_date': start_date, 'end_date': end_date})
            pvz_total = dictfetchall(cursor)

            cursor.execute(month_total_query, {'start_date': start_date, 'end_date': end_date})
            month_results = dictfetchone(cursor)

        serializer = WBMonitorSerializer({
            'pvz_total': pvz_total,
            'month_results': month_results,
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

        serializer = PVZMonitorSerializer({
            'pvz_total': pvz_total,
            'employees': employees,
        })
        return Response(serializer.data)


class PVZPaimentList(ListView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_list.html'
    paginate_by = 10


class PVZPaimentUpdate(UpdateView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_edit.html'
    success_url = reverse_lazy('list_pvz_payment')
    form_class = PVZPaymentForm


class PVZPaimentDelete(DeleteView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_delete.html'
    success_url = reverse_lazy('list_pvz_payment')


class PVZPaimentCreate(CreateView):
    model = PVZPaiment
    template_name = 'wb/pvz_payment_create.html'
    success_url = reverse_lazy('list_pvz_payment')
    form_class = PVZPaymentForm


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
