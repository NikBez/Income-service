import requests
from dateutil.relativedelta import relativedelta
from django.utils import dateformat, timezone
from environs import Env

env = Env()
env.read_env()

FREECURRENCY_API_ID = env('FREECURRENCY_API_ID')
DEFAULT_CURRENCY = env('DEFAULT_CURRENCY')
FIXER_API_KEY = env('FIXER_API_KEY')


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
            'apikey': FREECURRENCY_API_ID,
            'date_from': formated_date_of_rate,
            'date_to': formated_date_of_rate
        }
        responce = requests.get('https://api.freecurrencyapi.com/v1/historical', params=params)
        responce.raise_for_status()
        responce = responce.json()
        return responce['data'][formated_date_of_rate][DEFAULT_CURRENCY] * sum
    return sum


def convert_currency_by_fixer(sum, from_currency):
    headers = {
        'apikey': FIXER_API_KEY
    }
    params = {
        'from': from_currency,
        'to': DEFAULT_CURRENCY,
        'amount': int(sum)
    }
    response = requests.get('https://api.apilayer.com/fixer/convert', params=params, headers=headers)
    response.raise_for_status()
    response = response.json()
    return float(response['result'])
