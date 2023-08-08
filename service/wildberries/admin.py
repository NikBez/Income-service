from django.contrib import admin

from .models import PVZ, Employee, WBPayment, PVZPaiment


@admin.register(PVZ)
class PVZAdmin(admin.ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    pass

@admin.register(WBPayment)
class WBPaymentAdmin(admin.ModelAdmin):
    pass

@admin.register(PVZPaiment)
class PVZPaimentAdmin(admin.ModelAdmin):
    pass