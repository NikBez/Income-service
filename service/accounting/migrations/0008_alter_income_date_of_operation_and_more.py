# Generated by Django 4.1.7 on 2023-03-31 02:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0007_alter_income_date_of_operation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='date_of_operation',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 31, 2, 46, 19, 392737, tzinfo=datetime.timezone.utc), verbose_name='Дата операции'),
        ),
        migrations.AlterField(
            model_name='regularoutcome',
            name='period',
            field=models.CharField(choices=[('день', 'Day'), ('неделя', 'Week'), ('месяц', 'Month'), ('год', 'Year')], default='месяц', max_length=10, verbose_name='Периодичность'),
        ),
        migrations.AlterField(
            model_name='regularoutcome',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2023, 3, 31, 2, 46, 19, 397104, tzinfo=datetime.timezone.utc), verbose_name='Дата начала'),
        ),
    ]
