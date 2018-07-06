import json
from datetime import datetime, date, time, timedelta
from db import db
from trip import break_stop, trip
from CFA import CCells, CFA
import numpy as np

#test case
 # 1. datang malam sampai dihotel malaml lanjut besok
 # 2. datang malam sampai di hotel subuh2
 # 3. datang subuh lanjut paginya
 # 4. datang pagi
 # 5. datang pagi dr hotel langsung makan siang
 # 6. datang siang
 # 7. datang sore dr hotel langsung makan malam

 #last airport
 # 8. pulang pagi
 # 8. pulang siang
 # 9. pulang SORE
 # 10. pulang malam

 # hari biasa
 # pindah kota

start = datetime.today()
np.random.seed(777)
#10.15, 17.10, 12.40, 13.35

# hotel tainan -> Tayih Landis Hotel Tainan ChIJgbQuvnt2bjQR3Opc2ZtWzwU

# datetime.today()+timedelta(days=1)

go_back_hour = "2115"
trip = trip(break_stop=break_stop(city="TPE", first_place="TPE", last_place="TPE",
            arrival_date=(datetime(2018,5,18,0,0)), arrival_hour="1015",
            go_back_date=(datetime(2018,5,20,0,0)), go_back_hour=go_back_hour),
            limit_night_next_day=time(18), budget="low", last_airport=True, start_hour="0800", end_hour="2130",
            must_see=0, recreation=0, culture=0, nature=0) # last_airport = True/False
cfa = CFA(iteration=10000, pop_size=300, R1=0.25, R2=-0.55, V1=0.5, V2=-1.1, problem=trip)
cfa.run()

end = datetime.today()
execution_time = int((end-start).total_seconds())
m, s = divmod(execution_time, 60)
h, m = divmod(m, 60)

print('')
print(trip.break_stop.city + " " + str(trip.total_days) + " HARI")
print("Execution Time :", '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s))
print("Best Fitness : " + str(1/cfa.best_cell.fitness) +
      " | Iteration : " + str(cfa.iteration) + " | Population : " + str(cfa.population_size) +
      " | R1 : " + str(cfa.R1) + " | R2 : " + str(cfa.R2) +
      " | V1 : " + str(cfa.V1) + " | V2 : " + str(cfa.V2))
print("Must See : " + str(trip.must_see_interest) + " | Recreation : " + str(trip.recreation_interest) +
      " Culture : " + str(trip.culture_interest) + " | Nature : " + str(trip.nature_interest))

print('Route:')
print(cfa.best_cell.other['route'])
# trip.showResult(cfa.best_cell.points, cfa.best_cell.other['stop_sign'], cfa.problem.start_date, cfa.best_cell.other['is_too_late'])

print('')
trip.showResultNew(cfa.best_cell.other['route'], cfa.problem.start_date)
# trip.showRoute(cfa.best_cell.points)
print('')
print('List Penalty Index:')
print(cfa.best_cell.other['misc'])

print('')
print('List Penalty:')
print(cfa.best_cell.other['is_too_late'])

print('')
print('Total Place:')
print(cfa.best_cell.other['stop_sign'])

print('')
print('Place Discount Percent:')
print(cfa.best_cell.other['other']['place_discount_percent'])

print('')
print('Total Interest')
print(trip.total_interest)

print('')
print('Interest Discount Percent:')
print(cfa.best_cell.other['other']['interest_discount_percent'])


# print(cfa.best_cell.other['misc2'])
# print(cfa.best_cell.other['last_place_id'])
