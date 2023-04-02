# Generated by Django 4.1.7 on 2023-03-31 02:25

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_income_sum_in_default_currency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='regularoutcome',
            name='currency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='outcomes_by_currency', to='accounting.currency', verbose_name='Валюта'),
        ),
        migrations.AlterField(
            model_name='income',
            name='date_of_operation',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 31, 2, 25, 47, 123812, tzinfo=datetime.timezone.utc), verbose_name='Дата операции'),
        ),
        migrations.AlterField(
            model_name='regularoutcome',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2023, 3, 31, 2, 25, 47, 134035, tzinfo=datetime.timezone.utc), verbose_name='Дата начала'),
        ),
    ]
