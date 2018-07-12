import numpy as np
import collections
import random
import json
import requests
import time as tt
import copy
from db import db
from datetime import datetime, date, time, timedelta
from trip import break_stop, trip
from CFA import CCells, CFA
from flight import flight_api
from hotel import hotel_api

class trip_schedule():
    def __init__(self, request_data, iteration=25000):
        self.db_access = db()

        # HEADER #
        self.header = request_data['header']
        self.user_id = self.header['user_id']
        self.schedule_id = self.header['schedule_id']

        self.plan_data = json.loads(self.header['plan_data'])

        self.city_origin = self.plan_data['first_city_code']
        self.start_date = datetime.combine(datetime.strptime(self.plan_data['start_date'], "%Y-%m-%d"), datetime.min.time())

        self.start_hour = self.plan_data['start_hour'][0:2] + self.plan_data['start_hour'][3:]
        self.end_hour = self.plan_data['end_hour'][0:2] + self.plan_data['end_hour'][3:]
        self.budget = self.plan_data['budget'].lower()

        self.return_here = self.plan_data['return_here']
        # adult maks 4
        # children + infant maks 3
        self.adult = int(self.plan_data['passenger']['adults'])
        self.children = int(self.plan_data['passenger']['children'])

        self.must_see = int(self.plan_data['interests'][0]['value'])
        self.culture = int(self.plan_data['interests'][1]['value'])
        self.nature = int(self.plan_data['interests'][2]['value'])
        self.recreation = int(self.plan_data['interests'][3]['value'])

        self.hotel_stay_dur = 60
        self.airport_stay_dur = 60

        # detail
        self.detail = []
        for list_dest in self.plan_data['list_destination']:
            temp = {
                'country_code': list_dest['country_code'],
                'starting_city': list_dest['city_code'],
                'stay_duration': int(list_dest['stay'])
            }
            print(temp)
            self.detail.append(temp)

        # self.arrival_hour = "1015"
        # self.go_back_hour = "2200"

        #cfa
        self.iteration = iteration
        self.pop_size = 200
        self.R1 = 0.25
        self.R2 = -0.55
        self.V1 = 5
        self.V2 = -1.1

        #flight
        self.flight_plan = []

        #hotel
        self.hotel_plan = []

        self.trip_plan_data = copy.copy(self.plan_data)
        self.trip_city_plan_data = []

    def changeDateTime(self, datetime, time):
        hours = int(time[0:2])
        minutes = int(time[2:])
        new_datetime = datetime.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    def getListCityTour(self, country_code, starting_city, stay_duration):
        list_city = self.db_access.getAllCityByCountry(country_code)

        list_city_tour = []
        list_stay_duration = []
        list_city_tour.append(starting_city)
        if stay_duration == 4:
            list_stay_duration.append(2)
            day_left = stay_duration - 2
        else:
            list_stay_duration.append(3)
            day_left = stay_duration - 3

        current_place = self.db_access.getFirstPlaceByCity(starting_city)['place_id']

        while(day_left > 0):
            if day_left == 3:
                day_left -= 3
                list_stay_duration.append(3)
            else:
                day_left -= 2
                list_stay_duration.append(2)
            next_city = self.db_access.getNearestCityById(current_place, list_city_tour)
            list_city_tour.append(next_city)
            current_place = self.db_access.getFirstPlaceByCity(next_city)['place_id']

        result = {}
        result['list_city'] = list_city_tour
        result['list_stay_duration'] = list_stay_duration

        return result

    def doFlightSearch(self, origin, dest, flight_date, type='arrival'):
        #offset --> urutan NEGARA
        #type   --> arrival / go_back

        trip_class = "Y"
        adults = self.adult
        children = self.children

        origin = origin
        destination = dest
        start_date = flight_date.strftime("%Y-%m-%d")

        api = flight_api(trip_class=trip_class, adults=adults, children=children, origin=origin, destination=destination, start_date=start_date)

        flight_result = api.flight_search()
        if type == 'arrival':
            ticket_data = flight_api.sorted_one_way_arrival_flight_result(flight_result)
        elif type == 'go_back':
            ticket_data = flight_api.sorted_one_way_departure_flight_result(flight_result)

        self.flight_plan.append(json.loads(json.dumps(ticket_data)))

        return ticket_data
        print('Buy Ticket Sucess')

    def doHotelSearch(self, check_in, check_out, hotel_id):
        checkIn = check_in.strftime("%Y-%m-%d")
        checkOut = check_out.strftime("%Y-%m-%d")

        print('CheckIn: ' + str(checkIn) + ' || ' + 'CheckOut: ' + str(checkOut))

        adults = self.adult
        children = self.children

        api = hotel_api(adults=adults, children=children, checkIn=checkIn, checkOut=checkOut)
        hotel_data = api.hotel_search("hotel", hotel_id)
        if hotel_data:
            self.hotel_plan.append(hotel_data)
        else:
            self.hotel_plan.append({'hotel_id': hotel_id})
            print("NO ROOMS AVAILABLE")

        return hotel_data
        print('Book Hotel Sucess')

    def changeQueryResult(self, place):
        result = {
            'place_id' : place.place_id,
            'category_id' : place.category_id,
            'category_name' : place.category_place.name,
            'city_code' : place.city_code,
            'city_name' : place.city.city_name,
            'latitude' : place.latitude,
            'longitude' : place.longitude,
            'name' : place.name,
            'address' : place.address,
            'phone_number' : place.phone_number,
            'rating' : place.rating,
            'reviews' : place.reviews,
            'description' : place.description,
            'avg_dur' : place.avg_dur,
            'opening_hours' : json.loads(place.opening_hours),
            'types' : place.types,
            'interests' : place.interests,
            'url' : place.url,
            'photo_name' : place.photo_name,
            'extension' : place.extension,
            'misc' : place.misc,
        }
        return result

    def save_result(self, file_name, data):
        f = open(file_name, "w+", encoding='utf-8')
        f.write(str(json.dumps(data)))
        f.close()
        print("Done!!!")

    def save_database(self):
        schedule_id = self.schedule_id
        user_id = self.user_id

        nplan_data = str(json.dumps(self.trip_plan_data))
        ncity_plan_data = str(json.dumps(self.trip_city_plan_data))
        nflight_plan = str(json.dumps(self.flight_plan))

        description = "route " + str(schedule_id)
        created_at = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        self.db_access.setNewTrip(user_id=user_id, plan_data=nplan_data, city_plan_data=ncity_plan_data, flight_plan=nflight_plan, description=description, created_at=created_at)

        self.db_access.updateDoneAtTripSchedule(schedule_id=str(schedule_id), done_at=created_at)

    def send_notif(self):
        total_days_trip = 0
        for i in range(len(self.trip_plan_data['list_destination'])):
            total_days_trip = total_days_trip + self.trip_plan_data['list_destination'][i]['stay']

        dest_title = ""
        for i in range(len(self.trip_plan_data['list_destination'])):
            dest_title = dest_title + self.trip_plan_data['list_destination'][i]['country_name']
            if(i != len(self.trip_plan_data['list_destination'])-1):
                dest_title = dest_title + ' - '

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=AAAAWN_fPMk:APA91bGnOj0MsFIWy5W4XbGAeeAghOLaLG1NICp0LAdvdpWcjERANcSqpv9kMPJp2p-AyxKhZXkIQLn7g19Etve8CxEgl-zIUAAtNkgDNfpTVxhajRqOqpKm0z9bRGY-LZaAzYfY1AHQ'
        }

        device_token = "eay5Vd5HTtQ:APA91bGeQan6URkfE6EOVrQQY9pGfKCXTzgn5Du_4WEqvsBOyttZpwwQlbnRgfDgOKHTfoaabMoZxfzFWJLNfsBZgP96Beza9Jgx9ZswdQlkhkic4oJFNWD_7NEBNkuNU-yTEQqcktHY"
        notif_data = {
         "to" : device_token,
         "notification" : {
             "title" : "Your itinerary is ready",
             "body": str(total_days_trip) + ' Days Trip | ' + dest_title
         },
        }

        url = "https://fcm.googleapis.com/fcm/send"
        data = requests.post(url, json=notif_data, headers=headers)
        print('Push Notification Success!')

    def run(self):
        current_date = self.start_date
        offset_day = 0

        for i in range(len(self.detail)):
            per_detail = self.detail[i]
            country = per_detail['country_code']
            city = per_detail['starting_city']
            stay_duration = per_detail['stay_duration']

            list_city = self.db_access.getAllCityByCountry(country)

            if len(list_city) == 1 or stay_duration == 3:
                print("SENDIRI")
                # last_airport = True if i < len(self.detail)-1 self.return_here else False

                # beli tiket pesawat
                if i == 0:
                    print("BARU")
                    city_origin = self.city_origin
                    arrival_ticket_data = self.doFlightSearch(city_origin, city, current_date, 'arrival')
                else:
                    # temp_country = self.detail[i-1]['country_code']
                    # temp_city = self.detail[i-1]['starting_city']
                    # temp_stay_duration = self.detail[i-1]['stay_duration']
                    # list_tour = self.getListCityTour(temp_country, temp_city, temp_stay_duration)
                    # city_origin = list_tour['list_city'][len(list_tour['list_city'])-1]
                    print("LAMA")
                    arrival_ticket_data = self.flight_plan[len(self.flight_plan)-1]
                    print(str(arrival_ticket_data))

                # print(str(arrival_ticket_data))
                arrival_airport = arrival_ticket_data['display'][0]['arrival_airport']['airport']['code']
                departure_airport = arrival_ticket_data['display'][0]['arrival_airport']['airport']['code']

                arrival_hour = arrival_ticket_data['display'][0]['arrival_airport']['time'][0:2] + arrival_ticket_data['display'][0]['arrival_airport']['time'][3:]
                go_back_hour = self.end_hour
                # print("Airport Arrival: ", str(arrival_airport))
                # print("Airport Arrival Time: ", arrival_hour)

                arrival_date = datetime.combine(datetime.strptime(arrival_ticket_data['display'][0]['arrival_airport']['date'], "%Y-%m-%d"), datetime.min.time())
                go_back_date = arrival_date + timedelta(days=stay_duration-1) # tanggal CHECKOUT

                #ubah current_date
                current_date = arrival_date
                # print('Current Date:', str(current_date))

                print(str(go_back_date))
                tt.sleep(15)

                if i < len(self.detail)-1:
                    print('PINDAH NEGARA')
                    city_origin = self.detail[i+1]['starting_city']
                    go_back_ticket_data = self.doFlightSearch(arrival_airport, city_origin, go_back_date, 'arrival')
                    # print(str(go_back_ticket_data))
                    departure_airport = go_back_ticket_data['display'][0]['departure_airport']['airport']['code']
                    go_back_hour = go_back_ticket_data['display'][0]['departure_airport']['time'][0:2] + go_back_ticket_data['display'][0]['departure_airport']['time'][3:]
                    # print("Airport Go Back: ", str(departure_airport))
                    # print("Airport Go Back Time: ", go_back_hour)
                    last_airport = True
                else:
                    if self.return_here == True or i != len(self.detail)-1:
                        if self.return_here == True:
                            print('PULKAM LAGI')
                            flight_type = 'go_back'
                        elif i != len(self.detail)-1:
                            print('PINDAH NEGARA')
                            flight_type = 'arrival'

                        city_origin = self.city_origin

                        print('flight_type :' + flight_type)
                        go_back_ticket_data = self.doFlightSearch(arrival_airport, city_origin, go_back_date, flight_type)
                        # print(str(go_back_ticket_data))
                        departure_airport = go_back_ticket_data['display'][0]['departure_airport']['airport']['code']
                        go_back_hour = go_back_ticket_data['display'][0]['departure_airport']['time'][0:2] + go_back_ticket_data['display'][0]['departure_airport']['time'][3:]
                        # print("Airport Go Back: ", str(departure_airport))
                        # print("Airport Go Back Time: ", go_back_hour)
                        last_airport = True
                    else:
                        print('TIDAK PULKAM')
                        last_airport = False

                vbreak_stop = break_stop(city=city, first_place=arrival_airport, last_place=departure_airport,
                                        arrival_date=arrival_date, arrival_hour=arrival_hour,
                                        go_back_date=go_back_date, go_back_hour=go_back_hour)

                print("arrival_date : " + str(arrival_date) + " | arrival_hour : " + str(arrival_hour))
                print("go_back_date : " + str(go_back_date) + " | go_back_hour : " + str(go_back_hour))

                vtrip = trip(break_stop=vbreak_stop, last_airport=last_airport, budget=self.budget,
                            start_hour=self.start_hour, end_hour=self.end_hour,
                            must_see=self.must_see, recreation=self.recreation, culture=self.culture, nature=self.nature,
                            hotel_stay_dur=self.hotel_stay_dur, airport_stay_dur=self.airport_stay_dur)

                vcfa = CFA(iteration=self.iteration, pop_size=self.pop_size, R1=self.R1, R2=self.R2, V1=self.V1, V2=self.V2, problem=vtrip)
                vcfa.run()

                print(vtrip.break_stop.city + " " + str(vtrip.total_days) + " HARI")
                print("Best Fitness : " + str(1/vcfa.best_cell.fitness) +
                      " | Iteration : " + str(vcfa.iteration) + " | Population : " + str(vcfa.population_size) +
                      " | R1 : " + str(vcfa.R1) + " | R2 : " + str(vcfa.R2) +
                      " | V1 : " + str(vcfa.V1) + " | V2 : " + str(vcfa.V2))
                print("Must See : " + str(vtrip.must_see_interest) + " | Recreation : " + str(vtrip.recreation_interest) +
                      " Culture : " + str(vtrip.culture_interest) + " | Nature : " + str(vtrip.nature_interest))

                tt.sleep(15)

                list_dest_trip = vtrip.showResultNew(vcfa.best_cell.other['route'], vcfa.problem.start_date, offset_day)
                print(vcfa.best_cell.other['misc'])
                print(vcfa.best_cell.other['is_too_late'])
                print(vcfa.best_cell.other['misc2'])
                print(vcfa.best_cell.other['last_place_id'])

                #simpan hotel
                hotel_id = str(vcfa.best_cell.other['misc2'])
                print('Hotel ID:',hotel_id)
                hotel_data = self.doHotelSearch(current_date, go_back_date, hotel_id)
                # print(hotel_data)

                #buat trip city plan data
                city_plan_data = {}
                city_plan_data['already_open'] = True
                city_plan_data['hotel_go_back_duration'] = vtrip.hotel_stay_dur
                city_plan_data['arrival'] = arrival_ticket_data['display'][0]
                city_plan_data['arrival_airport'] = self.db_access.getDataById(arrival_airport)
                city_plan_data['arrival_airport']['opening_hours'] = json.loads(city_plan_data['arrival_airport']['opening_hours'])
                city_plan_data['arrival_duration'] = vtrip.airport_stay_dur

                if last_airport == True:
                    city_plan_data['go_back'] = go_back_ticket_data['display'][0]
                    city_plan_data['go_back_airport'] = self.db_access.getDataById(departure_airport)
                    city_plan_data['go_back_airport']['opening_hours'] = json.loads(city_plan_data['go_back_airport']['opening_hours'])
                    # city_plan_data['go_back_duration'] = vtrip.airport_stay_dur
                    city_plan_data['go_back_duration'] = 0

                city_detail_data = self.db_access.getCityDetail(city)
                city_plan_data['cities'] = []
                city_plan_data_city = {}
                city_plan_data_city['booking_data'] = {
                    'adults': self.adult,
                    'children': self.children,
                    'checkin': arrival_date.strftime("%Y-%m-%d"),
                    'checkout': go_back_date.strftime("%Y-%m-%d"),
                    'place_id': city_detail_data['hotel_city_id'],
                    'type': 'city'
                }
                city_plan_data_city['city_code'] = city_detail_data['city_code']
                city_plan_data_city['city_name'] = city_detail_data['city_name']
                city_plan_data_city['day'] = stay_duration
                city_plan_data_city['hotel'] = hotel_data if hotel_data else {}
                city_plan_data_city['hotel_city_id'] = city_detail_data['hotel_city_id']
                city_plan_data_city['hotel_data'] = self.db_access.getHotelDataByHotelId(hotel_id)
                city_plan_data_city['hotel_data']['opening_hours'] = json.loads(city_plan_data_city['hotel_data']['opening_hours'])
                city_plan_data_city['id'] = 1
                city_plan_data_city['search_at'] = datetime.today().strftime("%Y-%m-%d")
                city_plan_data_city['list_dest_trip'] = list_dest_trip
                city_plan_data['cities'].append(city_plan_data_city)

                #ubah start_hour, to_another_city
                city_plan_data['cities'][0]['list_dest_trip'][0]['start_hour'] = arrival_ticket_data['display'][0]['arrival_airport']['time']
                # city_plan_data['cities'][0]['list_dest_trip'][len(city_plan_data['cities'][0]['list_dest_trip'])-1]['to_another_city'] = False

                self.trip_city_plan_data.append(city_plan_data)

                offset_day += stay_duration

                current_date = go_back_date + timedelta(days=1)
                offset_day += 1
            else:
                print("BANYAK")
                list_tour = self.getListCityTour(country, city, stay_duration)

                #ubah new plan_data
                city_detail = self.db_access.getCityDetail(list_tour['list_city'][len(list_tour['list_city'])-1])
                self.trip_plan_data['list_destination'][i]['last_city_code'] = city_detail['city_code']
                self.trip_plan_data['list_destination'][i]['last_city_name'] = city_detail['city_name']
                self.trip_plan_data['list_destination'][i]['last_hotel_city_id'] = city_detail['hotel_city_id']

                print(list_tour)

                #buat trip city plan data
                city_plan_data = {}
                city_plan_data['already_open'] = True
                city_plan_data['hotel_go_back_duration'] = self.hotel_stay_dur
                city_plan_data['cities'] = []
                offset_city_id = 1

                for j in range(len(list_tour['list_city'])):
                    tt.sleep(15)
                    city = list_tour['list_city'][j]
                    stay_duration = list_tour['list_stay_duration'][j]

                    # to_another_city = False
                    # if j < len(list_tour['list_city']) - 1:
                    #     to_another_city = True

                    if j == 0: # BERANGKAT AWAL ADA FLIGHT AWAL
                        print("11111111")
                        #beli tiket pesawat
                        if i == 0:
                            print('BARU')
                            city_origin = self.city_origin
                            arrival_ticket_data = self.doFlightSearch(city_origin, city, current_date, 'arrival')
                            # print(str(arrival_ticket_data))
                        else:
                            print('LAMA')
                            # temp_country = self.detail[i-1]['country_code']
                            # temp_city = self.detail[i-1]['starting_city']
                            # temp_stay_duration = self.detail[i-1]['stay_duration']
                            # list_tour = self.getListCityTour(temp_country, temp_city, temp_stay_duration)
                            # city_origin = list_tour['list_city'][len(list_tour['list_city'])-1]
                            arrival_ticket_data = self.flight_plan[len(self.flight_plan)-1]
                            print(str(arrival_ticket_data))

                        arrival_airport = arrival_ticket_data['display'][0]['arrival_airport']['airport']['code']
                        departure_airport = arrival_ticket_data['display'][0]['arrival_airport']['airport']['code']

                        arrival_hour = arrival_ticket_data['display'][0]['arrival_airport']['time'][0:2] + arrival_ticket_data['display'][0]['arrival_airport']['time'][3:]
                        go_back_hour = self.end_hour
                        # print("Airport Arrival: ", str(arrival_airport))
                        # print("Airport Arrival Time: ", arrival_hour)

                        arrival_date = datetime.combine(datetime.strptime(arrival_ticket_data['display'][0]['arrival_airport']['date'], "%Y-%m-%d"), datetime.min.time())
                        go_back_date = arrival_date + timedelta(days=stay_duration-1)

                        current_date = arrival_date
                        # print('Current Date:', str(current_date))
                        #
                        # print(str(go_back_date))

                        first_place = arrival_airport
                        last_place = departure_airport
                        new_arrival_hour = arrival_hour
                        new_go_back_hour = self.end_hour
                        new_last_airport = False

                        city_plan_data['arrival'] = arrival_ticket_data['display'][0]
                        city_plan_data['arrival_airport'] = self.db_access.getDataById(arrival_airport)
                        city_plan_data['arrival_airport']['opening_hours'] = json.loads(city_plan_data['arrival_airport']['opening_hours'])
                        city_plan_data['arrival_duration'] = self.airport_stay_dur

                    elif j < len(list_tour['list_city']) - 1: #PINDAH KOTA
                        print("22222222")
                        arrival_date = current_date
                        go_back_date = arrival_date + timedelta(days=stay_duration-1)

                        first_place = last_place_id
                        last_place = last_place_id
                        new_arrival_hour = self.start_hour
                        new_go_back_hour = self.end_hour
                        new_last_airport = False
                    else: #PINDAH KOTA DAN PULANG
                        if self.return_here == True or i != len(self.detail)-1:
                            print("33333333")
                            if i == len(self.detail)-1:
                                city_origin = self.city_origin
                                flight_type = 'go_back'
                                print('PULKAM')
                            else:
                                city_origin = self.detail[i+1]['starting_city']
                                flight_type = 'arrival'
                                print('PINDAH NEGARA')

                            arrival_date = current_date
                            go_back_date = arrival_date + timedelta(days=stay_duration-1)

                            print('flight_type :' + flight_type)
                            go_back_city_code = self.db_access.getAirportByCity(city)
                            go_back_ticket_data = self.doFlightSearch(go_back_city_code, city_origin, go_back_date, flight_type)
                            # print(str(go_back_ticket_data))
                            departure_airport = go_back_ticket_data['display'][0]['departure_airport']['airport']['code']
                            go_back_hour = go_back_ticket_data['display'][0]['departure_airport']['time'][0:2] + go_back_ticket_data['display'][0]['departure_airport']['time'][3:]
                            # print("Airport Go Back: ", str(departure_airport))
                            # print("Airport Go Back Time: ", go_back_hour)

                            first_place = last_place_id
                            last_place = departure_airport
                            new_arrival_hour = self.start_hour
                            new_go_back_hour = go_back_hour
                            new_last_airport = True

                            city_plan_data['go_back'] = go_back_ticket_data['display'][0]
                            city_plan_data['go_back_airport'] = self.db_access.getDataById(departure_airport)
                            city_plan_data['go_back_airport']['opening_hours'] = json.loads(city_plan_data['go_back_airport']['opening_hours'])
                            # city_plan_data['go_back_duration'] = self.airport_stay_dur
                            city_plan_data['go_back_duration'] = 0
                        else:
                            print('TIDAK PULKAM')
                            print("555555555")
                            arrival_date = current_date
                            go_back_date = arrival_date + timedelta(days=stay_duration-1)

                            first_place = last_place_id
                            last_place = last_place_id
                            new_arrival_hour = self.start_hour
                            new_go_back_hour = self.end_hour
                            new_last_airport = False

                    print('Arrival Hour:', str(new_arrival_hour))
                    print('Go Back Hour:', str(new_go_back_hour))

                    vbreak_stop = break_stop(city=city, first_place=first_place, last_place=last_place,
                                            arrival_date=arrival_date, arrival_hour=new_arrival_hour,
                                            go_back_date=go_back_date, go_back_hour=new_go_back_hour)

                    print("arrival_date : " + str(arrival_date) + " | arrival_hour : " + str(arrival_hour))
                    print("go_back_date : " + str(go_back_date) + " | go_back_hour : " + str(go_back_hour))

                    vtrip = trip(break_stop=vbreak_stop, last_airport=new_last_airport, budget=self.budget,
                                start_hour=self.start_hour, end_hour=self.end_hour,
                                must_see=self.must_see, recreation=self.recreation, culture=self.culture, nature=self.nature,
                                hotel_stay_dur=self.hotel_stay_dur, airport_stay_dur=self.airport_stay_dur)

                    vcfa = CFA(iteration=self.iteration, pop_size=self.pop_size, R1=self.R1, R2=self.R2, V1=self.V1, V2=self.V2, problem=vtrip)
                    vcfa.run()

                    print(vtrip.break_stop.city + " " + str(vtrip.total_days) + " HARI")
                    print("Best Fitness : " + str(1/vcfa.best_cell.fitness) +
                          " | Iteration : " + str(vcfa.iteration) + " | Population : " + str(vcfa.population_size) +
                          " | R1 : " + str(vcfa.R1) + " | R2 : " + str(vcfa.R2) +
                          " | V1 : " + str(vcfa.V1) + " | V2 : " + str(vcfa.V2))
                    print("Must See : " + str(vtrip.must_see_interest) + " | Recreation : " + str(vtrip.recreation_interest) +
                          " Culture : " + str(vtrip.culture_interest) + " | Nature : " + str(vtrip.nature_interest))

                    tt.sleep(15)

                    list_dest_trip = vtrip.showResultNew(vcfa.best_cell.other['route'], vcfa.problem.start_date, offset_day)
                    print(vcfa.best_cell.other['misc'])
                    print(vcfa.best_cell.other['is_too_late'])
                    print(vcfa.best_cell.other['misc2'])
                    print(vcfa.best_cell.other['last_place_id'])

                    #simpan hotel
                    hotel_id = str(vcfa.best_cell.other['misc2'])
                    print('Hotel ID:',hotel_id)
                    hotel_data = self.doHotelSearch(current_date, go_back_date, hotel_id)
                    # print(hotel_data)

                    last_place_id = vcfa.best_cell.other['last_place_id']

                    city_detail_data = self.db_access.getCityDetail(city)
                    city_plan_data_city = {}
                    city_plan_data_city['booking_data'] = {
                        'adults': self.adult,
                        'children': self.children,
                        'checkin': arrival_date.strftime("%Y-%m-%d"),
                        'checkout': go_back_date.strftime("%Y-%m-%d"),
                        'place_id': city_detail_data['hotel_city_id'],
                        'type': 'city'
                    }
                    city_plan_data_city['city_code'] = city_detail_data['city_code']
                    city_plan_data_city['city_name'] = city_detail_data['city_name']
                    city_plan_data_city['day'] = stay_duration
                    city_plan_data_city['hotel'] = hotel_data if hotel_data else {}
                    city_plan_data_city['hotel_city_id'] = city_detail_data['hotel_city_id']
                    city_plan_data_city['hotel_data'] = self.db_access.getHotelDataByHotelId(hotel_id)
                    city_plan_data_city['hotel_data']['opening_hours'] = json.loads(city_plan_data_city['hotel_data']['opening_hours'])
                    city_plan_data_city['id'] = offset_city_id

                    offset_city_id += 1

                    city_plan_data_city['search_at'] = datetime.today().strftime("%Y-%m-%d")
                    city_plan_data_city['list_dest_trip'] = list_dest_trip
                    city_plan_data['cities'].append(city_plan_data_city)

                    #ubah start_hour, to_another_city
                    if j == 0:
                        city_plan_data['cities'][0]['list_dest_trip'][0]['start_hour'] = arrival_ticket_data['display'][0]['arrival_airport']['time']
                    else:
                        city_plan_data['cities'][j]['list_dest_trip'][0]['to_another_city'] = True

                    offset_day += stay_duration

                    current_date = go_back_date + timedelta(days=1)

                self.trip_city_plan_data.append(city_plan_data)

        self.save_result("result-data/plan_data.json", self.trip_plan_data)
        self.save_result("result-data/city_plan_data.json", self.trip_city_plan_data)
        self.save_result("result-data/flight_plan.json", self.flight_plan)
        self.save_result("result-data/hotel.json", self.hotel_plan)
        self.save_database()
        # self.send_notif()

# # vcity_tour = city_tour('TW','TPE',11)
# # vcfa = CFA(iteration=1000, pop_size=15, R1=1, R2=-1, V1=2, V2=-2, problem=vcity_tour)
# # vcfa.run()
# # print(vcfa.best_cell.other['route'])
# # print(vcfa.best_cell.other['misc'])
#
# start = datetime.today()
# np.random.seed(0)
#
# db_access = db()
# trip_schedule = trip_schedule(db_access.getTripScheduleRequestData())
# # print(trip_schedule.start_date)
# # print(trip_schedule.must_see)
# # print(trip_schedule.culture)
# # print(trip_schedule.nature)
# # print(trip_schedule.recreation)
# print(trip_schedule.return_here)
# trip_schedule.run()
#
# end = datetime.today()
# execution_time = int((end-start).total_seconds())
# m, s = divmod(execution_time, 60)
# h, m = divmod(m, 60)
# print("Execution Time :", '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s))
