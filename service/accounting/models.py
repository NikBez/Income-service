import django.contrib.auth.models
from django.db import models
from django.utils import timezone


class Income(models.Model):
    date_of_operation = models.DateTimeField(
        'Date of operation',
        default=timezone.now()
    )
    source = models.ForeignKey(
        'Source',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes_by_source'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes_by_category'
    )
    sum = models.FloatField('Sum',
                            default=0
                            )
    currency = models.ForeignKey(
        'Currency',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes_by_currency'
    )
    user = models.ForeignKey(
        django.contrib.auth.models.User,
        on_delete=models.CASCADE,
        related_name='incomes_by_user'
    )

    def __str__(self):
        formated_date = self.date_of_operation.strftime("%d-%m-%Y %H:%M:%S")
        return f'Доход от {formated_date} на {self.sum} {self.currency}.'


class Source(models.Model):
    title = models.CharField('Source title', max_length=200, unique=True)
    currency = models.ForeignKey('Currency', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField('Category title', max_length=200, unique=True)

    def __str__(self):
        return self.title


class Currency(models.Model):
    name = models.CharField('Name', max_length=50, null=True)
    short_name = models.CharField('Short view', max_length=3, unique=True)

    def __str__(self):
        return self.short_name


class RegularOutcome(models.Model):
    period_choises = [
        ('d', 'Day'),
        ('w', 'Week'),
        ('m', 'Month'),
        ('y', 'Year'),
    ]
    title = models.CharField(
        'Outcome',
        max_length=100
    )
    period = models.CharField(
        'Period of outcome',
        max_length=10,
        choices=period_choises
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='outcomes'
    )
    sum = models.FloatField(
        'Sum of outcome',
        default=0
    )
    start_date = models.DateField(
        'Date of beginning',
        auto_now_add=True
    )
    end_date = models.DateField(
        'Date of ending',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.title} / {self.sum}'
