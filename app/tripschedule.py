import numpy as np
import random
import json
from db import db
from datetime import datetime, date, time, timedelta
from trip import break_stop, trip
from CFA import CCells, CFA

class city_tour():
    def __init__(self, country_code='TW', starting_city='KHH', stay_duration=8):
        self.db_access = db()
        self.distance = self.db_access.getDistanceData()

        self.country_code = country_code
        self.starting_city = starting_city
        self.stay_duration = stay_duration

        self.list_city = self.getListCity()
        self.list_first_place = self.getAllFirstPlace()
        self.starting_city_place_id = self.db_access.getFirstPlaceByCity(self.starting_city)['place_id']
        print(self.list_city)
        print(self.starting_city_place_id)
        print(self.list_first_place)


    def getLowerBound(self):
        return 0

    def getUpperBound(self):
        return 1

    def getDimension(self):
        return len(self.list_city)

    def randomPopulation(self):
        return np.random.uniform(self.getLowerBound(), self.getUpperBound(), self.getDimension())

    def getListCity(self):
        list_dict_city = self.db_access.getAllCityByCountry(self.country_code)
        result = []
        for i in range(len(list_dict_city)):
            city = list_dict_city[i]
            if city['city_code'] != self.starting_city:
                result.append(city['city_code'])
        return result

    def getAllFirstPlace(self):
        result = []
        for i in range(len(self.list_city)):
            result.append(self.db_access.getFirstPlaceByCity(self.list_city[i])['place_id'])
        return result

    def calculateFitness(self, individual):
        city_count = self.getDimension()
        idx_city = individual.argsort(kind='quicksort').argsort(kind='quicksort')

        travel_time_total = 0
        route = []
        misc = []

        result = {}
        result['fitness'] = -1
        result['route'] = []
        result['time'] = ""
        result['stop_sign'] = ""
        result['is_too_late'] = ""
        result['misc'] = ""
        result['misc2'] = ""
        result['last_place_id'] = ""

        try:
            first_place_id = self.starting_city_place_id
            next_id = self.list_first_place[idx_city[0]]
            travel_duration = self.distance[first_place_id][next_id]
            travel_time_total += travel_duration
            route.append(self.starting_city)
            route.append(self.list_city[idx_city[0]])

            day_left = self.stay_duration - 3
            misc.append(3)
        except KeyError:
            result['fitness'] = -1
            return result

        i = 0
        while True:
            if day_left == 3:
                day_left -= 3
                misc.append(3)
            else:
                day_left -= 2
                misc.append(2)

            if day_left == 0:
                break

            if i < len(self.list_city) - 1:
                try:
                    origin_id = self.list_first_place[idx_city[i]]
                    destination_id = self.list_first_place[idx_city[i+1]]
                    travel_duration = self.distance[origin_id][destination_id]
                    travel_time_total += travel_duration
                    route.append(self.list_city[idx_city[i+1]])
                except KeyError:
                    result['fitness'] = -1
                    return result

            i+=1

        result['fitness'] = 1 / (travel_time_total + 0.00001)
        result['route'] = route
        result['misc'] = misc
        return result

