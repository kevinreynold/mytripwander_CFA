import collections
import json
import requests
import hashlib
import time as tt
import pymysql
from operator import itemgetter
from datetime import datetime, date, time, timedelta
from db import db

def updateCurrencyDaily(list_currency):
    for currency in list_currency:
        currency_id = str(currency['id'])
        query = 'RUB_' + currency_id
        print(query)
        data = {
            'q': query,
            'compact': 'ultra'
        }

        url = "https://free.currencyconverterapi.com/api/v5/convert?"
        data = requests.get(url, params=data)

        rate = data.json()[query]
        print(rate)
        db_access.setNewCurency(currency_id, rate)

        tt.sleep(2)

db_access = db()
list_currency = db_access.getAllCurrency()

updateCurrencyDaily(list_currency)


# for currency in list_currency:
#     currency_id = str(currency['id'])
#     currency_name = str(currency['name'])
#     print('<option>' + currency_id + ' - ' + currency_name +'</option>')
