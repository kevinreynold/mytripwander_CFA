import json
from datetime import datetime, date, time, timedelta
from db import db
from trip import flight, break_stop, trip
from CFA import CCells, CFA
import numpy as np

# getPlaceOpeningHoursByDay ############
# a = trip()
# place = a.place[1]
# print(place['opening_hours'])
# today = datetime.today()
# print(today)
# open_hours = a.getPlaceOpeningHoursByDay(place,today)['open']
# close_hours = a.getPlaceOpeningHoursByDay(place,today)['close']
# now = today + timedelta(minutes=45)
# isOpen = a.isPlaceOpenRightNow(now,place,today)
# print(open_hours)
# print(now)
# print(close_hours)
# print(isOpen)

#test case
 # 1. datang malam sampai dihotel malaml lanjut besok
 # 2. datang malam sampai di hotel subuh2
 # 3. datang subuh lanjut paginya
 # 4. datang pagi
 # 5. datang pagi dr hotel langsung makan siang
 # 6. datang siang
 # 7. datang sore dr hotel langsung makan malam

 #last airport
 # 1. pulang pagi
 # 2. pulang siang
 # 3. pulang SORE
 # 4. pulang malam

start = datetime.today()
np.random.seed(0)
#10.15, 17.10, 12.40, 13.35
go_back_hour = "1240"
trip = trip(break_stop=break_stop(city="HKG", first_place="HKG", last_place="HKG",
            arrival_date=(datetime.today()+timedelta(days=1)), arrival_hour="1015",
            go_back_date=(datetime.today()+timedelta(days=3)), go_back_hour=go_back_hour),
            limit_night_next_day=time(18), budget="none", last_airport=False, start_hour="0830", end_hour="2130",
            must_see=1, recreation=2, culture=0, nature=-2) # last_airport = True/False
cfa = CFA(iteration=10, pop_size=50, R1=0.55, R2=-0.55, V1=1, V2=-1, problem=trip)
cfa.run()

end = datetime.today()
execution_time = int((end-start).total_seconds())
m, s = divmod(execution_time, 60)
h, m = divmod(m, 60)

print(trip.break_stop.city + " " + str(trip.total_days) + " HARI")
print("Execution Time :", '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s))
print("Best Fitness : " + str(1/cfa.best_cell.fitness) +
      " | Iteration : " + str(cfa.iteration) + " | Population : " + str(cfa.population_size) +
      " | R1 : " + str(cfa.R1) + " | R2 : " + str(cfa.R2) +
      " | V1 : " + str(cfa.V1) + " | V2 : " + str(cfa.V2) )
print("Must See : " + str(trip.must_see_interest) + " | Recreation : " + str(trip.recreation_interest) +
      " Culture : " + str(trip.culture_interest) + " | Nature : " + str(trip.nature_interest))

print(cfa.best_cell.other['route'])
# trip.showResult(cfa.best_cell.points, cfa.best_cell.other['stop_sign'], cfa.problem.start_date, cfa.best_cell.other['is_too_late'])
trip.showResultNew(cfa.best_cell.other['route'], cfa.problem.start_date)
# trip.showRoute(cfa.best_cell.points)
print(cfa.best_cell.other['misc'])
print(cfa.best_cell.other['is_too_late'])
print(cfa.best_cell.other['misc2'])
