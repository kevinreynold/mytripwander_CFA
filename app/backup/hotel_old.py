import collections
import json
import requests
import hashlib
import time as tt
from operator import itemgetter
from datetime import datetime, date, time, timedelta

class hotel_api():
    def __init__(self, adults=1, children=0, checkIn="", checkOut= "", query=""):
        # hotel bisa kasih tau kalo ndak ada kamar yang tersedia
        self.token = "0852ce5f48b5d4158ed28dd23e7ddd44"
        self.marker = "143764"
        self.customerIP = "127.0.0.1"
        self.lang = "en"
        self.currency = "USD"
        self.waitForResult = "1"

        self.query = query
        self.checkIn = checkIn
        self.checkOut = checkOut

        self.adults = adults
        self.children = children

    def makeSignature(self, data):
        result = list()
        for k, v in sorted(data.items()):
            if isinstance(v, dict):
                result.append(self.makeSignature(v))
            elif isinstance(v, list):
                for one in v:
                    result.append(self.makeSignature(one))
            else:
                result.append(str(v))

        return ':'.join(result)

    def realSignature(self, body):
        m = hashlib.md5()
        m.update((self.token + ':' + self.marker + ':' + self.makeSignature(body)).encode('utf-8'))
        return m.hexdigest()

    def passenger_data(self):
        hotelId = self.getHotelID()[0]['id']

        passenger_data = {
            'hotelId': hotelId,
            'customerIP': self.customerIP,
            'checkIn': self.checkIn,
            'checkOut': self.checkOut,
            'adultsCount': self.adults,
            'lang': self.lang,
            'currency': self.currency,
            'waitForResult': self.waitForResult
        }

        if self.children > 0:
            passenger_data['childrenCount'] = self.children
            if self.children == 1:
                passenger_data['childAge1'] = 7
            elif self.children == 2:
                passenger_data['childAge1'] = 7
                passenger_data['childAge2'] = 7
            elif self.children == 3:
                passenger_data['childAge1'] = 7
                passenger_data['childAge2'] = 7
                passenger_data['childAge3'] = 7

        signature = api.realSignature(passenger_data)

        passenger_data['signature'] = signature
        passenger_data['marker'] = self.marker
        return passenger_data

    def hotel_search(self):
        tt.sleep(5)

        passenger_data = self.passenger_data()
        url = "http://engine.hotellook.com/api/v2/search/start.json?"
        data = requests.get(url, params=passenger_data)

        print(data.url)
        print("Status : " + str(data.status_code))
        # hotel_json = json.JSONEncoder().encode(data.json())
        hotel_json = data.json()['results']['hotels']
        return hotel_json

    def getHotelID(self):
        params = {
            'query' : self.query,
            'lang' : 'en',
            'lookFor' : 'both',
            'limit' : 10,
            'token' : self.token
        }

        url = "http://engine.hotellook.com/api/v2/lookup.json?"
        data = requests.get(url, params=params)
        result = data.json()
        return result

    def getListOfQueryResult(self):
        data = self.getHotelID()
        locations_data = data['results']['locations']
        hotels_data = data['results']['hotels']
        result = []

        for i in range(len(locations_data)):
            temp = {
                'type' : 'City',
                'name' : locations_data[i]['cityName'],
                'fullName' : locations_data[i]['fullName'],
                'id' : locations_data[i]['id']
            }
            result.append(temp)

        for i in range(len(hotels_data)):
            temp = {
                'type' : 'Hotel',
                'name' : hotels_data[i]['label'],
                'fullName' : hotels_data[i]['fullName'],
                'id' : hotels_data[i]['id']
            }
            result.append(temp)
        return result

    def save_result(self, hotel_result):
        f = open("hotel.json","w+")
        f.write(str(hotel_result))
        f.close()
        print("Done!!!")

checkIn = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
checkOut = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")

adults = 2
children = 1

hotel_name = "Hong Kong"
city_id = 4525

api = hotel_api(adults, children, checkIn, checkOut, hotel_name)
list_hotel = api.getHotelID()

api.save_result(list_hotel)
