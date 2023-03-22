
from django.urls import path
from .views import main_page_view, IncomesView, IncomeEditView,\
    IncomeDeleteView, RegisterUser, LoginUser, logout_user, IncomeCreateView

urlpatterns = [
    path('', IncomesView.as_view(), name='main_page'),
    path('incomes/', IncomesView.as_view(), name='IncomesView'),
    path('income/<int:pk>/edit/', IncomeEditView.as_view(), name='edit_income'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='delete_income'),
    path('income/create', IncomeCreateView.as_view(), name='create_income'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
]