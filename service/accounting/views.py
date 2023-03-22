from datetime import timedelta

from django.shortcuts import render
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Income
from .forms import IncomeForm
from django.utils import timezone


def main_page_view(request):
    return render('Hello')


class IncomesView(ListView):
    model = Income
    template_name = 'accounting/incomes_list.html'


    def get_queryset(self):
        period = self.request.GET.get('period')
        if period == 'month':
            beginning_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return Income.objects.filter(date_of_operation__gte=beginning_of_month)
        elif period == 'week':
            beginning_of_week = timezone.now() - timedelta(days=timezone.now().weekday())
            beginning_of_week = beginning_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            return Income.objects.filter(date_of_operation__gte=beginning_of_week)
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
    success_url = reverse_lazy('IncomesView')


class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'accounting/income_delete.html'
    success_url = reverse_lazy('IncomesView')


class IncomeCreateView(CreateView):
    pass

