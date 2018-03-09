import collections
import json
import requests
import hashlib
from datetime import datetime, date, time, timedelta

class hotel_api():
    def __init__(self):
        print("hi")

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

    def realSignature(self, token, marker, body):
        m = hashlib.md5()
        m.update((token + ':' + marker + ':' + self.makeSignature(body)).encode('utf-8'))
        return m.hexdigest()

api = hotel_api()

# r = requests.get('http://mytripwander.com/test/tokyo-round-trip.json')
# data = r.text

token = "0852ce5f48b5d4158ed28dd23e7ddd44"
marker = "143764"

iata = "HKG"
hotelId = "520684"
cityId = ""

customerIP = "127.0.0.1"

checkIn = datetime.today().strftime("%Y-%m-%d")
checkOut = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")

checkIn = datetime(2018,4,3).strftime("%Y-%m-%d")
checkOut = datetime(2018,4,5).strftime("%Y-%m-%d")

adultsCount = 2
lang = "en"
currency = "USD"
waitForResult = "1"

passenger_data = {
    'hotelId': hotelId,
    'customerIP': customerIP,
    'checkIn': checkIn,
    'checkOut': checkOut,
    'adultsCount': adultsCount,
    'lang': lang,
    'currency': currency,
    'waitForResult': waitForResult
}

signature = api.realSignature(token, marker, passenger_data)

passenger_data['signature'] = signature
passenger_data['marker'] = marker

body_request = passenger_data.__str__().replace("\'","\"")

print(body_request)

#mulai masukin
url = "http://engine.hotellook.com/api/v2/search/start.json?"
data = requests.get(url, params=passenger_data)
print(data.status_code)
print(data.url)
hotel_json = json.JSONEncoder().encode(data.json())

f = open("hotel.json","w+")
f.write(hotel_json)
f.close()


# #search-result
# url = "http://api.travelpayouts.com/v1/flight_search_results"
# params = {"uuid": uuid}
# search_result = requests.get(url, params)
# print(search_result.status_code)
#
# # LOCAL
# # search_result = requests.get('http://mytripwander.com/test/tokyo-round-trip.json')
# #
# # print(len(search_result.json()))
#
# fix = api.processData(search_result.json())[0:5:1]
#
# print(fix)
