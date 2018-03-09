import collections
import json
import requests
import hashlib
from datetime import datetime, date, time, timedelta

class api():
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

    def realSignature(self, token, body):
        m = hashlib.md5()
        m.update((token + ':' + self.makeSignature(body)).encode('utf-8'))
        return m.hexdigest()

    #ubah durationnya ya
    def processData(self, data):
        ticket_list = []
        search_id = data[len(data)-1]['search_id']
        ctr = 0

        for i in range(len(data)):
            if 'proposals' in data[i]:
                gates_info = data[i]['gates_info']
                airports = data[i]['airports']
                airlines = data[i]['airlines']
                if len(data[i]['proposals']) > 0:
                    for j in range(len(data[i]['proposals'])):
                        ticket_data = data[i]['proposals'][j]
                        temp_ticket = {}
                        image_size = 200

                        #Info
                        temp_ticket['display'] = []
                        temp_ticket['carriers'] = ticket_data['carriers']
                        temp_ticket['carriers_name'] = airlines[temp_ticket['carriers'][0]]['name']
                        temp_ticket['image_url'] = "http://pics.avs.io/" + str(image_size) + "/" + str(image_size) + "/" + str(temp_ticket['carriers'][0]) + ".png"
                        temp_ticket['is_direct'] = ticket_data['is_direct']
                        temp_ticket['segment_durations'] = ticket_data['segment_durations']
                        temp_ticket['total_duration'] = ticket_data['total_duration']
                        temp_ticket['search_id'] = search_id

                        #price
                        terms = ticket_data['terms']
                        for key, value in terms.items():
                            temp_ticket['price'] = float(value['price'])
                            temp_ticket['unified_price'] = float(value['unified_price'])
                            temp_ticket['currency'] = value['currency']
                            temp_ticket['url'] = "http://api.travelpayouts.com/v1/flight_searches/" + str(search_id) + "/clicks/" + str(value['url']) + ".json"

                        #host Info
                        for key, value in gates_info.items():
                            temp_ticket['host_name'] = value['label']

                        #flight
                        temp_ticket['segment'] = []
                        for s in range(len(ticket_data['segment'])):
                            temp_ticket['segment'].append({})
                            temp_ticket['segment'][s]['flight'] = []
                            for f in range(len(ticket_data['segment'][s]['flight'])):
                                flight = {
                                    'operated_by' : ticket_data['segment'][s]['flight'][f]['operated_by'],
                                    'class' : "Economy" if ticket_data['segment'][s]['flight'][f]['trip_class'] == "Y" else "Business",
                                    'duration' : ticket_data['segment'][s]['flight'][f]['duration'],
                                    'delay' : ticket_data['segment'][s]['flight'][f]['delay'],
                                    'departure' : {
                                        'date' : ticket_data['segment'][s]['flight'][f]['departure_date'],
                                        'time' : ticket_data['segment'][s]['flight'][f]['departure_time'],
                                        'airport': {
                                            'code' : ticket_data['segment'][s]['flight'][f]['departure'],
                                            'city' : airports[ticket_data['segment'][s]['flight'][f]['departure']]['city'],
                                            'country' : airports[ticket_data['segment'][s]['flight'][f]['departure']]['country'],
                                            'name' : airports[ticket_data['segment'][s]['flight'][f]['departure']]['name']
                                        }
                                    },
                                    'arrival' : {
                                        'date' : ticket_data['segment'][s]['flight'][f]['arrival_date'],
                                        'time' : ticket_data['segment'][s]['flight'][f]['arrival_time'],
                                        'airport': {
                                            'code' : ticket_data['segment'][s]['flight'][f]['arrival'],
                                            'city' : airports[ticket_data['segment'][s]['flight'][f]['arrival']]['city'],
                                            'country' : airports[ticket_data['segment'][s]['flight'][f]['arrival']]['country'],
                                            'name' : airports[ticket_data['segment'][s]['flight'][f]['arrival']]['name']
                                        }
                                    }
                                }

                                #display
                                if f == 0:
                                    temp_display = {
                                        'departure_airport': {
                                            'date' : ticket_data['segment'][s]['flight'][f]['departure_date'],
                                            'time' : ticket_data['segment'][s]['flight'][f]['departure_time'],
                                            'airport': {
                                                'code' : ticket_data['segment'][s]['flight'][f]['departure'],
                                                'city' : airports[ticket_data['segment'][s]['flight'][f]['departure']]['city'],
                                                'country' : airports[ticket_data['segment'][s]['flight'][f]['departure']]['country'],
                                                'name' : airports[ticket_data['segment'][s]['flight'][f]['departure']]['name']
                                            }
                                        },
                                        'arrival_airport' : {
                                            'date' : ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival_date'],
                                            'time' : ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival_time'],
                                            'airport': {
                                                'code' : ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival'],
                                                'city' : airports[ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival']]['city'],
                                                'country' : airports[ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival']]['country'],
                                                'name' : airports[ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival']]['name']
                                            }
                                        },
                                        'duration': str(ticket_data['segment_durations'][s]),
                                        'transit': []
                                    }
                                    temp_ticket['display'].append(temp_display)
                                else:
                                    temp_ticket['display'][s]['transit'].append(ticket_data['segment'][s]['flight'][f]['departure'])

                                temp_ticket['segment'][s]['flight'].append(flight)
                        ticket_list.append(temp_ticket)
        return ticket_list


api = api()

# r = requests.get('http://mytripwander.com/test/tokyo-round-trip.json')
# data = r.text

token = "0852ce5f48b5d4158ed28dd23e7ddd44"
marker = "143764"
host = "mytripwander.com"
user_ip = "127.0.0.1"
locale = "en"
trip_class = "Y"
adults = 2
children = 0
infants = 0

origin = "SUB"
destination = "SEL"
start_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
return_date = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
round_trip = False

segment = []
segment.append({'origin': origin, 'destination': destination, 'date': start_date})
if round_trip == True:
    segment.append({'origin': destination, 'destination': origin, 'date': return_date})

passenger_data = {
    'host': host,
    'locale': locale,
    'marker': marker,
    'passengers': {'adults': adults,'children': children,'infants': infants},
    'segments': segment,
    'trip_class': trip_class,
    'user_ip': user_ip,
    'know_english': "true"
}

signature = api.realSignature(token, passenger_data)

passenger_data['signature'] = signature

body_request = passenger_data.__str__().replace("\'","\"")

print(body_request)

#mulai masukin
url = "http://api.travelpayouts.com/v1/flight_search"
data = requests.post(url, json=passenger_data)
print(data.status_code)
uuid = data.json()['meta']['uuid']
print(uuid)

#search-result
url = "http://api.travelpayouts.com/v1/flight_search_results"
params = {"uuid": uuid}
search_result = requests.get(url, params)
print(search_result.status_code)

# LOCAL
# search_result = requests.get('http://mytripwander.com/test/tokyo-round-trip.json')
# print(len(search_result.json()))

flight_result = api.processData(search_result.json())

f = open("flight.json","w+")
f.write(str(flight_result))
f.close()

print("Done!!!")
