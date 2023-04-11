from django.contrib import admin
from .models import Source, Category, RegularOutcome, Currency, Income


admin.site.site_header = 'Outcomes accounting'
admin.site.index_title = 'Date tables'

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(RegularOutcome)
class RegularOutcomeAdmin(admin.ModelAdmin):
    pass


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    pass


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    pass
