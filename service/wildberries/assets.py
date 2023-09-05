import datetime
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.contrib.contenttypes.models import ContentType

from wildberries.models import WalletTransaction, Wallet, PVZPaiment


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))


def update_employee_penalty(employee, to_add, to_surcharge, create=True):
    if create:
        employee.penalty += float(to_add) - float(to_surcharge)
    else:
        employee.penalty -= float(to_add) + float(to_surcharge)
    employee.save()


def create_wallet_outcome(user, sum, employee_name, object_id, update=False):
    salary_wallet, created = Wallet.objects.get_or_create(user=user, for_salary=True, is_archived=False)

    content_type = ContentType.objects.get_for_model(PVZPaiment)
    transaction_type = 'OUT'

    transaction = WalletTransaction.objects.filter(object_id=object_id).first()
    if transaction:
        prev_sum = transaction.transaction_sum

        transaction.operation_date = datetime.datetime.utcnow()
        transaction.wallet_id = salary_wallet
        transaction.transaction_type = WalletTransaction.TransactionType.OUTCOME
        transaction.description = f'Зарплата для {employee_name}'
        transaction.transaction_sum = sum
        transaction.content_type = content_type
        transaction.save()

        update_wallet_total(salary_wallet.id, transaction_type, sum, prev_sum)
    else:
        WalletTransaction.objects.create(
            operation_date=datetime.datetime.utcnow(),
            wallet_id=salary_wallet,
            transaction_type=WalletTransaction.TransactionType.OUTCOME,
            description=f'Зарплата для {employee_name}',
            transaction_sum=sum,
            content_type=content_type,
            object_id=object_id
        )
        update_wallet_total(salary_wallet.id, transaction_type, sum)

def delete_wallet_transaction(payment_id: int):
    '''
    Процедура удаляет транзакцию при удалении платежа.
    '''
    transaction_to_delete = WalletTransaction.objects.get(object_id=payment_id)
    if transaction_to_delete:
        update_wallet_total(transaction_to_delete.wallet_id.id, 'IN', transaction_to_delete.transaction_sum)
        transaction_to_delete.delete()


def update_wallet_total(wallet_id, transaction_type, transaction_sum, prev_sum=0):
    wallet = Wallet.objects.get(pk=wallet_id)
    if transaction_type == 'IN':
        new_balance = wallet.balance + transaction_sum
    elif transaction_type == 'OUT':
        new_balance = wallet.balance + prev_sum - transaction_sum
    wallet.balance = new_balance
    wallet.save()


def translate_month_titles(month_list):
    if not month_list:
        return month_list

    russin_titles = {
        'January': 'Январь',
        'February': 'Февраль',
        'March': 'Март',
        'January': 'Апрель',
        'May': 'Май',
        'June': 'Июнь',
        'July': 'Июль',
        'August': 'Август',
        'September': 'Сентябрь',
        'October': 'Октябрь',
        'November': 'Ноябрь',
        'December': 'Декабрь',
    }

    return [russin_titles[month] for month in month_list]
