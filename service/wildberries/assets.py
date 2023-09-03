from django.shortcuts import get_object_or_404

from wildberries.models import Employee


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


