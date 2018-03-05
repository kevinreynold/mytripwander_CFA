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
    def __init__(self, start_hour="0830", end_hour="2130",
                flight=flight("SUB", "HKG", (datetime.today()-timedelta(days=1)), datetime.today(), "0950", "0950"),
                flight2=flight("HKG", "SUB", (datetime.today()+timedelta(days=3)), (datetime.today()+timedelta(days=4)), "1850", "0950"), limit_night_next_day=time(18), hotel_stay_dur=60, airport_stay_dur=60,
                must_see=2, recreation=0, culture=0, nature=-2): #hotel dan airport dalam menit
        self.db_access = db()
        self.airport = self.db_access.getAirportData()
        self.place = self.db_access.getPlaceData()
        self.food = self.db_access.getFoodData()
        self.hotel = self.db_access.getHotelData()
        self.distance = self.db_access.getDistanceData()

        self.start_hour = start_hour
        self.end_hour = end_hour
        self.flight = flight
        self.flight2 = flight2
        self.start_date = self.flight.arrival['datetime']
        self.end_date = self.flight2.departure['datetime']
        self.total_days = (self.end_date.date() - self.start_date.date()).days + 1
        # self.total_days = 2
        self.limit_night_next_day = limit_night_next_day #setelah datang dari airport
        self.hotel_stay_dur = hotel_stay_dur
        self.airport_stay_dur = airport_stay_dur

        self.penalty_opening_hours = 60 * 60 * 100 #(10 jam dalam detik)
        self.penalty_eat_late = 25  #dalam (detik)
        self.penalty_go_home_late = 7  #dalam (detik)
        self.lunch_time_lower = time(12,00)
        self.lunch_time_upper = time(14,00)
        self.dinner_time_lower = time(18,00)
        self.dinner_time_upper = time(20,00)

        # range : -2 ~ 2
        self.interest_multiplier = 5
        self.must_see_interest = must_see * self.interest_multiplier
        self.recreation_interest = recreation * self.interest_multiplier
        self.culture_interest = culture * self.interest_multiplier
        self.nature_interest = nature * self.interest_multiplier
        self.total_interest = 2 * 4 * self.interest_multiplier

    def getLowerBound(self):
        return 0

    def getUpperBound(self):
        return 1

    def getPlaceByID(self, place_id): #dictionary
        return [x for x in self.place if x['place_id'] == place_id]

    def isPlaceNatureType(self, input):
        if input['category_id'] != 4:
            types = input['interests'].split(';')
            check = [type for type in types if type == 'nature']
            return True if len(check) > 0 else False
        return False

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
            if self.isPlaceNatureType(place) == True:
                hours = 18
                minutes = 30
            else:
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

    ################################################### v5 ######################################################
    # hanya travel_time
    # airport awal
    # pilih hotel juga (awal dan akhir)

    # ada start - end activities hour
    # end activities nya itu hanya berlaku di tempat wisata saja.
    # UNTUK 1 HARI SAJA
    # sudah BISA CEK KALO DATENGNYA TERLALU SORE
    # cek jam buka-tutup juga
    # maksimalkan tempat wisata sampai jam habis

    # kalau sampai lebih dari limit jam atau kalau sampainya subuh2 maka lanjut besok
    # untuk setiap harinya kalau jam nya kelewat batas maksmium 30 menit selama itu efektif

    # ubah format showResult dulu (1->airport, 2->tempat, 3->food, 4->hotel)

    # JAM MALAM HARUS LEBIH DARI JAM 20.00

    # tambah food (asumsi makan 2 kali yaitu siang dan malam) -> paginya dianggap sudah breakfast
    # kondisi makan :
        # kalau masih berada ditempat wisata dan terdapat makanan(selama average_dur) -> maka sudah dianggap makan
        # kalau blm makan cek jam (kalau berada dijam makan) -> cari tempat makan
        # kalau diluar jam tempat makan -> cari tempat makan

    # JENIS PENALTY:
    # 1. SEMAKIN TELAT PULANG ADA PENALTY (SELISIH WAKTU * 20 DETIK)
    # 2. SEMAKIN TELAT MAKAN ADA PENALTY (SELISIH WAKTU * 500 DETIK)
    # 3. KALAU ADA TEMPAT WISATA YANG LAGI TUTUP TAPI DIKUNJUNGI (WAKTU + 10 JAM)

    # JENIS BENEFIT:
    # 1. SEMAKIN BANYAK TEMPAT WISATA FITNESS MAKIN BAGUS (WAKTU - 30 MENIT @PLACE)

    # ISSUE :
    # ATUR JADWAL SAMPAI SESUAI TIKET PULANG ?
    # JAM TUTUP NATURE DIUBAH JANGAN 24 JAM (KE GUNUNG ATAU KE PANTAI MALAM? ANEH)
    # TIMEZONE TIAP PINDAH kota
    # LEBIH DARI 1 HARI
    # BISA PINDAH KOTA
    # SESUAI INTEREST

    # BISA LEBIH DARI 1 HARI (SAMPAI END DATE)
    # KALAU BELUM MAKAN 2 KALI KASIH PENALTY BESAR
    # NORMALISASI DURATION JADI 0 - 1 (BERDASARKAN TRAVEL TIME DAN STAY DURATION SAJA)
    # UNTUK NORMALISASI PENALTY IKUT PERBANDINGAN TRAVEL TIME DAN STAY DURATION

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
            type = "airport"
        elif type_idx == "2":
            data = self.place[idx]
            type = "place"
        elif type_idx == "3":
            data = self.food[idx]
            type = "food"
        elif type_idx == "4":
            data = self.hotel[idx]
            type = "hotel"
        result['data'] = data
        result['type'] = type
        result['is_stop'] = is_stop

        return result

    def isPlaceHasFood(self, input):
        if input['category_id'] != 4:
            types = input['types'].split(';')
            check = [type for type in types if type == 'food' or type == 'amusement_park']
            return True if len(check) > 0 else False
        return False

    def getPlaceInterestValue(self, input):
        interests = input['interests'].split(';')
        result = 0
        for i in interests:
            if i == "must_see":
                result += self.must_see_interest
            if i == "culture":
                result += self.culture_interest
            if i == "nature":
                result += self.nature_interest
            if i == "recreation":
                result += self.recreation_interest
        return result

    def getDimension(self):
        return len(self.place) + len(self.hotel) + len(self.food)

    def randomPopulation(self):
        return np.random.uniform(self.getLowerBound(), self.getUpperBound(), self.getDimension())

    def calculateFitness(self, individual):
        # ubah dulu ke index place
        place_count = len(self.place)
        hotel_count = len(self.hotel)
        food_count = len(self.food)

        idx_place = individual[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_hotel = individual[place_count:(place_count+hotel_count):1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_food = individual[(place_count+hotel_count):].argsort(kind='quicksort').argsort(kind='quicksort')

        food_offset = 0
        already_lunch = False
        already_dinner = False
        just_eat = False
        eat_idx = 0

        #start / end date and hours
        day = 1
        stop_sign = 0
        start_time = self.start_date

        hours = int(self.end_hour[0:2])
        minutes = int(self.end_hour[2:])
        end_time = start_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)

        #treshold batas jam malam
        # lower_treshold = end_time - timedelta(minutes=30)
        lower_treshold = end_time
        upper_treshold = end_time + timedelta(minutes=30)

        current_time = self.start_date

        travel_time_total = 0
        list_time = [] # dalam detik
        list_time_idx = []
        list_penalty = [] # dalam detik
        list_penalty_idx = []
        list_interest = []

        result = {}
        result['fitness'] = -1
        result['time'] = ""
        result['stop_sign'] = stop_sign
        result['is_too_late'] = False
        result['route'] = []
        result['misc'] = ""
        result['misc2'] = []
        route = []

        # AIRPORT -> HOTEL
        try:
            # urus2 barang di airport sekitar 1 jam
            travel_time_total += self.airport_stay_dur * 60
            current_time += timedelta(seconds=(self.airport_stay_dur * 60))
            list_time.append(self.airport_stay_dur * 60)
            list_time_idx.append(current_time.time().__str__())
            route.append(self.addRoute("airport", 0, False))

            #hitung jarak dari airport ke hotel
            airport_id = self.airport[0]['place_id']
            hotel_id = self.hotel[idx_hotel[0]]['place_id']
            travel_duration = self.distance[airport_id][hotel_id]
            travel_time_total += travel_duration
            travel_time_total += self.hotel_stay_dur * 60 #checkin dkk
            current_time += timedelta(seconds=(travel_duration + (self.hotel_stay_dur * 60)))
            list_time.append(travel_duration)
            list_time_idx.append(current_time.time().__str__())
            list_time.append(self.hotel_stay_dur * 60)
            list_time_idx.append(current_time.time().__str__())

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
                day += 1
                start_time += timedelta(days=1)
                lower_treshold += timedelta(days=1)
                upper_treshold += timedelta(days=1)
            elif (current_time.time() < time(hours,minutes)): #kalau sampai dihari yang sama tapi subuh
                # antara sampai di hotel sudah ganti hari
                # atau sampai di negara itu subuh2
                current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if (current_time.date() - start_time.date()).days > 0: # jika sampai di hotel sudah ganti hari
                    day += 1
                    start_time += timedelta(days=1)
                    lower_treshold += timedelta(days=1)
                    upper_treshold += timedelta(days=1)
            travel_time_total = 0
            list_time.clear()
            route.append(self.addRoute("hotel", idx_hotel[0], True))
        else:
            route.append(self.addRoute("hotel", idx_hotel[0], False))

        #kalau sampai di hotelnya sore dianggap sudah makan siang
        dinner_lower = current_time.replace(hour=self.dinner_time_lower.hour, minute=self.dinner_time_lower.minute, second=0, microsecond=0)
        if current_time > dinner_lower:
            already_lunch = True

        #per perharinya
        # MULAI WHILE
        while day <= self.total_days:
            # HOTEL -> PLACE PERTAMA
            try:
                # CEK MAKAN
                # if (self.lunch_time_lower < current_time.time() < self.lunch_time_upper) or (self.dinner_time_lower < current_time.time() < self.dinner_time_upper): # makan dulu
                if current_time.time() > self.lunch_time_lower: # makan dulu
                    if current_time.time() > self.dinner_time_lower:
                        already_dinner = True

                    #hitung jarak dari hotel ke tempat makan
                    hotel_id = self.hotel[idx_hotel[0]]['place_id']
                    food_id = self.food[idx_food[food_offset]]['place_id']
                    travel_duration = self.distance[hotel_id][food_id]
                    travel_time_total += travel_duration
                    current_time += timedelta(seconds=(travel_duration))
                    list_time.append(travel_duration)
                    list_time_idx.append(current_time.time().__str__())

                    # #cek kalau makan siangnya telat
                    # if current_time.time() > self.lunch_time_upper and already_lunch == False:
                    #     lunch_upper = current_time.replace(hour=self.lunch_time_upper.hour, minute=self.lunch_time_upper.minute, second=0, microsecond=0)
                    #     if current_time > lunch_upper: #dinner
                    #         penalty = int((current_time - lunch_upper).total_seconds()) * (self.penalty_eat_late / 2)
                    #         travel_time_total += penalty
                    #         list_penalty.append(penalty)
                    #         list_penalty_idx.append(self.addRoute("food", idx_food[food_offset], False))
                    #         result['misc'] = '44'
                    # #cek kalau makan malamnya telat
                    # if current_time.time() > self.dinner_time_upper and already_dinner == False:
                    #     dinner_upper = current_time.replace(hour=self.dinner_time_upper.hour, minute=self.dinner_time_upper.minute, second=0, microsecond=0)
                    #     if current_time > dinner_upper: #dinner
                    #         penalty = int((current_time - dinner_upper).total_seconds()) * (self.penalty_eat_late / 2)
                    #         travel_time_total += penalty
                    #         list_penalty.append(penalty)
                    #         list_penalty_idx.append(self.addRoute("food", idx_food[food_offset], False))
                    #         result['misc'] = '22'

                    travel_time_total += (self.food[idx_food[food_offset]]['avg_dur'] * 60)
                    current_time += timedelta(seconds=((self.food[idx_food[food_offset]]['avg_dur'] * 60)))
                    list_time.append((self.food[idx_food[food_offset]]['avg_dur'] * 60))
                    list_time_idx.append(current_time.time().__str__())

                    # cek jam buka tempat makan
                    if self.isPlaceOpenRightNow(current_time, self.food[idx_food[food_offset]], start_time) == False:
                        travel_time_total += self.penalty_opening_hours
                        list_penalty.append(self.penalty_opening_hours)
                        list_penalty_idx.append(self.addRoute("food", idx_food[food_offset], False))
                        result['misc'] = '11'

                    route.append(self.addRoute("food", idx_food[food_offset], False))
                    eat_idx = food_offset
                    food_offset += 1
                    already_lunch = True

                    # kasih penalty kalau makannya lewat batas
                    # if current_time.time() > self.dinner_time_upper and already_dinner == False:
                    #     travel_time_total += 600 * self.penalty_eat_late
                    #     list_penalty.append(600 * self.penalty_eat_late)
                    #     list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                    #     result['misc'] = '22'
                    # elif current_time.time() > self.dinner_time_upper and already_dinner == True:
                    #     dinner_upper = current_time.replace(hour=self.dinner_time_upper.hour, minute=self.dinner_time_upper.minute, second=0, microsecond=0) + timedelta(minutes=30)
                    #     if current_time > dinner_upper: #dinner
                    #         penalty = int((current_time - dinner_upper).total_seconds()) * self.penalty_eat_late
                    #         travel_time_total += penalty
                    #         list_penalty.append(penalty)
                    #         list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                    #         result['misc'] = '33'
                    # elif current_time.time() > self.lunch_time_upper and already_lunch == True and already_dinner == False:
                    #     lunch_upper = current_time.replace(hour=self.lunch_time_upper.hour, minute=self.lunch_time_upper.minute, second=0, microsecond=0) + timedelta(minutes=30)
                    #     if current_time > lunch_upper: #dinner
                    #         penalty = int((current_time - lunch_upper).total_seconds()) * self.penalty_eat_late
                    #         travel_time_total += penalty
                    #         list_penalty.append(penalty)
                    #         list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                    #         result['misc'] = '44'

                    #hitung jarak dari tempat makan ke tempat wisata pertama
                    food_id = self.food[idx_food[eat_idx]]['place_id']
                    place_id = self.place[idx_place[0]]['place_id']
                    travel_duration = self.distance[food_id][place_id]
                    travel_time_total += travel_duration
                    current_time += timedelta(seconds=(travel_duration))
                    list_time.append(travel_duration)
                    list_time_idx.append(current_time.time().__str__())
                else:
                    #hitung jarak dari hotel ke tempat wisata pertama
                    hotel_id = self.hotel[idx_hotel[0]]['place_id']
                    place_id = self.place[idx_place[stop_sign]]['place_id']
                    travel_duration = self.distance[hotel_id][place_id]
                    travel_time_total += travel_duration
                    current_time += timedelta(seconds=(travel_duration))
                    list_time.append(travel_duration)
                    list_time_idx.append(current_time.time().__str__())
            except KeyError:
                result['fitness'] = -1
                return result

            #hitung per tempat wisatanya
            place_offset = stop_sign
            for i in range(place_offset, place_count):
                #cek makan ditempat wisata
                if self.isPlaceHasFood(self.place[idx_place[i]]) == True: # cek apakah ditempat saat ini ada makanan atau tidak
                    if (self.lunch_time_lower < current_time.time() < self.lunch_time_upper) or (self.dinner_time_lower < current_time.time() < self.dinner_time_upper):
                        if already_lunch == False or already_dinner == False: #makan dulu
                            already_dinner = True if already_lunch == True else False
                            already_lunch = True

                #tambah average_duration
                stay_duration = self.place[idx_place[i]]['avg_dur'] * 60
                travel_time_total += stay_duration
                current_time += timedelta(seconds=stay_duration)
                list_time.append(stay_duration)
                list_time_idx.append(current_time.time().__str__())
                list_interest.append(self.getPlaceInterestValue(self.place[idx_place[i]]))
                route.append(self.addRoute("place", idx_place[i], False))

                # cek jam buka tutup
                # kalau misalnya lagi tutup maka diberi penalty travel_time + 10 jam
                if self.isPlaceOpenRightNow(current_time, self.place[idx_place[i]], start_time) == False:
                    travel_time_total += self.penalty_opening_hours
                    list_penalty.append(self.penalty_opening_hours)
                    list_penalty_idx.append(self.addRoute("place", idx_place[i], False))
                    result['misc'] = '55'

                # CEK MAKAN
                # cek habis makan bisa langsung pulang atau tidak
                # cek habis makan kalau waktunya ke airport langsung ke hotel
                if current_time.time() > self.lunch_time_lower:
                    if already_lunch == False or already_dinner == False: #makan dulu
                        if (already_lunch == False and current_time.time() > self.lunch_time_lower) or (already_dinner == False and current_time.time() > self.dinner_time_lower):
                            try:
                                # kalau kelewat batas jam (toleransi 30 menit) -> distop (kasih tau stopnya dimana)
                                # hitung jarak dari place ke tempat makan
                                place_id = self.place[idx_place[i]]['place_id']
                                food_id = self.food[idx_food[food_offset]]['place_id']
                                travel_duration = self.distance[place_id][food_id]
                                next_dest_stay_duration = self.food[idx_food[food_offset]]['avg_dur'] * 60
                                predict_next_dest_time = current_time + timedelta(seconds=(travel_duration + next_dest_stay_duration))
                                if predict_next_dest_time >= upper_treshold:
                                    stop_sign = i
                                    if current_time < lower_treshold:
                                        penalty = int((lower_treshold - current_time).total_seconds()) * self.penalty_go_home_late
                                        travel_time_total += penalty
                                        list_penalty.append(penalty)
                                        list_penalty_idx.append(self.addRoute("place", idx_place[i], False))
                                        result['misc'] = '66'
                                    break
                            except KeyError:
                                result['fitness'] = -1
                                return result

                            travel_time_total += travel_duration
                            current_time += timedelta(seconds=(travel_duration))
                            list_time.append(travel_duration)
                            list_time_idx.append(current_time.time().__str__())

                            #cek kalau makan siangnya telat
                            if current_time.time() > self.lunch_time_upper and already_lunch == False:
                                lunch_upper = current_time.replace(hour=self.lunch_time_upper.hour, minute=self.lunch_time_upper.minute, second=0, microsecond=0)
                                if current_time > lunch_upper: #dinner
                                    penalty = int((current_time - lunch_upper).total_seconds()) * self.penalty_eat_late
                                    travel_time_total += penalty
                                    list_penalty.append(penalty)
                                    list_penalty_idx.append(self.addRoute("food", idx_food[food_offset], False))
                                    result['misc'] = '1010'
                            #cek kalau makan malamnya telat
                            if current_time.time() > self.dinner_time_upper and already_dinner == False:
                                dinner_upper = current_time.replace(hour=self.dinner_time_upper.hour, minute=self.dinner_time_upper.minute, second=0, microsecond=0)
                                if current_time > dinner_upper: #dinner
                                    penalty = int((current_time - dinner_upper).total_seconds()) * self.penalty_eat_late
                                    travel_time_total += penalty
                                    list_penalty.append(penalty)
                                    list_penalty_idx.append(self.addRoute("food", idx_food[food_offset], False))
                                    result['misc'] = '88'


                            travel_time_total += next_dest_stay_duration
                            current_time += timedelta(seconds=(next_dest_stay_duration))
                            list_time.append(next_dest_stay_duration)
                            list_time_idx.append(current_time.time().__str__())

                            # cek jam buka tempat makan
                            if self.isPlaceOpenRightNow(current_time, self.food[idx_food[food_offset]], start_time) == False:
                                travel_time_total += self.penalty_opening_hours
                                list_penalty.append(self.penalty_opening_hours)
                                list_penalty_idx.append(self.addRoute("food", idx_food[food_offset], False))
                                result['misc'] = '77'

                            route.append(self.addRoute("food", idx_food[food_offset], False))
                            just_eat = True
                            eat_idx = food_offset
                            food_offset += 1

                            if current_time.time() > self.dinner_time_lower and already_lunch == True:
                                already_dinner = True
                            else:
                                already_lunch = True

                            # kasih penalty kalau makannya lewat batas

                            # if current_time.time() > self.dinner_time_upper and already_dinner == False:
                            #     travel_time_total += 600 * self.penalty_eat_late
                            #     list_penalty.append(600 * self.penalty_eat_late)
                            #     list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                            #     result['misc'] = '88'
                            # elif current_time.time() > self.dinner_time_upper and already_dinner == True:
                            #     dinner_upper = current_time.replace(hour=self.dinner_time_upper.hour, minute=self.dinner_time_upper.minute, second=0, microsecond=0) + timedelta(minutes=30)
                            #     if current_time > dinner_upper: #dinner
                            #         penalty = int((current_time - dinner_upper).total_seconds()) * self.penalty_eat_late
                            #         travel_time_total += penalty
                            #         list_penalty.append(penalty)
                            #         list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                            #         result['misc'] = '99'
                            # elif current_time.time() > self.lunch_time_upper and already_lunch == True and already_dinner == False:
                            #     lunch_upper = current_time.replace(hour=self.lunch_time_upper.hour, minute=self.lunch_time_upper.minute, second=0, microsecond=0) + timedelta(minutes=30)
                            #     if current_time > lunch_upper: #dinner
                            #         penalty = int((current_time - lunch_upper).total_seconds()) * self.penalty_eat_late
                            #         travel_time_total += penalty
                            #         list_penalty.append(penalty)
                            #         list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                            #         result['misc'] = '1010'

                # cek kalau masih dalam batas end activities hour
                if i < place_count - 1: #hitung antar tempat wisata
                    # cek dulu kalau ketempat selanjutnya masih nutut ya capcus kalau ndak stop
                    try:
                        if just_eat == False:
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
                                    if current_time < lower_treshold:
                                        penalty = int((lower_treshold - current_time).total_seconds()) * self.penalty_go_home_late
                                        travel_time_total += penalty
                                        list_penalty.append(penalty)
                                        list_penalty_idx.append(self.addRoute("place", idx_place[i], False))
                                        result['misc'] = '1111'
                                    break
                            except KeyError:
                                result['fitness'] = -1
                                return result

                            # kalau masih bisa
                            travel_time_total += travel_duration
                            current_time += timedelta(seconds=(travel_duration))
                            list_time.append(travel_duration)
                            list_time_idx.append(current_time.time().__str__())
                        else: # kalau habis makan
                            try:
                                #cek habis makan langsung pulang atau tidak
                                food_id = self.food[idx_food[eat_idx]]['place_id']
                                place_id = self.place[idx_place[i+1]]['place_id']
                                travel_duration = self.distance[food_id][place_id]
                                next_dest_stay_duration = self.place[idx_place[i+1]]['avg_dur'] * 60
                                predict_next_dest_time = current_time + timedelta(seconds=(travel_duration + next_dest_stay_duration))
                                if predict_next_dest_time >= upper_treshold:
                                    stop_sign = i
                                    if current_time < lower_treshold:
                                        penalty = int((lower_treshold - current_time).total_seconds()) * self.penalty_go_home_late
                                        travel_time_total += penalty
                                        list_penalty.append(penalty)
                                        list_penalty_idx.append(self.addRoute("food", idx_food[eat_idx], False))
                                        result['misc'] = '1212'
                                    break
                            except KeyError:
                                result['fitness'] = -1
                                return result

                            # kalau lanjut
                            travel_time_total += travel_duration
                            current_time += timedelta(seconds=(travel_duration))
                            list_time.append(travel_duration)
                            list_time_idx.append(current_time.time().__str__())
                            just_eat = False
                    except KeyError:
                        result['fitness'] = -1
                        return result

            try:
                #hitung jarak dari tempat wisata terakhir kembali ke hotel
                if just_eat == False:
                    place_id = self.place[idx_place[stop_sign]]['place_id']
                    hotel_id = self.hotel[idx_hotel[0]]['place_id']
                    travel_duration = self.distance[place_id][hotel_id]
                    travel_time_total += travel_duration
                    current_time += timedelta(seconds=(travel_duration))
                    list_time.append(travel_duration)
                    list_time_idx.append(current_time.time().__str__())
                    route.append(self.addRoute("hotel", idx_hotel[0], True))
                else:
                    food_id = self.food[idx_food[eat_idx]]['place_id']
                    hotel_id = self.hotel[idx_hotel[0]]['place_id']
                    travel_duration = self.distance[food_id][hotel_id]
                    travel_time_total += travel_duration
                    current_time += timedelta(seconds=(travel_duration))
                    list_time.append(travel_duration)
                    list_time_idx.append(current_time.time().__str__())
                    route.append(self.addRoute("hotel", idx_hotel[0], True))
                    just_eat = False

            except KeyError:
                result['fitness'] = -1
                return result

            # RESET
            result['time'] = str(current_time.__str__())
            result['stop_sign'] = stop_sign

            day += 1
            stop_sign += 1
            start_time += timedelta(days=1)
            lower_treshold += timedelta(days=1)
            upper_treshold += timedelta(days=1)

            hours = int(self.start_hour[0:2])
            minutes = int(self.start_hour[2:])
            # current_time = start_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)

            if (current_time.time() > self.limit_night_next_day): #lebih dari limit jam
                current_time = current_time + timedelta(days=1)
                current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            elif (current_time.time() < time(hours,minutes)): #kalau sampai dihari yang sama tapi subuh
                current_time = current_time.replace(hour=hours, minute=minutes, second=0, microsecond=0)

            # kalau belum makan 2 kali kasih penalty
            if already_dinner == False:
                travel_time_total += 40000 * self.penalty_eat_late
                list_penalty.append(40000 * self.penalty_eat_late)
                list_penalty_idx.append(self.addRoute("food", 999, False))
                result['misc'] = '1313'

            already_lunch = False
            already_dinner = False
            just_eat = False

        # END WHILE
        # print("END")
        # print("")

        # print(stop_sign)
        # print(travel_time_total)
        # print(current_time)

        # semakin banyak tempat fitness akan dikurang
        # travel_time_total -= ((stop_sign) * 3600)

        # normalized_list_time = np.divide((np.subtract(list_time, np.amin(list_time))), (np.subtract(np.amax(list_time), np.amin(list_time))))
        # normalized_list_penalty = np.divide((np.subtract(list_penalty, np.amin(list_time))), (np.subtract(np.amax(list_time), np.amin(list_time))))
        # normalized_fitness = np.sum(np.concatenate((normalized_list_time, normalized_list_penalty), axis=0)) - ((stop_sign) * 0.3)

        real_stay_days = self.total_days - 1 if is_too_late == True else self.total_days
        place_target_per_day = 6

        # total travel duration + stay duration
        place_time_total = np.sum(list_time)

        # makin banyak tempat makin bagus
        place_discount = place_time_total * (1 / (place_target_per_day * real_stay_days) / 2) * stop_sign

        #total penalty
        penalty_total = np.sum(list_penalty)

        # interest
        interests_total = place_time_total * (0 - (((np.sum(list_interest) - (stop_sign * self.total_interest * -1)) / ((stop_sign * self.total_interest) - (stop_sign * self.total_interest * -1))) - 0.5))

        fitness_total = place_time_total + penalty_total - place_discount + interests_total

        result['misc'] = list_penalty_idx
        result['is_too_late'] = list_penalty
        result['misc2'] = list_time_idx

        # result['fitness'] = 1 / (normalized_fitness)
        # result['fitness'] = 1 / (travel_time_total + 0.00001)
        result['fitness'] = 1 / (fitness_total + 0.00001)

        result['route'] = route

        return result

    def printResult(self, offset, name, current_time, next_time, opening_hours, is_open, type, types, place_id):
        if opening_hours['open'] == -1:
            print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + '{:^18} '.format("Closed") + " | " + '{:5}'.format(str(is_open)) + " | " + type + " | " + place_id + " | " + types)
        else:
            print('{:3}. '.format(str(offset)) + name + " | " + current_time.__str__() + " - " + next_time.__str__() + " | " + opening_hours['open'].time().__str__() + " - " + opening_hours['close'].time().__str__() + " | " + '{:5}'.format(str(is_open)) + " | " + type + " | " + place_id + " | " + types)

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
            name = '{:47}'.format(data['data']['name'].encode("utf-8").__str__()[0:47:1])
            place_id = data['data']['place_id']
            is_stop = data['is_stop']
            type = '{:7}'.format(data['type'])
            types = data['data']['interests']
            if i == 0: # airport
                current_time = current_time
                next_time = current_time + timedelta(minutes=self.airport_stay_dur)

                opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                self.printResult(offset, name, current_time, next_time, opening_hours, is_open, type, types, place_id)
            elif i == 1: # hotel pertama kali
                airport_id = prev_data['data']['place_id']
                hotel_id = data['data']['place_id']

                current_time = next_time + timedelta(seconds=self.distance[airport_id][hotel_id])
                next_time = current_time + timedelta(minutes=self.hotel_stay_dur)

                opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                self.printResult(offset, name, current_time, next_time, opening_hours, is_open, type, types, place_id)

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

                    self.printResult(offset, name, current_time, next_time, opening_hours, is_open, type, types, place_id)
            else:
                before_place = prev_data['data']['place_id']
                current_place = data['data']['place_id']

                current_time = next_time + timedelta(seconds=self.distance[before_place][current_place])
                next_time = current_time + timedelta(minutes=data['data']['avg_dur'])

                opening_hours = self.getPlaceOpeningHoursByDay(data['data'], current_time)
                is_open = self.isPlaceOpenRightNow(next_time, data['data'], current_time)

                self.printResult(offset, name, current_time, next_time, opening_hours, is_open, type, types, place_id)

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

                    self.printResult(offset, name, current_time, next_time, opening_hours, is_open, type, types, place_id)

            prev_data = data
            offset += 1

    def showRoute(self, individual):
        place_count = len(self.place)
        hotel_count = len(self.hotel)
        food_count = len(self.food)

        idx_place = individual[0:place_count:1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_hotel = individual[place_count:(place_count+hotel_count):1].argsort(kind='quicksort').argsort(kind='quicksort')
        idx_food = individual[(place_count+hotel_count):].argsort(kind='quicksort').argsort(kind='quicksort')

        print(idx_place)
        print(idx_hotel)
        print(idx_food)

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
