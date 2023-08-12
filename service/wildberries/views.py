from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import dateformat, timezone
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import WBPaymentForm, PVZPaymentForm
from .models import PVZ, Employee, WBPayment, PVZPaiment

from django.conf import settings



def wb_monitor(request):
    source_date = request.GET.get('date', None)
    if source_date:
        month_and_year = datetime.strptime(source_date, '%Y-%m-%d').date()
    else:
        month_and_year = timezone.now().date()
    params = {
        'date': month_and_year,
    }
    api_url = reverse('api_wb_monitor')
    response = requests.get(request.build_absolute_uri(api_url), params=params)
    response.raise_for_status()
    response = response.json()

    context = {
        'static_data': response,
        'next_month': dateformat.format(month_and_year + relativedelta(months=1), 'Y-m-d'),
        'previous_month': dateformat.format(month_and_year - relativedelta(months=1), 'Y-m-d'),
        'current_month': month_and_year,
        'avg_period_length': settings.AVERAGE_PERIOD_LENGTH,
    }
    return render(request, 'wb/wb_monitor.html', context)

class GetWBAnalitic(APIView):

    def get(self, request):
        path_date = request.query_params.get('date')
        path_date = datetime.strptime(path_date, '%Y-%m-%d')
        prev_month = path_date - relativedelta(months=1)
        sample_data = {}
        return Response(sample_data)

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


class WBPaymentUpdate(UpdateView):
    model = WBPayment
    template_name = 'wb/wb_payment_edit.html'
    success_url = reverse_lazy('list_wb_payment')
    form_class = WBPaymentForm


class WBPaymentDelete(DeleteView):
    model = WBPayment
    template_name = 'wb/wb_payment_delete.html'
    success_url = reverse_lazy('list_wb_payment')


class WBPaymentCreate(CreateView):
    model = WBPayment
    template_name = 'wb/wb_payment_create.html'
    success_url = reverse_lazy('list_wb_payment')
    form_class = WBPaymentForm


class EmployeeList(ListView):
    model = Employee

    template_name = 'wb/employee_list.html'
    paginate_by = 10


class EmployeeUpdate(UpdateView):
    model = Employee
    template_name = 'wb/employee_edit.html'
    success_url = reverse_lazy('list_employee')
    fields = '__all__'


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
