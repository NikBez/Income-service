
from django.urls import path
from .views import main_page_view, IncomesView, IncomeEditView, \
    IncomeDeleteView, RegisterUser, LoginUser, logout_user, IncomeCreateView, main_page_view, IncomeSummaryView, OutcomeCreateView

urlpatterns = [
    path('', main_page_view, name='main_page'),
    path('incomes/', IncomesView.as_view(), name='list_incomes'),
    path('income/<int:pk>/edit/', IncomeEditView.as_view(), name='edit_income'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='delete_income'),
    path('income/create', IncomeCreateView.as_view(), name='create_income'),
    path('outcome/create', OutcomeCreateView.as_view(), name='create_outcome'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('api/income/', IncomeSummaryView.as_view(), name='api_incomes'),
]