import numpy as np
import random
import json
from db import db
from datetime import datetime, date, time, timedelta

class flight():
    def __init__(self, departure_city, arrival_city, departure_date, arrival_date, departure_hour, arrival_hour):
        self.departure = {}
        self.departure['city'] = departure_city

        hours = int(departure_hour[0:2])
        minutes = int(departure_hour[2:])
        self.departure['datetime'] = departure_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        self.arrival = {}
        self.arrival['city'] = arrival_city

        hours = int(arrival_hour[0:2])
        minutes = int(arrival_hour[2:])
        self.arrival['datetime'] = arrival_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)

class trip():
    def __init__(self, start_hour="0830", end_hour="2100",
                flight=flight("SUB", "HKG", (datetime.today()-timedelta(days=1)), datetime.today(), "0950", "0950"), limit_night_next_day=time(18), hotel_stay_dur=60, airport_stay_dur=60): #hotel dan airport dalam menit
        self.db_access = db()
        self.airport = self.db_access.getAirportData()
        self.place = self.db_access.getPlaceData()
        self.food = self.db_access.getFoodData()
        self.hotel = self.db_access.getHotelData()
        self.distance = self.db_access.getDistanceData()

        self.start_hour = start_hour
        self.end_hour = end_hour
        self.flight = flight
        self.start_date = self.flight.arrival['datetime']
        self.limit_night_next_day = limit_night_next_day
        self.hotel_stay_dur = hotel_stay_dur
        self.airport_stay_dur = airport_stay_dur

        self.lunch_time_lower = time(12,00)
        self.lunch_time_upper = time(14,00)
        self.dinner_time_lower = time(18,00)
        self.dinner_time_upper = time(20,00)

    def getLowerBound(self):
        return 0

    def getUpperBound(self):
        return 1

    def getPlaceByID(self, place_id): #dictionary
        return [x for x in self.place if x['place_id'] == place_id]

    def getPlaceOpeningHoursByDay(self, place, date): #datetime
        # day --> Sunday : 0 || Saturday : 6
        opening_hours = json.loads(place['opening_hours'])
        weekday = date.isoweekday() % 7
        raw_result = opening_hours['day'][weekday]

        result = {}
        result['open'] = -1
        result['close'] = -1

        if raw_result != "Closed":
            str_hours = raw_result.split('-')
            if str_hours[0] == "2400": str_hours[0] = "2359"
            if str_hours[1] == "2400": str_hours[1] = "2359"

            #open
            hours = int(str_hours[0][0:2])
            minutes = int(str_hours[0][2:])
            result['open'] = date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            #close
            hours = int(str_hours[1][0:2])
            minutes = int(str_hours[1][2:])
            result['close'] = date.replace(hour=hours, minute=minutes, second=0, microsecond=0)

            if result['open'] > result['close']:
                result['close'] += timedelta(days=1)
        return result

    def isPlaceOpenRightNow(self, now, place, date): #now = datetime
        opening_hours = self.getPlaceOpeningHoursByDay(place, date)
        if opening_hours['open'] == -1:
            return False
        return opening_hours['open'] < now < opening_hours['close']

    def convertFitnessValue(self, fitness_value): #ke time format
        fitness = int(1 / fitness_value)
        m, s = divmod(fitness, 60)
        h, m = divmod(m, 60)
        return '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s)
        # return str(1/fitness_value)

    ################################################### v4 ######################################################
    # hanya travel_time
    # airport awal
    # pilih hotel juga (awal dan akhir)

    # ada start - end activities hour
    # end activities nya itu hanya berlaku di tempat wisata saja.
    # UNTUK 1 HARI SAJA
    # BLM BISA CEK KALO DATENGNYA TERLALU SORE
    # cek jam buka-tutup juga
    # maksimalkan tempat wisata sampai jam habis

    # kalau sampai lebih dari limit jam atau kalau sampainya subuh2 maka lanjut besok
    # untuk setiap harinya kalau jam nya kelewat batas maksmium 30 menit selama itu efektif

    # ubah format showResult dulu (1->airport, 2->tempat, 3->food, 4->hotel)

    # tambah food (asumsi makan 2 kali yaitu siang dan malam) -> paginya dianggap sudah breakfast
    # kondisi makan :
        # kalau masih berada ditempat wisata dan terdapat makanan(selama average_dur) -> maka sudah dianggap makan
        # kalau blm makan cek jam (kalau berada dijam makan) -> cari tempat makan
        # kalau diluar jam tempat makan -> cari tempat makan

    def addRoute(self, type, idx, is_stop=False):
        if type == "airport":
            type_idx = "1"
        elif type == "place":
            type_idx = "2"
        elif type == "food":
            type_idx = "3"
        elif type == "hotel":
            type_idx = "4"
        stop_idx = "0" if is_stop == False else "1"
        return type_idx + "-" + str(idx) + "-" + stop_idx

    def getDataByType(self, input):
        split_string = input.split('-')
        type_idx = split_string[0]
        idx = int(split_string[1])
        is_stop = True if int(split_string[2]) == 1 else False

        result = {}
        if type_idx == "1":
            data = self.airport[idx]
        elif type_idx == "2":
            data = self.place[idx]
        elif type_idx == "3":
            data = self.food[idx]
        elif type_idx == "4":
            data = self.hotel[idx]
        result['data'] = data
        result['is_stop'] = is_stop

        return result

    def getDimension(self):
        return len(self.place) + len(self.hotel) #+ len(self.food)

    def randomPopulation(self):
        return np.random.uniform(self.getLowerBound(), self.getUpperBound(), self.getDimension())

    def calculateFitness(self, individual):
        # ubah dulu ke index place
        place_count = len(self.place)
        hotel_count = len(self.hotel)
        # food_count = len(self.food)

        idx_place = individual[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_hotel = individual[place_count:].argsort(kind='quicksort').argsort(kind='quicksort')
        # idx_hotel = individual[place_count:(place_count+hotel_count):1].argsort(kind='quicksort').argsort(kind='quicksort')
        # idx_food = individual[(place_count+hotel_count):].argsort(kind='quicksort').argsort(kind='quicksort')

        food_offset = 0

        #start / end date and hours
        start_time = self.start_date

        hours = int(self.end_hour[0:2])
        minutes = int(self.end_hour[2:])
        end_time = start_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)

        #treshold batas jam malam
        # lower_treshold = end_time - timedelta(minutes=30)
        lower_treshold = end_time
        upper_treshold = end_time + timedelta(minutes=30)

        current_time = self.start_date

        # tanda stop index place tiap selesai perharinya
        stop_sign = place_count - 1

        travel_time_total = 0

        result = {}
        result['fitness'] = -1
        result['time'] = ""
        result['stop_sign'] = stop_sign
        result['is_too_late'] = False
        result['route'] = []
        route = []

        # AIRPORT -> HOTEL
        try:
            # urus2 barang di airport sekitar 1 jam
            travel_time_total += self.airport_stay_dur * 60
            current_time += timedelta(seconds=(self.airport_stay_dur * 60))
            route.append(self.addRoute("airport", 0, False))

            #hitung jarak dari airport ke hotel
            airport_id = self.airport[0]['place_id']
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            travel_duration = self.distance[airport_id][hotel_id]
            travel_time_total += travel_duration
            travel_time_total += self.hotel_stay_dur * 60 #checkin dkk
            current_time += timedelta(seconds=(travel_duration + (self.hotel_stay_dur * 60)))

        except KeyError:
            result['fitness'] = -1
            return result

        # kalau lebih dari jam 6 lanjut keesokan harinya
        hours = int(self.start_hour[0:2])
        minutes = int(self.start_hour[2:])
        is_too_late = True if (current_time.time() > self.limit_night_next_day) or (current_time.time() < time(hours,minutes)) else False
        if is_too_late:
            if (current_time.time() > self.limit_night_next_day): #lebih dari limit jam
                current_time = current_time + timedelta(days=1)
                current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                start_time += timedelta(days=1)
                lower_treshold += timedelta(days=1)
                upper_treshold += timedelta(days=1)
            elif (current_time.time() < time(hours,minutes)): #kalau sampai dihari yang sama tapi subuh
                # antara sampai di hotel sudah ganti hari
                # atau sampai di negara itu subuh2
                current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if current_time.day - start_time.day > 0: # jika sampai di hotel sudah ganti hari
                    start_time += timedelta(days=1)
                    lower_treshold += timedelta(days=1)
                    upper_treshold += timedelta(days=1)
            travel_time_total = 0
            route.append(self.addRoute("hotel", idx_hotel[0], True))
        else:
            route.append(self.addRoute("hotel", idx_hotel[0], False))

        # HOTEL -> PLACE PERTAMA
        try:
            # CEK MAKAN


            #hitung jarak dari hotel ke tempat wisata pertama
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            place_id = self.place[idx_place[0]]['place_id']
            travel_duration = self.distance[hotel_id][place_id]
            travel_time_total += travel_duration
            current_time += timedelta(seconds=(travel_duration))
        except KeyError:
            result['fitness'] = -1
            return result

        #hitung per tempat wisatanya
        for i in range(place_count):
            #tambah average_duration
            stay_duration = self.place[idx_place[i]]['avg_dur'] * 60
            travel_time_total += stay_duration
            current_time += timedelta(seconds=stay_duration)
            route.append(self.addRoute("place", idx_place[i], False))

            # CEK MAKAN

            # cek jam buka tutup
            # kalau misalnya lagi tutup maka diberi penalty travel_time + 10 jam
            if self.isPlaceOpenRightNow(current_time, self.place[idx_place[i]], start_time) == False:
                travel_time_total += 60 * 60 * 10

            # cek kalau masih dalam batas end activities hour
            if i < place_count - 1: #hitung antar tempat wisata
                # cek dulu kalau ketempat selanjutnya masih nutut ya capcus kalau ndak stop
                try:
                    origin_id = self.place[idx_place[i]]['place_id']
                    destination_id = self.place[idx_place[i+1]]['place_id']
                    travel_duration = self.distance[origin_id][destination_id]

                    # kalau kelewat batas jam (toleransi 30 menit) -> distop (kasih tau stopnya dimana)
                    next_dest_stay_duration =self.place[idx_place[i+1]]['avg_dur'] * 60
                    predict_next_dest_time = current_time + timedelta(seconds=(travel_duration + next_dest_stay_duration))
                    if predict_next_dest_time >= upper_treshold:
                        stop_sign = i
                        # kasih penalty -> setiap detiknya kekurangannya x 20
                        # print("BATAS!!!!!")
                        # print(predict_next_dest_time)
                        if current_time < lower_treshold:
                            penalty = int((lower_treshold - current_time).total_seconds()) * 20
                            travel_time_total += penalty
                            # print("PENALTY!!!!!")
                        break
                    else:
                        # kalau masih bisa
                        travel_time_total += travel_duration
                        current_time += timedelta(seconds=(travel_duration))
                except KeyError:
                    result['fitness'] = -1
                    return result

        try:
            #hitung jarak dari tempat wisata terakhir kembali ke hotel
            place_id = self.place[idx_place[stop_sign]]['place_id']
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            travel_duration = self.distance[place_id][hotel_id]
            travel_time_total += travel_duration
            current_time += timedelta(seconds=(travel_duration))
            route.append(self.addRoute("hotel", idx_hotel[0], True))
        except KeyError:
            result['fitness'] = -1
            return result

        # print(stop_sign)
        # print(travel_time_total)
        # print(current_time)

        result['fitness'] = 1 / travel_time_total
        result['time'] = str(current_time.__str__())
        result['stop_sign'] = stop_sign
        result['is_too_late'] = is_too_late
        result['route'] = route

        return result

    def showResultNew(self, result, start_date):
        # airport - hotel - place - hotel
        print("")
        current_time = start_date
        next_time = current_time

        data = {}
        prev_data = {}
        day = 1
        offset = 1

        print("Day - " + str(day))
        for i in range(len(result)):
            data = self.getDataByType(result[i])
            name = '{:55}'.format(data['data']['name'].encode("utf-8").__str__())
            is_stop = data['is_stop']
            if i == 0: # airport
                current_time = current_time
                next_time = current_time + timedelta(minutes=self.airport_stay_dur)

                opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + opening_hours['open'].__str__() + " - " + opening_hours['close'].__str__() + " | " + str(is_open))
            elif i == 1: # hotel pertama kali
                airport_id = prev_data['data']['place_id']
                hotel_id = data['data']['place_id']

                current_time = next_time + timedelta(seconds=self.distance[airport_id][hotel_id])
                next_time = current_time + timedelta(minutes=self.hotel_stay_dur)

                opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + opening_hours['open'].__str__() + " - " + opening_hours['close'].__str__() + " | " + str(is_open))

                # cek is_stop
                if is_stop == True:
                    offset += 1
                    day += 1
                    print("")
                    print("Day - " + str(day))

                    # hitung jarak dari hotel ke tempat wisata pertama
                    if next_time.time() > self.limit_night_next_day: #lebih dari limit jam
                        current_time = next_time + timedelta(days=1)
                    else:
                        current_time = next_time

                    hours = int(self.start_hour[0:2])
                    minutes = int(self.start_hour[2:])
                    current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    next_time = current_time

                    opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                    is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                    print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + opening_hours['open'].__str__() + " - " + opening_hours['close'].__str__() + " | " + str(is_open))
            else:
                before_place = prev_data['data']['place_id']
                current_place = data['data']['place_id']

                current_time = next_time + timedelta(seconds=self.distance[before_place][current_place])
                next_time = current_time + timedelta(minutes=data['data']['avg_dur'])

                opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + opening_hours['open'].__str__() + " - " + opening_hours['close'].__str__() + " | " + str(is_open))

                # cek is_stop
                if is_stop == True and i != len(result)-1:
                    offset += 1
                    day += 1
                    print("")
                    print("Day - " + str(day))

                    # hitung jarak dari hotel ke tempat wisata pertama
                    if next_time.time() > self.limit_night_next_day: #lebih dari limit jam
                        current_time = next_time + timedelta(days=1)
                    else:
                        current_time = next_time

                    hours = int(self.start_hour[0:2])
                    minutes = int(self.start_hour[2:])
                    current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    next_time = current_time

                    opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                    is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                    print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + opening_hours['open'].__str__() + " - " + opening_hours['close'].__str__() + " | " + str(is_open))

            prev_data = data
            offset += 1

    def showResult(self, result, stop_sign, start_date, is_too_late):
        # airport - hotel - place - hotel
        place_count = len(self.place)
        hotel_count = len(self.hotel)

        idx_place = result[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_hotel = result[place_count:].argsort(kind='quicksort').argsort(kind='quicksort')

        print(idx_place)
        print(idx_hotel)

        current_time = start_date
        next_dest = current_time + timedelta(seconds=(self.airport_stay_dur * 60))

        print("")
        print("is_too_late :", is_too_late)
        print("Airport : ", self.airport[0]['name'].encode("utf-8"), "|", self.airport[0]['place_id'], " | ", current_time.__str__(), "-", next_dest.__str__())

        # CEK IS is_too_late NANTI AJA !!!!!!!!!!!!!!!!!!!!
        if is_too_late:
            # hitung jarak dari airport ke hotel
            airport_id = self.airport[0]['place_id']
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            current_time = next_dest + timedelta(seconds=self.distance[airport_id][hotel_id])
            next_dest = current_time + timedelta(seconds=(self.hotel_stay_dur * 60))
            print("")
            print("Stay in hotel(checkin etc): ", current_time.__str__(), "-", next_dest.__str__())
            print("")

            #hitung jarak dari hotel ke tempat wisata pertama
            if next_dest.time() > self.limit_night_next_day: #lebih dari limit jam
                current_time = next_dest + timedelta(days=1)
            else:
                current_time = next_dest

            hours = int(self.start_hour[0:2])
            minutes = int(self.start_hour[2:])
            current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            next_dest = current_time

            print("Hotel : ", self.hotel[idx_hotel[0]]['name'].encode("utf-8"), "|", self.hotel[idx_hotel[0]]['place_id'], " | ", current_time.__str__(), "-", next_dest.__str__())
            # hitung jarak dari hotel ke tempat wisata pertama
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            place_id = self.place[idx_place[0]]['place_id']
            current_time = next_dest + timedelta(seconds=self.distance[hotel_id][place_id])
            next_dest = current_time + timedelta(minutes=self.place[idx_place[0]]['avg_dur'])
        else:
            # hitung jarak dari airport ke hotel
            airport_id = self.airport[0]['place_id']
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            current_time = next_dest + timedelta(seconds=self.distance[airport_id][hotel_id])
            next_dest = current_time + timedelta(seconds=(self.hotel_stay_dur * 60))

            print("Hotel : ", self.hotel[idx_hotel[0]]['name'].encode("utf-8"), "|", self.hotel[idx_hotel[0]]['place_id'], " | ", current_time.__str__(), "-", next_dest.__str__())
            # hitung jarak dari hotel ke tempat wisata pertama
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            place_id = self.place[idx_place[0]]['place_id']
            current_time = next_dest + timedelta(seconds=self.distance[hotel_id][place_id])
            next_dest = current_time + timedelta(minutes=self.place[idx_place[0]]['avg_dur'])

        for i in range(stop_sign + 1):
            if i < stop_sign:
                name = '{:50}'.format(self.place[idx_place[i]]['name'].encode("utf-8").__str__())
                travel_time = str(self.distance[self.place[idx_place[i]]['place_id']][self.place[idx_place[i+1]]['place_id']])
                opening_hours = self.getPlaceOpeningHoursByDay(self.place[idx_place[i]], current_time)
                print((i+1), ". ", name, "|", current_time.time(), "-", next_dest.time(), "|", opening_hours['open'], "-", opening_hours['close'], "|", self.isPlaceOpenRightNow(next_dest,self.place[idx_place[i]],current_time))

                current_time = next_dest + timedelta(seconds=self.distance[self.place[idx_place[i]]['place_id']][self.place[idx_place[i+1]]['place_id']])
                next_dest = current_time + timedelta(minutes=self.place[idx_place[i+1]]['avg_dur'])
            else:
                name = '{:50}'.format(self.place[idx_place[i]]['name'].encode("utf-8").__str__())
                opening_hours = self.getPlaceOpeningHoursByDay(self.place[idx_place[i]], current_time)
                print((i+1), ". ", name, "|", current_time.time(), "-", next_dest.time(), "|", opening_hours['open'], "-", opening_hours['close'], "|", self.isPlaceOpenRightNow(next_dest,self.place[idx_place[i]],current_time))
                current_time = next_dest

        #hitung jarak dari tempat wisata terakhir kembali ke hotel
        place_id = self.place[idx_place[stop_sign]]['place_id']
        hotel_id = self.hotel[idx_hotel[0]]['place_id']
        current_time = next_dest + timedelta(seconds=self.distance[place_id][hotel_id])
        print("")
        print("Arrive at hotel :", current_time.__str__())
    #############################################################################################################
