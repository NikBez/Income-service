import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class PVZ(models.Model):
    title = models.CharField('Название ПВЗ', max_length=100)
    rent_price = models.FloatField('Стоимость аренды(месяц)', default=0)
    video_price = models.FloatField('Стоимость обслуживания камер(месяц)', default=0)
    extra_serving_price = models.FloatField('Стоимость доп. обслуживания(месяц)', default=0)

    def __str__(self):
        return self.title


class Employee(models.Model):
    name = models.CharField('ФИО сотрудника', max_length=200, unique=True, default='Unnamed')
    pvz_id = models.ManyToManyField(
        'PVZ',
        verbose_name='ПВЗ сотрудника',
        related_name='employees'
    )
    date_of_start = models.DateField('Дата трудоустройства', null=True, blank=True)
    salary = models.FloatField('Ставка за смену', default=0)
    penalty = models.FloatField('Накопленный штраф', default=0)
    is_archived = models.BooleanField('В архиве', default=False)

    def __str__(self):
        return self.name


class WBPayment(models.Model):
    pvz_id = models.ForeignKey(
        PVZ,
        verbose_name='ПВЗ',
        on_delete=models.CASCADE,
        related_name='wb_payments'
    )
    from_date = models.DateField('Дата начала периода')
    to_date = models.DateField('Дата окончания периода')
    charged_rate = models.FloatField('Начислено по тарифу', default=0)
    charged_courier = models.FloatField('Доплата за выданное через курьера', default=0)
    surcharge_motivation = models.FloatField('Доплата за мотивацию', default=0)
    hold_motivation = models.FloatField('Удержание за мотивацию', default=0)
    hold_rating = models.FloatField('Удержание за рейтинг', default=0)
    surcharge_signage = models.FloatField('Доплата за вывеску', default=0)
    surcharge_goods = models.FloatField('Доплата за товары', default=0)
    hold_goods = models.FloatField('Удержание за товары', default=0)
    hold_substitution = models.FloatField('Удержание за подмену товара', default=0)
    hold_furniture = models.FloatField('Удержание за мебель', default=0)
    hold_for_defects = models.FloatField('Удержание за брак', default=0)
    subsidies = models.FloatField('Субсидии', default=0)
    debt = models.FloatField('Долг', default=0)
    penalty = models.FloatField('Штраф', default=0)
    supplier_returns = models.FloatField('Возвраты поставщику', default=0)
    extra_motivation = models.FloatField('Дополнительная мотивация', default=0)
    zero_substitution_effect = models.FloatField('Нулевой эффект подмены', default=0)
    return_incorrect_mark = models.FloatField('Возврат удержаний за некорректную отметку о браке', default=0)
    extra_nds = models.FloatField('Доплата НДС', default=0)
    package_compensation = models.FloatField('Компенсация за пакеты', default=0)
    hold_non_returned = models.FloatField('Удержано за невозврат товара', default=0)
    total_charge = models.FloatField('Всего начислено', default=0)
    total_hold = models.FloatField('Всего удержано', default=0)
    total = models.FloatField('Доход', default=0)

    def __str__(self):
        formatted_from_date = self.from_date.strftime("%d-%m-%Y")
        formatted_to_date = self.to_date.strftime("%d-%m-%Y")
        return f'Оплата от WB по ПВЗ: {self.pvz_id.title} за период {formatted_from_date} - {formatted_to_date}, на сумму: {self.total}'


class PVZPaiment(models.Model):
    pvz_id = models.ForeignKey(
        PVZ,
        verbose_name='Пункт выдачи',
        on_delete=models.CASCADE,
        related_name='pvz_payments'
    )
    date = models.DateField('Дата выплаты', default=datetime.datetime.utcnow)
    employee_id = models.ForeignKey(
        Employee,
        verbose_name='Сотрудник',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    number_days = models.IntegerField('Cмены', null=False, default=0)
    boxes_count = models.IntegerField('Коробки', default=0)
    extra_payment = models.IntegerField('Бонус(руб.)', default=0)
    add_penalty = models.IntegerField('Штраф к начислению', default=0)
    surcharge_penalty = models.IntegerField('Штраф к удержанию', default=0)
    total = models.IntegerField('Итого к выплате', null=False, default=0)
    is_closed = models.BooleanField('Оплачен', default=False)

    def __str__(self):
        formatted_date = self.date.strftime("%d-%m-%Y")

        return f'Выплата расчет ЗП сотруднику {self.employee_id.name} от {formatted_date}'


class Category(models.Model):
    title = models.CharField('Название', max_length=50)

    def __str__(self):
        return self.title


class PVZOutcomes(models.Model):
    date = models.DateField('Дата', default=datetime.datetime.utcnow)
    sum = models.DecimalField('Сумма', blank=True, default=0, decimal_places=2, max_digits=10)
    pvz = models.ForeignKey(PVZ, verbose_name='ПВЗ',
                            on_delete=models.CASCADE,
                            related_name='outcomes'
                            )
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 on_delete=models.CASCADE,
                                 related_name='outcomes'
                                 )
    description = models.CharField('Описание', max_length=150, null=True, blank=True)

    def __str__(self):
        return f'Расход на: {self.sum}, ПВЗ {self.pvz}'


class Wallet(models.Model):
    title = models.CharField('Название счета', max_length=100)
    balance = models.DecimalField('Текущий баланс', max_digits=10, decimal_places=2, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets', verbose_name='Пользователь')
    is_archived = models.BooleanField('В архиве', default=False)
    for_salary = models.BooleanField('Зарплатный', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=datetime.datetime.utcnow)

    def save(self, *args, **kwargs):
        if self.for_salary:
            current_user = self.user_id
            existing_salary_wallets = Wallet.objects.filter(user=current_user, is_archived=False, for_salary=True).exclude(pk=self.pk)
            if existing_salary_wallets.exists():
                raise ValueError('У вас уже есть зарплатные счета.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} Баланс: {self.balance}'


class WalletTransaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = 'IN', _('Поступление')
        OUTCOME = 'OUT', _('Списание')

    operation_date = models.DateTimeField('Дата операции', default=datetime.datetime.utcnow)
    wallet_id = models.ForeignKey(Wallet, on_delete=models.CASCADE, verbose_name='Счет', related_name='transactions')
    transaction_type = models.CharField('Тип операции', max_length=20, choices=TransactionType.choices)
    transaction_sum = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    description = models.CharField('Описание', max_length=200, null=True, blank=True)
    last_modified = models.DateTimeField('Дата создания', auto_now=datetime.datetime.utcnow)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Основание', related_name='transactions')
    object_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Операция от {self.operation_date} по счету {self.wallet_id} на сумму {self.transaction_sum}'
