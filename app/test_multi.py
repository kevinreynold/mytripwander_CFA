from tripschedule import *

# np.random.seed(0)
while True:
    db_access = db()
    request_data = db_access.getTripScheduleRequestData()
    print(request_data)

    if request_data['header']:
        start = datetime.today()
        trip_schedules = trip_schedule(request_data=request_data, iteration=50000)

        # print(trip_schedules.user_id)
        # created_at = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # db_access.updateDoneAtTripSchedule(schedule_id=trip_schedules.schedule_id, done_at=created_at)
        # trip_schedules.try_send_notif()

        print("Making new trip itinerary for schedule id: " + str(trip_schedules.schedule_id))
        trip_schedules.run()

        end = datetime.today()
        execution_time = int((end-start).total_seconds())
        m, s = divmod(execution_time, 60)
        h, m = divmod(m, 60)
        print("Execution Time: ", '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s))

        f = open("autotrip_log.txt", "a")
        f.write("TripSchedule ID - " + str(trip_schedules.schedule_id) + " | "+ "Execution Time: " + '{0:02d}:{1:02d}:{2:02d}'.format(h, m, s) + "\n")
    else:
        # tunggu 5 menit
        print("Wait for 5 minutes...")
        tt.sleep(300)

    tt.sleep(10)
