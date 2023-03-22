import django.contrib.auth.models
from django.db import models
from django.utils import timezone


class Income(models.Model):
    date_of_operation = models.DateTimeField(
        'Дата операции',
        default=timezone.now()
    )
    source = models.ForeignKey(
        'Source',
        verbose_name='Источник',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes_by_source'
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes_by_category'
    )
    sum = models.FloatField('Сумма',
                            default=0
                            )
    currency = models.ForeignKey(
        'Currency',
        verbose_name='Валюта',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incomes_by_currency'
    )
    user = models.ForeignKey(
        django.contrib.auth.models.User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='incomes_by_user'
    )
    status = models.BooleanField(
        'Оплачен',
        default=False
    )
    description = models.TextField(
        'Описание',
        max_length=300,
        default=''
        # blank=True,
    )

    def __str__(self):
        formated_date = self.date_of_operation.strftime("%d-%m-%Y %H:%M:%S")
        return f'Доход от {formated_date} на {self.sum} {self.currency}.'


class Source(models.Model):
    title = models.CharField('Source title', max_length=200, unique=True)
    currency = models.ForeignKey('Currency', verbose_name='Валюта', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField('Название', max_length=200, unique=True)

    def __str__(self):
        return self.title


class Currency(models.Model):
    name = models.CharField('Название', max_length=50, null=True)
    short_name = models.CharField('Короткий код', max_length=3, unique=True)

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
        'Расход',
        max_length=100
    )
    period = models.CharField(
        'Периодичность',
        max_length=10,
        choices=period_choises
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='outcomes'
    )
    sum = models.FloatField(
        'Сумма расхода',
        default=0
    )
    start_date = models.DateField(
        'Дата начала',
        auto_now_add=True
    )
    end_date = models.DateField(
        'Дата окончания',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.title} / {self.sum}'
