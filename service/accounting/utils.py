import requests
from dateutil.relativedelta import relativedelta
from environs import Env
from django.utils import dateformat, timezone


env = Env()
env.read_env()

CURRATERU_API_ID = env('CURRATERU_API_ID')
DEFAULT_CURRENCY = env('DEFAULT_CURRENCY')

def get_sum_in_default_currency(sum, source, date_of_operation):

    from_currancy = source.currency.short_name
    if from_currancy != DEFAULT_CURRENCY:
        today = timezone.now().date()
        if date_of_operation.date() == today:
            formated_date_of_rate = dateformat.format(date_of_operation - relativedelta(days=1), 'Y-m-d')
        else:
            formated_date_of_rate = dateformat.format(date_of_operation, 'Y-m-d')

        params = {
            'currencies': DEFAULT_CURRENCY,
            'apikey': CURRATERU_API_ID,
            'date_from': formated_date_of_rate,
            'date_to': formated_date_of_rate
        }
        responce = requests.get('https://api.freecurrencyapi.com/v1/historical', params=params)
        responce.raise_for_status()
        responce = responce.json()
        return responce['data'][formated_date_of_rate][DEFAULT_CURRENCY] * sum
    return sum

