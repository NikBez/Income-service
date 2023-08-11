from django.urls import path

from .views import (wb_monitor, PVZCreate, PVZList, PVZDelete, PVZUpdate,
                    EmployeeCreate, EmployeeDelete, EmployeeUpdate, EmployeeList,
                    WBPaymentCreate, WBPaymentDelete, WBPaymentUpdate, WBPaymentList,
                    PVZPaimentCreate, PVZPaimentDelete, PVZPaimentUpdate, PVZPaimentList
                    )

urlpatterns = [
    path('', wb_monitor, name='wb_monitor'),
    path('pvz/', PVZList.as_view(), name='list_pvz'),
    path('pvz/<int:pk>/edit/', PVZUpdate.as_view(), name='edit_pvz'),
    path('pvz/<int:pk>/delete/', PVZDelete.as_view(), name='delete_pvz'),
    path('pvz/create', PVZCreate.as_view(), name='create_pvz'),

    path('employee/', EmployeeList.as_view(), name='list_employee'),
    path('employee/<int:pk>/edit/', EmployeeUpdate.as_view(), name='edit_employee'),
    path('employee/<int:pk>/delete/', EmployeeDelete.as_view(), name='delete_employee'),
    path('employee/create', EmployeeCreate.as_view(), name='create_employee'),

    path('wb-payments/', WBPaymentList.as_view(), name='list_wb_payment'),
    path('wb-payments/<int:pk>/edit/', WBPaymentUpdate.as_view(), name='edit_wb_payment'),
    path('wb-payments/<int:pk>/delete/', WBPaymentDelete.as_view(), name='delete_wb_payment'),
    path('wb-payments/create', WBPaymentCreate.as_view(), name='create_wb_payment'),

    path('pvz-payments/', PVZPaimentList.as_view(), name='list_pvz_payment'),
    path('pvz-payments/<int:pk>/edit/', PVZPaimentUpdate.as_view(), name='edit_pvz_payment'),
    path('pvz-payments/<int:pk>/delete/', PVZPaimentDelete.as_view(), name='delete_pvz_payment'),
    path('pvz-payments/create', PVZPaimentCreate.as_view(), name='create_pvz_payment'),
]
