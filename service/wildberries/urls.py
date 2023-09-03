from django.urls import path

from .views import (wb_monitor, GetWBAnalitic, PVZCreate, PVZList, PVZDelete, PVZUpdate,
                    EmployeeCreate, EmployeeDelete, EmployeeUpdate, EmployeeList,
                    WBPaymentCreate, WBPaymentDelete, WBPaymentUpdate, WBPaymentList,
                    PVZPaimentCreate, PVZPaimentDelete, PVZPaimentUpdate, PVZPaimentList, GetPVZAnalitic, pvz_monitor,
                    OutcomeList, OutcomeUpdate, OutcomeDelete, OutcomeCreate, CategoryList, CategoryUpdate,
                    CategoryDelete,
                    CategoryCreate, WalletList, WalletUpdate, WalletDelete, WalletCreate, WalletTransactionsList,
                    WalletTransactionUpdate, WalletTransactionDelete, WalletTransactionCreate
                    )

urlpatterns = [
    path('', wb_monitor, name='wb_monitor'),
    path('<int:pk>/', pvz_monitor, name='pvz_monitor'),
    path('api_wb_monitor/', GetWBAnalitic.as_view(), name='api_wb_monitor'),
    path('api_pvz_monitor/', GetPVZAnalitic.as_view(), name='api_pvz_monitor'),

    path('pvz/', PVZList.as_view(), name='list_pvz'),
    path('pvz/<int:pk>/edit/', PVZUpdate.as_view(), name='edit_pvz'),
    path('pvz/<int:pk>/delete/', PVZDelete.as_view(), name='delete_pvz'),
    path('pvz/create/', PVZCreate.as_view(), name='create_pvz'),

    path('employee/', EmployeeList.as_view(), name='list_employee'),
    path('employee/<int:pk>/edit/', EmployeeUpdate.as_view(), name='edit_employee'),
    path('employee/<int:pk>/delete/', EmployeeDelete.as_view(), name='delete_employee'),
    path('employee/create/', EmployeeCreate.as_view(), name='create_employee'),

    path('wb-payments/<int:pvz_id>/', WBPaymentList.as_view(), name='list_wb_payment'),
    path('wb-payments/<int:pvz_id>/<int:pk>/edit/', WBPaymentUpdate.as_view(), name='edit_wb_payment'),
    path('wb-payments/<int:pvz_id>/<int:pk>/delete/', WBPaymentDelete.as_view(), name='delete_wb_payment'),
    path('wb-payments/create/<int:pvz_id>/<str:cr_start_week>/<str:cr_end_week>/', WBPaymentCreate.as_view(),
         name='create_wb_payment'),

    path('pvz-payments/<int:employee_id>/<str:cr_start_week>/<str:cr_end_week>/<int:doc_id>/',
         PVZPaimentList.as_view(),
         name='list_pvz_payment'
         ),
    path('pvz-payments/<int:pk>/<int:employee_id>/<str:start_week>/<str:end_week>/edit/', PVZPaimentUpdate.as_view(),
         name='edit_pvz_payment'),
    path('pvz-payments/<int:pk>/<int:employee_id>/<str:start_week>/<str:end_week>/delete/', PVZPaimentDelete.as_view(),
         name='delete_pvz_payment'),
    path('pvz-payments/create/<int:employee_id>/<int:pvz_id>/<str:cr_start_week>/<str:cr_end_week>/',
         PVZPaimentCreate.as_view(), name='create_pvz_payment'),

    path('pvz-outcomes/<int:pk>/<int:pvz_id>/edit/', OutcomeUpdate.as_view(), name='edit_outcome'),
    path('pvz-outcomes/<int:pk>/<int:pvz_id>/delete/', OutcomeDelete.as_view(), name='delete_outcome'),
    path('pvz-outcomes/<int:pvz_id>/create/', OutcomeCreate.as_view(), name='create_outcome'),
    path('pvz-outcomes/<int:pvz_id>/<str:start_week>/<str:end_week>/', OutcomeList.as_view(), name='list_outcomes'),

    path('categories/', CategoryList.as_view(), name='list_categories'),
    path('categorie/<int:pk>/edit/', CategoryUpdate.as_view(), name='edit_category'),
    path('categorie/<int:pk>/delete/', CategoryDelete.as_view(), name='delete_category'),
    path('categorie/create/', CategoryCreate.as_view(), name='create_category'),

    path('<int:user_id>/wallets/', WalletList.as_view(), name='list_wallets'),
    path('wallet/<int:pk>/edit/', WalletUpdate.as_view(), name='edit_wallet'),
    path('wallet/<int:pk>/delete/', WalletDelete.as_view(), name='delete_wallet'),
    path('wallet/create/', WalletCreate.as_view(), name='create_wallet'),

    path('<int:user_id>/wallet-transactions/', WalletTransactionsList.as_view(), name='list_wallet_transactions'),
    path('wallet-transaction/<int:pk>/edit/', WalletTransactionUpdate.as_view(), name='edit_wallet_transaction'),
    path('wallet-transaction/<int:pk>/delete/', WalletTransactionDelete.as_view(), name='delete_wallet_transaction'),
    path('wallet-transaction/create/', WalletTransactionCreate.as_view(), name='create_wallet_transaction'),
]
