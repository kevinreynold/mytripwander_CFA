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
        self.currency = "RUB"
        self.waitForResult = "1"

        self.query = query
        self.checkIn = checkIn
        self.checkOut = checkOut

        self.adults = int(adults)
        self.children = int(children)

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

    def passenger_data(self, place_type, input_id):

        passenger_data = {
            'customerIP': self.customerIP,
            'checkIn': self.checkIn,
            'checkOut': self.checkOut,
            'adultsCount': self.adults,
            'lang': self.lang,
            'currency': self.currency,
            'waitForResult': self.waitForResult
        }

        if place_type == "hotel":
            passenger_data['hotelId'] =  input_id
        if place_type == "city":
            passenger_data['cityId'] =  input_id
            passenger_data['sortBy'] = 'popularity'
            passenger_data['sortAsc'] =  0

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

        signature = self.realSignature(passenger_data)

        passenger_data['signature'] = signature
        passenger_data['marker'] = self.marker
        return passenger_data

    def hotel_search(self, place_type, input_id):
        passenger_data = self.passenger_data(place_type, input_id)

        status_code = 500
        data = None

        while status_code != 200:
            url = "http://engine.hotellook.com/api/v2/search/start.json?"
            data = requests.get(url, params=passenger_data)

            print(data.url)
            status_code = data.status_code
            print("Status : " + str(data.status_code))
            tt.sleep(5)

        # hotel_json = json.JSONEncoder().encode(data.json())
        hotel_json = data.json()

        result = json.loads(json.dumps(hotel_json))

        if len(result['result']) > 0:
            result = result['result'][0]
            result['rooms'] = result['rooms'][0:1]
        else:
            result = None

        return result

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
        f.write(str(json.dumps(hotel_result)))
        f.close()
        print("Done!!!")


# checkIn = datetime(2018,5,16).strftime("%Y-%m-%d")
# checkOut = datetime(2018,5,20).strftime("%Y-%m-%d")
#
# adults = 2
# children = 1
#
# hotel_name = "InterContinental Hong Kong"
# city_id = '520684'
#
# hotel_id = '555118'
#
# api = hotel_api(adults=adults, children=children, checkIn=checkIn, checkOut=checkOut)
# list_hotel = api.hotel_search("hotel", hotel_id)
#
# # list_hotel = api.getHotelID()
#
# api.save_result(list_hotel)


# TEST
# checkIn = datetime(2018,7,4).strftime("%Y-%m-%d")
# checkOut = datetime(2018,7,7).strftime("%Y-%m-%d")
# 
# adults = 2
# children = 0
# 
# 
# hotel_id = '417347'
# 
# api = hotel_api(adults=adults, children=children, checkIn=checkIn, checkOut=checkOut)
# list_hotel = api.hotel_search("hotel", hotel_id)