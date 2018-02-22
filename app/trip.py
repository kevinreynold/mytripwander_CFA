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
                flight=flight("SUB", "HKG", (datetime.today()-timedelta(days=1)), datetime.today(), "0950", "0950")):
        self.db_access = db()
        self.place = self.db_access.getPlaceData()
        self.airport = self.db_access.getAirportData()
        self.hotel = self.db_access.getHotelData()
        self.distance = self.db_access.getDistanceData()
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.flight = flight
        self.start_date = self.flight.arrival['datetime']

    def getLowerBound(self):
        return 0

    def getUpperBound(self):
        return 1

    def getPlaceByID(self, place_id): #dictionary
        return [x for x in self.place if x['place_id'] == place_id]

    def getPlaceOpeningHoursByDay(self, place, date, mode): #datetime
        # day --> Sunday : 0 || Saturday : 6
        # mode --> "open" (0) || "close" (1)
        offset = 0 if mode == 'open' else 1
        opening_hours = json.loads(place['opening_hours'])
        weekday = date.isoweekday() % 7
        raw_result = opening_hours['day'][weekday]
        if raw_result == "Closed":
            result = -1
        else:
            str_hours = raw_result.split('-')[offset]
            hours = int(str_hours[0:2])
            minutes = int(str_hours[2:])
            result = date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        return result

    def convertFitnessValue(self, fitness_value): #ke time format
        fitness = int(1 / fitness_value)
        m, s = divmod(fitness, 60)
        h, m = divmod(m, 60)
        return '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s)
        # return str(1/fitness_value)

    ################################################### v3 ######################################################
    # hanya travel_time
    # airport awal
    # pilih hotel juga (awal dan akhir)

    # ada start - end activities hour
    # end activities nya itu hanya berlaku di tempat wisata saja.
    # UNTUK 1 HARI SAJA
    # BLM BISA CEK KALO DATENGNYA TERLALU SORE
    # cek jam buka-tutup juga - BELUM
    # maksimalkan tempat wisata sampai jam habis

    # kalau sampai lebih dari jam 18.00 maka lanjut besok
    # untuk setiap harinya kalau jam nya kelewat batas maksmium 30 menit selama itu efektif

    def getDimension(self):
        return len(self.place) + len(self.hotel)

    def randomPopulation(self):
        return np.random.uniform(self.getLowerBound(), self.getUpperBound(), self.getDimension())

    def calculateFitness(self, individual):
        # ubah dulu ke index place
        place_count = len(self.place)
        hotel_count = len(self.hotel)

        idx_place = individual[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_hotel = individual[place_count:].argsort(kind='quicksort').argsort(kind='quicksort')

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

        #kalau lebih dari jam 6 lanjut keesokan harinya
        is_too_late = True if start_time.time() > time(18) else False
        if is_too_late:
            current_time = current_time + timedelta(days=1)
            hours = int(self.start_hour[0:2])
            minutes = int(self.start_hour[2:])
            current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)

        travel_time_total = 0

        if is_too_late == False:
            try:
                # urus2 barang di airport sekitar 1 jam
                travel_time_total += 3600
                current_time += timedelta(seconds=3600)

                #hitung jarak dari airport ke hotel
                airport_id = self.airport[0]['place_id']
                hotel_id = self.hotel[idx_hotel[0]]['place_id']
                travel_duration = self.distance[airport_id][hotel_id]
                travel_time_total += travel_duration
                travel_time_total += 3600 #checkin dkk
                current_time += timedelta(seconds=(travel_duration+3600))
            except KeyError:
                return np.inf

        try:
            #hitung jarak dari hotel ke tempat wisata pertama
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            place_id = self.place[idx_place[0]]['place_id']
            travel_duration = self.distance[hotel_id][place_id]
            travel_time_total += travel_duration
            current_time += timedelta(seconds=(travel_duration))
        except KeyError:
            return np.inf

        #hitung per tempat wisatanya
        for i in range(place_count):

            #tambah average_duration
            stay_duration = self.place[idx_place[i]]['avg_dur'] * 60
            travel_time_total += stay_duration
            current_time += timedelta(seconds=stay_duration)

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
                    return np.inf


        try:
            #hitung jarak dari tempat wisata terakhir kembali ke hotel
            place_id = self.place[idx_place[stop_sign]]['place_id']
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            travel_duration = self.distance[place_id][hotel_id]
            travel_time_total += travel_duration
            current_time += timedelta(seconds=(travel_duration))
        except KeyError:
            return np.inf

        # print(stop_sign)
        # print(travel_time_total)
        # print(current_time)

        result = {}
        result['fitness'] = 1 / travel_time_total
        result['time'] = str(current_time.__str__())
        # result['time'] = str(stop_sign)
        result['stop_sign'] = stop_sign
        result['is_too_late'] = is_too_late

        return result

    def showResult(self, result, stop_sign, start_date, is_too_late):
        # airport - hotel - place - hotel
        place_count = len(self.place)
        hotel_count = len(self.hotel)

        idx_place = result[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_hotel = result[place_count:].argsort(kind='quicksort').argsort(kind='quicksort')

        current_time = start_date
        next_dest = current_time + timedelta(hours=1)

        print("")
        print("Airport : ", self.airport[0]['name'].encode("utf-8"), "|", self.airport[0]['place_id'], " | ", current_time.__str__(), " | ", next_dest.__str__())

        # hitung jarak dari airport ke hotel
        airport_id = self.airport[0]['place_id']
        hotel_id = self.hotel[idx_hotel[0]]['place_id']
        current_time = next_dest + timedelta(seconds=self.distance[airport_id][hotel_id])
        next_dest = current_time + timedelta(hours=1)

        print("Hotel : ", self.hotel[idx_hotel[0]]['name'].encode("utf-8"), "|", self.hotel[idx_hotel[0]]['place_id'], " | ", current_time.__str__(), " | ", next_dest.__str__())
        # hitung jarak dari hotel ke tempat wisata pertama
        hotel_id = self.hotel[idx_hotel[0]]['place_id']
        place_id = self.place[idx_place[0]]['place_id']
        current_time = next_dest + timedelta(seconds=self.distance[hotel_id][place_id])
        next_dest = current_time + timedelta(minutes=self.place[idx_place[0]]['avg_dur'])

        #CEK IS is_too_late NANTI AJA !!!!!!!!!!!!!!!!!!!!

        print(idx_place)
        print(idx_hotel)

        for i in range(stop_sign + 1):
            if i < stop_sign:
                print((i+1), ". ", self.place[idx_place[i]]['name'].encode("utf-8"), "|", self.place[idx_place[i]]['place_id'] ,"|", str(self.distance[self.place[idx_place[i]]['place_id']][self.place[idx_place[i+1]]['place_id']]), " | ", current_time.__str__(), " | ", next_dest.__str__())

                current_time = next_dest + timedelta(seconds=self.distance[self.place[idx_place[i]]['place_id']][self.place[idx_place[i+1]]['place_id']])
                next_dest = current_time + timedelta(minutes=self.place[idx_place[i+1]]['avg_dur'])
            else:
                print((i+1), ". ", self.place[idx_place[i]]['name'].encode("utf-8"), "|", self.place[idx_place[i]]['place_id'] ,"|", current_time.__str__(), " | ", next_dest.__str__())
                current_time = next_dest

        #hitung jarak dari tempat wisata terakhir kembali ke hotel
        place_id = self.place[idx_place[stop_sign]]['place_id']
        hotel_id = self.hotel[idx_hotel[0]]['place_id']
        current_time = next_dest + timedelta(seconds=self.distance[place_id][hotel_id])
        print(current_time.__str__())
    #############################################################################################################

    ################################################### v2 ######################################################
    # hanya travel_time
    # airport awal
    # pilih hotel juga (awal dan akhir)
    #
    # def getDimension(self):
    #     return len(self.place) + len(self.hotel)
    #
    # def randomPopulation(self):
    #     return np.random.uniform(self.getLowerBound(), self.getUpperBound(), self.getDimension())
    #
    # def calculateFitness(self, individual):
    #     # ubah dulu ke index place
    #     place_count = len(self.place)
    #     hotel_count = len(self.hotel)
    #
    #     idx_place = individual[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
    #     idx_hotel = individual[place_count:].argsort(kind='quicksort').argsort(kind='quicksort')
    #
    #     travel_time_total = 0
    #
    #     try:
    #         #hitung jarak dari airport ke hotel
    #         airport_id = self.airport[0]['place_id']
    #         hotel_id = self.hotel[idx_hotel[0]]['place_id']
    #         travel_time_total += self.distance[airport_id][hotel_id]
    #     except KeyError:
    #         travel_time_total += 99999999
    #
    #     try:
    #         #hitung jarak dari hotel ke tempat wisata pertama
    #         hotel_id = self.hotel[idx_hotel[0]]['place_id']
    #         place_id = self.place[idx_place[0]]['place_id']
    #         travel_time_total += self.distance[hotel_id][place_id]
    #     except KeyError:
    #         travel_time_total += 99999999
    #
    #     try:
    #         #hitung jarak dari tempat wisata terakhir kembali ke hotel
    #         place_id = self.place[idx_place[place_count-1]]['place_id']
    #         hotel_id = self.hotel[idx_hotel[0]]['place_id']
    #         travel_time_total += self.distance[place_id][hotel_id]
    #     except KeyError:
    #         travel_time_total += 99999999
    #
    #     for i in range(place_count):
    #         temp = 0
    #         if i < place_count - 1: #hitung antar tempat wisata
    #             try:
    #                 origin_id = self.place[idx_place[i]]['place_id']
    #                 destination_id = self.place[idx_place[i+1]]['place_id']
    #                 temp = self.distance[origin_id][destination_id]
    #             except KeyError:
    #                 temp = 99999999
    #
    #         travel_time_total += temp
    #
    #     result = {}
    #     result['fitness'] = 1 / travel_time_total
    #     result['time'] = "None"
    #     result['stop_sign'] = "None"
    #     result['is_too_late'] = "None"
    #
    #     return result
    #
    # def showResult(self, result):
    #     # airport - hotel - place - hotel
    #     place_count = len(self.place)
    #     hotel_count = len(self.hotel)
    #
    #     idx_place = result[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
    #     idx_hotel = result[place_count:].argsort(kind='quicksort').argsort(kind='quicksort')
    #
    #     try:
    #         #hitung jarak dari airport ke hotel
    #         airport_id = self.airport[0]['place_id']
    #         hotel_id = self.hotel[idx_hotel[0]]['place_id']
    #         print(self.distance[airport_id][hotel_id])
    #     except KeyError:
    #         print(99999999)
    #
    #     try:
    #         #hitung jarak dari hotel ke tempat wisata pertama
    #         hotel_id = self.hotel[idx_hotel[0]]['place_id']
    #         place_id = self.place[idx_place[0]]['place_id']
    #         print(self.distance[hotel_id][place_id])
    #     except KeyError:
    #         print(99999999)
    #
    #     print("Airport : ", self.airport[0]['name'].encode("utf-8"), "|", self.airport[0]['place_id'])
    #     print("Hotel : ", self.hotel[idx_hotel[0]]['name'].encode("utf-8"), "|", self.hotel[idx_hotel[0]]['place_id'])
    #     print(idx_place)
    #     print(idx_hotel)
    #
    #     for i in range(place_count):
    #         if i < place_count-1:
    #             print((i+1), ". ", self.place[idx_place[i]]['name'].encode("utf-8"), "|", self.place[idx_place[i]]['place_id'] ,"|", str(self.distance[self.place[idx_place[i]]['place_id']][self.place[idx_place[i+1]]['place_id']]))
    #         else:
    #             print((i+1), ". ", self.place[idx_place[i]]['name'].encode("utf-8"), "|", self.place[idx_place[i]]['place_id'] ,"|")
    #
    #     try:
    #         #hitung jarak dari tempat wisata terakhir kembali ke hotel
    #         place_id = self.place[idx_place[place_count-1]]['place_id']
    #         hotel_id = self.hotel[idx_hotel[0]]['place_id']
    #         print(self.distance[place_id][hotel_id])
    #     except KeyError:
    #         print(99999999)
    #############################################################################################################

    ################################################### v1 ######################################################
    #travel time saja fitnessnya
    #
    # def getDimension(self):
    #     return len(self.place)
    #
    # def randomPopulation(self):
    #     return np.random.uniform(self.getLowerBound(), self.getUpperBound(), self.getDimension()) # min,max,size
    #
    # def calculateFitness(self, individual):
    #     # ubah dulu ke index place
    #     idx = individual.argsort(kind='quicksort').argsort(kind='quicksort')
    #     place_count = len(self.place)
    #     travel_time_total = 0
    #     for i in range(place_count):
    #         if i < place_count - 1:
    #             temp = 0
    #             try:
    #                 temp = self.distance[self.place[idx[i]]['place_id']][self.place[idx[i+1]]['place_id']]
    #             except KeyError:
    #                 temp = 99999999
    #             travel_time_total += temp
    #     return 1 / travel_time_total
    #
    # def showResult(self, result):
    #     position = result.argsort(kind='quicksort').argsort(kind='quicksort')
    #     print(position)
    #
    #     place_count = len(self.place)
    #     for i in range(place_count):
    #         print((i+1), ". ", self.place[position[i]]['name'].encode("utf-8"), "|", self.place[position[i]]['place_id'])

    #############################################################################################################
