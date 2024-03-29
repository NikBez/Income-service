# Generated by Django 4.1.7 on 2023-09-03 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wildberries', '0008_wallet_wallettransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wildberries.pvzpaiment', verbose_name='Основание'),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Название счета'),
        ),
    ]
