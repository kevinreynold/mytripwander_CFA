import collections
import json
import requests
import hashlib
import time as tt
from operator import itemgetter
from datetime import datetime, date, time, timedelta

class flight_api():
    def __init__(self, trip_class, adults, children, origin, destination, start_date, return_date=None, round_trip=False):
        self.token = "0852ce5f48b5d4158ed28dd23e7ddd44"
        self.marker = "143764"
        self.host = "mytripwander.com"
        self.user_ip = "127.0.0.1"
        self.locale = "en"

        self.trip_class = trip_class # Y / C
        self.adults = adults
        self.children = children

        self.origin = origin
        self.destination = destination
        self.start_date = start_date
        self.return_date = return_date
        self.round_trip = round_trip

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
        m.update((self.token + ':' + self.makeSignature(body)).encode('utf-8'))
        return m.hexdigest()

    def changeFormatDuration(self, duration):
        result = ""
        if duration > 60:
            result += ("00" + str(duration // 60))[-2:] + "h "
            result += str(duration % 60) + "m"
        else:
            result += str(duration) + "m"
        return result

    def changeStringToDateTime(self, date, time):
        split_date = date.split('-')
        split_time = time.split(':')

        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])

        hour = int(split_time[0])
        minute = int(split_time[1])

        return datetime(year, month, day, hour, minute)

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
                        # temp_ticket['total_duration_readable'] = self.changeFormatDuration(ticket_data['total_duration'])
                        temp_ticket['total_duration'] = ticket_data['total_duration']
                        temp_ticket['search_id'] = search_id
                        temp_ticket['search_at'] = datetime.today().strftime("%Y-%m-%d")

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
                        # temp_ticket['departure_first_date'] = ""
                        # temp_ticket['arrival_first_date'] = ""
                        # temp_ticket['departure_second_date'] = ""
                        # temp_ticket['arrival_second_date'] = ""
                        for s in range(len(ticket_data['segment'])):
                            temp_ticket['segment'].append({})
                            temp_ticket['segment'][s]['flight'] = []

                            for f in range(len(ticket_data['segment'][s]['flight'])):
                                flight = {
                                    'operated_by' : ticket_data['segment'][s]['flight'][f]['operated_by'],
                                    'class' : "Economy" if ticket_data['segment'][s]['flight'][f]['trip_class'] == "Y" else "Business",
                                    'duration' : self.changeFormatDuration(ticket_data['segment'][s]['flight'][f]['duration']),
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
                                    if s == 0: # one-way
                                        temp_date = ticket_data['segment'][s]['flight'][f]['departure_date']
                                        temp_time = ticket_data['segment'][s]['flight'][f]['departure_time']
                                        # temp_ticket['departure_first_date'] = self.changeStringToDateTime(temp_date, temp_time)

                                        temp_date = ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival_date']
                                        temp_time = ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival_time']
                                        # temp_ticket['arrival_first_date'] = self.changeStringToDateTime(temp_date, temp_time)
                                    elif s == 1: # round-trip
                                        temp_date = ticket_data['segment'][s]['flight'][f]['departure_date']
                                        temp_time = ticket_data['segment'][s]['flight'][f]['departure_time']
                                        # temp_ticket['departure_second_date'] = self.changeStringToDateTime(temp_date, temp_time)

                                        temp_date = ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival_date']
                                        temp_time = ticket_data['segment'][s]['flight'][len(ticket_data['segment'][s]['flight'])-1]['arrival_time']
                                        # temp_ticket['arrival_second_date'] = self.changeStringToDateTime(temp_date, temp_time)

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
                                        'duration': self.changeFormatDuration(ticket_data['segment_durations'][s]),
                                        'transit': []
                                    }
                                    temp_ticket['display'].append(temp_display)
                                else:
                                    temp_ticket['display'][s]['transit'].append(ticket_data['segment'][s]['flight'][f]['departure'])

                                temp_ticket['segment'][s]['flight'].append(flight)
                        ticket_list.append(temp_ticket)
        return ticket_list

    def passenger_data(self):
        segment = []
        segment.append({'origin': self.origin, 'destination': self.destination, 'date': self.start_date})
        if self.round_trip == True:
            segment.append({'origin': self.destination, 'destination': self.origin, 'date': self.return_date})

        passenger_data = {
            'host': self.host,
            'locale': self.locale,
            'marker': self.marker,
            'passengers': {'adults': self.adults,'children': self.children,'infants': 0},
            'segments': segment,
            'trip_class': self.trip_class,
            'user_ip': self.user_ip,
            'know_english': "true",
            'currency': "usd"
        }

        signature = self.realSignature(passenger_data)
        passenger_data['signature'] = signature

        return passenger_data

    def flight_search(self):
        passenger_data = self.passenger_data()
        #mulai masukin
        url = "http://api.travelpayouts.com/v1/flight_search"
        data = requests.post(url, json=passenger_data)
        uuid = data.json()['meta']['uuid']

        tt.sleep(5)

        #search-result
        url = "http://api.travelpayouts.com/v1/flight_search_results"
        params = {"uuid": uuid}
        search_result = requests.get(url, params)

        print("Status : " + str(search_result.status_code))
        flight_result = self.processData(search_result.json())
        return flight_result

    def flight_search_local(self):
        search_result = requests.get('http://mytripwander.com/test/flight-api-result.json')
        flight_result = api.processData(search_result.json())
        return flight_result

    def save_result(self, flight_result):
        f = open("flight.json","w+")
        f.write(str(json.dumps(flight_result)))
        f.close()
        print("Done!!!")

    @staticmethod
    def sorted_one_way_arrival_flight_result(flight_result):
        # bisa dapat jam 0050
        # rows = [x for x in flight_result if (time(1) < x['arrival_first_date'].time() < time(12)) or x['arrival_first_date'].time() > time(18)]
        rows = [x for x in flight_result if (time(10) < time(int(x['display'][0]['arrival_airport']['time'][0:2]),int(x['display'][0]['arrival_airport']['time'][3:])) < time(16))]

        result = flight_result[0]
        print("JUMLAH TIKET ASLI : " + str(len(flight_result)))

        if(len(rows) > 0):
            print("JUMLAH TIKET : " + str(len(rows)))
            print("ADA ARRIVAL FLIGHT ANTARA JAM 10 HINGGA 16")
            result = min(rows, key=itemgetter('unified_price'))
        return result

    @staticmethod
    def sorted_one_way_departure_flight_result(flight_result):
        rows = [x for x in flight_result if (time(17) < time(int(x['display'][0]['departure_airport']['time'][0:2]),int(x['display'][0]['departure_airport']['time'][3:])) < time(21))]

        result = flight_result[0]
        print("JUMLAH TIKET ASLI : " + str(len(flight_result)))

        if(len(rows) > 0):
            print("JUMLAH TIKET : " + str(len(rows)))
            print("ADA GO BACK FLIGHT ANTARA JAM 17 HINGGA 21")
            result = min(rows, key=itemgetter('unified_price'))
        return result

    @staticmethod
    def sorted_round_trip_flight_result(flight_result):
        row = []
        offset_time = 18
        while len(rows) == 0:
            rows = [x for x in flight_result if x['departure_second_date'].time() > time(offset_time)]
            offset_time -= 3
        result = min(rows, key=itemgetter('unified_price'))
        return result

# trip_class = "Y"
# adults = 2
# children = 1
#
# origin = "SUB"
# destination = "TPE"
# start_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
# return_date = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
# round_trip = False
#
# api = flight_api(trip_class=trip_class, adults=adults, children=children, origin=origin, destination=destination, start_date=start_date, return_date=return_date, round_trip=round_trip)
#
# flight_result = api.flight_search()
#
# if api.round_trip == False:
#     ticket_data = flight_api.sorted_one_way_flight_result(flight_result)
# else:
#     ticket_data = flight_api.sorted_round_trip_flight_result(flight_result)
# api.save_result(ticket_data)

# TEST
# trip_class = "Y"
# adults = 2
# children = 1
#
# origin = "SUB"
# destination = "DPS"
# start_date = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
# return_date = (datetime.today() + timedelta(days=10)).strftime("%Y-%m-%d")
# round_trip = True
#
# api = flight_api(trip_class=trip_class, adults=adults, children=children, origin=origin, destination=destination, start_date=start_date, return_date=return_date, round_trip=round_trip)
#
# passenger_data = api.passenger_data()
# print(str(json.dumps(passenger_data)))
#
# flight_result = api.flight_search()
# api.save_result(flight_result)
