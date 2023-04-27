# Generated by Django 4.2 on 2023-04-09 12:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0010_regularoutcome_sum_in_default_currency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='date_of_operation',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 9, 12, 25, 33, 8516, tzinfo=datetime.timezone.utc), verbose_name='Дата операции'),
        ),
        migrations.AlterField(
            model_name='regularoutcome',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 9, 12, 25, 33, 11246, tzinfo=datetime.timezone.utc), verbose_name='Дата начала'),
        ),
    ]