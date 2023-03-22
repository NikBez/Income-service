from django.urls import path
from .views import main_page_view, IncomesView, IncomeEditView, IncomeDeleteView


urlpatterns = [
    path('/', IncomesView.as_view(), name='main_page'),
    path('incomes/', IncomesView.as_view(), name='IncomesView'),
    path('income/<int:pk>/edit/', IncomeEditView.as_view(), name='edit_income'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='delete_income'),
]