from tripschedule import *

start = datetime.today()
# np.random.seed(0)

db_access = db()

trip_schedule = trip_schedule(request_data=db_access.getTripScheduleRequestData(), iteration=100)
print(trip_schedule.user_id)
trip_schedule.run()

end = datetime.today()
execution_time = int((end-start).total_seconds())
m, s = divmod(execution_time, 60)
h, m = divmod(m, 60)
print("Execution Time :", '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s))
