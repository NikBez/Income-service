from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page_view, name='main_page'),
    path('incomes/', IncomesView.as_view(), name='list_incomes'),
    path('outcomes/', RegularOutcomesView.as_view(), name='list_outcomes'),
    path('income/<int:pk>/edit/', IncomeEditView.as_view(), name='edit_income'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='delete_income'),
    path('outcome/<int:pk>/edit/', OutcomeEditView.as_view(), name='edit_outcome'),
    path('outcome/<int:pk>/delete/', OutcomeDeleteView.as_view(), name='delete_outcome'),
    path('income/create', IncomeCreateView.as_view(), name='create_income'),
    path('income/copy/<int:pk>', income_copy_view, name='copy_income'),
    path('outcome/create', OutcomeCreateView.as_view(), name='create_outcome'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('api/income/', IncomeSummaryView.as_view(), name='api_incomes'),
]