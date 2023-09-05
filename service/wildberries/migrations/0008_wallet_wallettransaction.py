# Generated by Django 4.1.7 on 2023-09-02 12:40

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wildberries', '0007_employee_is_archived'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Unnamed wallet', max_length=100, verbose_name='Название счета')),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Текущий баланс')),
                ('is_archived', models.BooleanField(default=False, verbose_name='В архиве')),
                ('for_salary', models.BooleanField(default=False, verbose_name='Зарплатный')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallets', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_date', models.DateTimeField(default=datetime.datetime.utcnow, verbose_name='Дата операции')),
                ('transaction_type', models.CharField(choices=[('IN', 'Поступление'), ('OUT', 'Списание')], max_length=20, verbose_name='Тип операции')),
                ('transaction_sum', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('description', models.TextField(null=True, verbose_name='Описание')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('wallet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wildberries.wallet', verbose_name='Счет')),
            ],
        ),
    ]