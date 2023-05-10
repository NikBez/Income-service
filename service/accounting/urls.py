from django.urls import path
from .views import main_page_view, IncomesView, RegularOutcomesView, IncomeEditView, \
    IncomeDeleteView, OutcomeEditView, OutcomeDeleteView, IncomeCreateView, income_copy_view, \
    OutcomeCreateView, LoginUser, logout_user, RegisterUser, IncomeSummaryView, list_of_vocabularies, \
    CategoriesView, CategoryEditView, CategoryDeleteView, CategoryCreateView, SourcesView, SourceEditView, \
    SourceDeleteView, SourceCreateView


urlpatterns = [
    path('', main_page_view, name='main_page'),
    path('vocabularies/', list_of_vocabularies, name='list_of_vocabularies'),
    path('vocabularies/sources', SourcesView.as_view(), name='sources'),
    path('vocabularies/sources/<int:pk>/edit/', SourceEditView.as_view(), name='edit_source'),
    path('vocabularies/sources/<int:pk>/delete/', SourceDeleteView.as_view(), name='delete_source'),
    path('vocabularies/sources/create', SourceCreateView.as_view(), name='create_source'),
    path('vocabularies/categories', CategoriesView.as_view(), name='categories'),
    path('vocabularies/categories/<int:pk>/edit/', CategoryEditView.as_view(), name='edit_category'),
    path('vocabularies/categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='delete_category'),
    path('vocabularies/categories/create', CategoryCreateView.as_view(), name='create_category'),
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
