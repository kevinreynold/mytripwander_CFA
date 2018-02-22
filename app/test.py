import json
from datetime import datetime, date, time, timedelta
from db import db
from trip import trip, flight
from CFA import CCells, CFA
import numpy as np

# getPlaceOpeningHoursByDay ############
# place = a.place[25]
# today = datetime.today()
# mode = "close"
# print(today)
# result = a.getPlaceOpeningHoursByDay(place,today,mode)
# print(result)
# print(today < result)

# points = np.random.uniform(trip.getLowerBound(), trip.getUpperBound(), trip.getDimension())
# print(points)
#
# result = 1/trip.calculateFitness(points)
# print(result)
#
# place = points.argsort().argsort()
# print(place)
#

np.random.seed(0)
trip = trip()
cfa = CFA(iteration=100, pop_size=50, R1=0.55, R2=-0.55, V1=1, V2=-1, problem=trip)
cfa.run()
trip.showResult(cfa.best_cell.points, cfa.best_cell.other['stop_sign'], cfa.problem.start_date, cfa.best_cell.other['is_too_late'])
