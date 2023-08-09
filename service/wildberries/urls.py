from django.urls import path
from .views import (wb_monitor, PVZCreate, PVZList, PVZDelete, PVZUpdate,
                    EmployeeCreate, EmployeeDelete, EmployeeUpdate, EmployeeList
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
]