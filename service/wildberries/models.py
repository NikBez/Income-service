from django.db import models


class PVZ(models.Model):
    title = models.CharField('Название ПВЗ', max_length=100)
    rent_price = models.FloatField('Стоимость аренды(месяц)', default=0)
    video_price = models.FloatField('Стоимость обслуживания камер(месяц)', default=0)
    extra_serving_price = models.FloatField('Стоимость доп. обслуживания(месяц)', default=0)

    def __str__(self):
        total = self.calc_total_serv()
        return f'ПВЗ: {self.title}, Стоит содержать:{total} руб.'

    def calc_total_serv(self):
        return self.extra_serving_price + self.video_price + self.rent_price


class Employee(models.Model):
    name = models.CharField('ФИО сотрудника', max_length=200, unique=True, default='Unnamed')
    pvz_id = models.ForeignKey(
        'PVZ',
        verbose_name='ПВЗ сотрудника',
        on_delete=models.CASCADE,
        related_name='employees'
    )
    date_of_start = models.DateField('Дата трудоустройства', null=True, blank=True)
    salary = models.FloatField('Ставка за смену', default=0)
    penalty = models.FloatField('Сумма штрафа', default=0)

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
    total = models.FloatField('Итого', default=0)

    def __str__(self):
        formatted_from_date = self.from_date.strftime("%d-%m-%Y")
        formatted_to_date = self.to_date.strftime("%d-%m-%Y")
        return f'Оплата от WB по ПВЗ: {self.pvz_id.title} за период {formatted_from_date} - {formatted_to_date}, на сумму: {self.total}'

class PVZPaiment(models.Model):
    pvz_id = models.ForeignKey(
        PVZ,
        verbose_name='ПВЗ',
        on_delete=models.CASCADE,
        related_name='pvz_payments'
    )
    from_date = models.DateField('Дата начала периода')
    to_date = models.DateField('Дата окончания периода')
    employee_id = models.ForeignKey(
        Employee,
        verbose_name='Сотрудник',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    number_days = models.IntegerField('Отработано смен', null=False, default=0)
    count_big_boxes = models.IntegerField('Количество коробок', default=0)
    extra_boxes = models.IntegerField('Количество доп.коробок', default=0)
    extra_payment = models.IntegerField('Бонус(руб.)', default=0)
    add_penalty = models.IntegerField('Сумма начисленного штраф', default=0)
    surcharge_penalty = models.IntegerField('Сумма удержанного штрафа', default=0)
    total = models.IntegerField('Итого к выплате', null=False, default=0)

    def __str__(self):
        formatted_from_date = self.from_date.strftime("%d-%m-%Y")
        formatted_to_date = self.to_date.strftime("%d-%m-%Y")
        return f'Выплата зп по сотруднику {self.employee_id.name} за период {formatted_from_date} - {formatted_to_date}'

