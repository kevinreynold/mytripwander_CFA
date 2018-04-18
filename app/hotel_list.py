import collections
import json
import requests
import hashlib
import time as tt
import pymysql
from operator import itemgetter
from datetime import datetime, date, time, timedelta
from db import db
from hotel import hotel_api

db_access = db()
list_hotel = db_access.getAllHotel()

for index, hotel in enumerate(list_hotel):
    tt.sleep(1)
    query= hotel['name']
    api = hotel_api(query=query)
    result = api.getListOfQueryResult()
    if len(result) > 0:
        print(str(index) + '. ' + hotel['name'] + ' - ' + result[0]['id'])
        db_access.setHotelId(hotel['place_id'], result[0]['id'])
    else:
        print(str(index) + '. ' + hotel['name'] + ' - ' + 'NOT FOUND')
        print('NOT FOUND')
