from datetime import timedelta

from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Income
from .forms import IncomeForm, RegisterUserForm
from django.utils import timezone
from .models import Source, Currency


def main_page_view(request):


    return render(request, 'accounting/main_page.html')


class IncomesView(ListView):
    model = Income
    template_name = 'accounting/incomes_list.html'
    paginate_by = 10


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
    success_url = reverse_lazy('IncomesView')


class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'accounting/income_delete.html'
    success_url = reverse_lazy('IncomesView')


class IncomeCreateView(CreateView):
    model = Income
    fields = ['date_of_operation', 'source', 'category', 'sum', 'description' 'status']
    template_name = 'accounting/income_create.html'
    success_url = reverse_lazy('main_page')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # source = Source.objects.get(pk=form.instance.source.pk).select_related('currency')
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