class trip_schedule():
    def __init__(self, request_data):
        self.db_access = db()

        # HEADER #
        self.header = request_data['header']
        self.city_origin = self.header['city_origin']
        # self.start_date = self.header['start_date'].strftime("%Y-%m-%d")
        self.start_date = datetime.combine(self.header['start_date'], datetime.min.time())

        self.start_hour = self.header['start_hour']
        self.end_hour = self.header['end_hour']
        self.budget = self.header['budget']

        # adult maks 4
        # children + infant maks 3
        self.adult = self.header['adult']
        self.children = self.header['child']
        self.infant = self.header['infant']

        self.must_see = self.header['must_see']
        self.recreation = self.header['recreation']
        self.culture = self.header['culture']
        self.nature = self.header['nature']

        # detail
        self.detail = request_data['detail']

        # manual
        self.arrival_hour = "1015"
        self.go_back_hour = "2200"

        #cfa
        self.iteration = 5000
        self.pop_size = 200
        self.R1 = 0.55
        self.R2 = -0.55
        self.V1 = 1
        self.V2 = -1

    def getAirport(self, city):
        if city == "SEL":
            return 'ICN'
        return city

    def changeDateTime(self, datetime, time):
        hours = int(time[0:2])
        minutes = int(time[2:])
        new_datetime = datetime.replace(hour=hours, minute=minutes, second=0, microsecond=0)

    def getListCityTour(self, country_code, starting_city, stay_duration):
        list_city = self.db_access.getAllCityByCountry(country_code)

        list_city_tour = []
        list_stay_duration = []
        list_city_tour.append(starting_city)
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
                airport = self.getAirport(city)

                arrival_date = current_date + timedelta(days=1)
                go_back_date = arrival_date + timedelta(days=stay_duration - 1)

                vbreak_stop = break_stop(city=city, first_place=airport, last_place=airport,
                                        arrival_date=arrival_date, arrival_hour=self.arrival_hour,
                                        go_back_date=go_back_date, go_back_hour=self.go_back_hour)

                vtrip = trip(break_stop=vbreak_stop, last_airport=True, budget=self.budget,
                            start_hour=self.start_hour, end_hour=self.end_hour,
                            must_see=self.must_see, recreation=self.recreation, culture=self.culture, nature=self.nature)

                vcfa = CFA(iteration=self.iteration, pop_size=self.pop_size, R1=self.R1, R2=self.R2, V1=self.V1, V2=self.V2, problem=vtrip)
                vcfa.run()

                vtrip.showResultNew(vcfa.best_cell.other['route'], vcfa.problem.start_date, offset_day)
                print(vcfa.best_cell.other['misc'])
                print(vcfa.best_cell.other['is_too_late'])
                print(vcfa.best_cell.other['misc2'])
                print(vcfa.best_cell.other['last_place_id'])

                offset_day += stay_duration

                current_date = go_back_date + timedelta(days=1)
                offset_day += 1
            else:
                list_tour = self.getListCityTour(country, city, stay_duration)
                print(list_tour)
                for j in range(len(list_tour['list_city'])):
                    city = list_tour['list_city'][j]
                    stay_duration = list_tour['list_stay_duration'][j]

                    airport = self.getAirport(city)

                    arrival_date = current_date + timedelta(days=1)
                    go_back_date = arrival_date + timedelta(days=stay_duration - 1)

                    if j == 0:
                        print("11111111")
                        first_place = airport
                        last_place = airport
                        new_arrival_hour = self.arrival_hour
                        new_go_back_hour = self.end_hour
                        new_last_airport = False
                    elif j < len(list_tour['list_city']) - 1:
                        print("22222222")
                        first_place = last_place_id
                        last_place = airport
                        new_arrival_hour = self.start_hour
                        new_go_back_hour = self.end_hour
                        new_last_airport = False
                    else:
                        print("33333333")
                        first_place = last_place_id
                        last_place = airport

                        if self.db_access.getDataById(last_place) == None:
                            print("LAST AIRPORT")

                        new_arrival_hour = self.start_hour
                        new_go_back_hour = self.go_back_hour
                        new_last_airport = True

                    vbreak_stop = break_stop(city=city, first_place=first_place, last_place=last_place,
                                            arrival_date=arrival_date, arrival_hour=new_arrival_hour,
                                            go_back_date=go_back_date, go_back_hour=new_go_back_hour)

                    vtrip = trip(break_stop=vbreak_stop, last_airport=new_last_airport, budget=self.budget,
                                start_hour=self.start_hour, end_hour=self.end_hour,
                                must_see=self.must_see, recreation=self.recreation, culture=self.culture, nature=self.nature)

                    vcfa = CFA(iteration=self.iteration, pop_size=self.pop_size, R1=self.R1, R2=self.R2, V1=self.V1, V2=self.V2, problem=vtrip)
                    vcfa.run()

                    vtrip.showResultNew(vcfa.best_cell.other['route'], vcfa.problem.start_date, offset_day)
                    print(vcfa.best_cell.other['misc'])
                    print(vcfa.best_cell.other['is_too_late'])
                    print(vcfa.best_cell.other['misc2'])
                    print(vcfa.best_cell.other['last_place_id'])
                    last_place_id = vcfa.best_cell.other['last_place_id']

                    offset_day += stay_duration

                    current_date = go_back_date

# vcity_tour = city_tour('TW','TPE',11)
# vcfa = CFA(iteration=1000, pop_size=15, R1=1, R2=-1, V1=2, V2=-2, problem=vcity_tour)
# vcfa.run()
# print(vcfa.best_cell.other['route'])
# print(vcfa.best_cell.other['misc'])

start = datetime.today()
np.random.seed(0)

db_access = db()
trip_schedule = trip_schedule(db_access.getTripScheduleRequestData())
trip_schedule.run()

end = datetime.today()
execution_time = int((end-start).total_seconds())
m, s = divmod(execution_time, 60)
h, m = divmod(m, 60)
print("Execution Time :", '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s))
