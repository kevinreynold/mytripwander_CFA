import json
from datetime import datetime, date, time, timedelta
from db import db
from trip import trip, flight
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

start = datetime.today()
np.random.seed(0)
trip = trip(flight=flight("SUB", "HKG", (datetime.today()-timedelta(days=1)), (datetime.today()+timedelta(days=1)), "0950", "0950"),
            flight2=flight("HKG", "SUB", (datetime.today()+timedelta(days=4)), (datetime.today()+timedelta(days=3)), "1850", "0950"),
            limit_night_next_day=time(18))
cfa = CFA(iteration=100000, pop_size=25, R1=0.55, R2=-0.55, V1=1, V2=-1, problem=trip)
cfa.run()

end = datetime.today()
execution_time = (end-start).total_seconds()
print("")
print("Execution Time :", execution_time, "seconds")
print("Best Fitness : " + trip.convertFitnessValue(cfa.best_cell.fitness) +
      " | Iteration : " + str(cfa.iteration) + " | Population : " + str(cfa.population_size) +
      " | R1 : " + str(cfa.R1) + " | R2 : " + str(cfa.R2) +
      " | V1 : " + str(cfa.V1) + " | V2 : " + str(cfa.V2) )

print(cfa.best_cell.other['route'])
# trip.showResult(cfa.best_cell.points, cfa.best_cell.other['stop_sign'], cfa.problem.start_date, cfa.best_cell.other['is_too_late'])
trip.showResultNew(cfa.best_cell.other['route'], cfa.problem.start_date)
# trip.showRoute(cfa.best_cell.points)
print(cfa.best_cell.other['misc'])
