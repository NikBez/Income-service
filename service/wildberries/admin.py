from django.contrib import admin

from .models import PVZ, Employee, WBPayment, PVZPaiment, PVZOutcomes, Category, Wallet, WalletTransaction


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


@admin.register(PVZOutcomes)
class PVZAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class PVZAdmin(admin.ModelAdmin):
    pass


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    pass


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    pass
