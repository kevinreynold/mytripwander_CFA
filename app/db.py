import pymysql

class db():
    def __init__(self, db_host = "127.0.0.1", db_user = "root", db_password = "", db_name = "trip_wander", city="HKG"):
        charSet = "utf8"
        cusrorType = pymysql.cursors.DictCursor
        self.conn = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, charset=charSet, cursorclass=cusrorType)
        self.city = city

    def getPlaceData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 2 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result
        finally:
            print("Load Place Data Success!!")

    def getFirstPlaceByCity(self, city_code): # dict
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 4 AND city_code = %s"
                cursor.execute(sql, (city_code))
                result = cursor.fetchone()
                return result
        finally:
            print("")

    def getAirportData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 1 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result
        finally:
            print("Load Airport Data Success!!")

    def getFoodData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 3 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result
        finally:
            print("Load Food Data Success!!")

    def getHotelData(self, budget): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                if budget == "low":
                    sql = "SELECT * from place WHERE category_id = 4 AND city_code = %s AND CAST(SUBSTRING(description, 1, 1) AS UNSIGNED) < 5"
                elif budget == "high":
                    sql = "SELECT * from place WHERE category_id = 4 AND city_code = %s AND CAST(SUBSTRING(description, 1, 1) AS UNSIGNED) = 5"
                else:
                    sql = "SELECT * from place WHERE category_id = 4 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result
        finally:
            print("Load Hotel Data Success!!")

    def getAllHotel(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 4"
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        finally:
            print("Load Hotel Data Success!!")

    def getDataById(self, input):
        if len(input) > 0:
            with self.conn.cursor() as cursor:
                if len(input) == 3:
                    sql = "SELECT * FROM place WHERE category_id = 1 AND SUBSTRING(name,-4,3) = %s"
                else:
                    sql = "SELECT * FROM place WHERE place_id = %s"
                cursor.execute(sql, input)
                result = cursor.fetchone()
                return result

    def getHotelDataByHotelId(self, hotel_id):
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM place WHERE misc = %s"
            cursor.execute(sql, str(hotel_id))
            result = cursor.fetchone()
            return result

    def getDistanceData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                # sql =   "SELECT d.* FROM distance d, place p where d.origin = p.place_id and p.city_code = %s"
                # cursor.execute(sql, (self.city))
                sql =   "SELECT * from distance"
                cursor.execute(sql)

                result = {}
                rows = cursor.fetchall()
                for row in rows:
                    origin = row['origin']
                    destination = row['destination']
                    travel_time = row['travel_time']
                    result[origin] = result.get(origin, {})
                    result[origin][destination] = travel_time
                return result
        finally:
            print("Load Distance Data Success!!")

    def getAllCountry(self):
        try:
            with self.conn.cursor() as cursor:
                sql =   "SELECT * FROM country"
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        finally:
            print("")

    def getAllCityByCountry(self, country_code):
        try:
            with self.conn.cursor() as cursor:
                sql =   "SELECT * FROM city WHERE country_code = %s"
                cursor.execute(sql, country_code)
                result = cursor.fetchall()
                return result
        finally:
            print("")

    def getCityDetail(self, city_code):
        try:
            with self.conn.cursor() as cursor:
                sql =   "SELECT * FROM city WHERE city_code = %s"
                cursor.execute(sql, city_code)
                result = cursor.fetchone()
                return result
        finally:
            print("")

    def getNearestCityById(self, place_id, block_list=[]):
        try:
            # SELECT pd.city_code
            # FROM distance d, place po, place pd
            # WHERE po.place_id = 'ChIJzZl9PXLraDURpgeBSXYqYSQ'
            # AND pd.city_code NOT IN (po.city_code)
            # AND d.origin = 'ChIJzZl9PXLraDURpgeBSXYqYSQ'
            # AND d.destination = pd.place_id
            # AND d.travel_time = (
            #     SELECT MIN(d.travel_time)
            #     FROM distance d, place po, place pd
            #     WHERE po.place_id = 'ChIJzZl9PXLraDURpgeBSXYqYSQ'
            #     AND pd.city_code NOT IN (po.city_code)
            #     AND d.origin = 'ChIJzZl9PXLraDURpgeBSXYqYSQ'
            #     AND d.destination = pd.place_id)
            with self.conn.cursor() as cursor:
                # sql = "SELECT city_code FROM place WHERE place_id = %s"
                # cursor.execute(sql, place_id)
                # city_code = cursor.fetchone()['city_code']
                # block_list.append(city_code)
                # print(block_list)

                sql = "SELECT MIN(d.travel_time) AS 'travel_time', pd.city_code AS 'city_code' FROM distance d, place po, place pd WHERE po.place_id = d.origin AND d.origin = %s AND pd.city_code NOT IN %s AND d.destination = pd.place_id AND pd.category_id = 4"
                cursor.execute(sql, (place_id, block_list))
                travel_time = cursor.fetchone()['travel_time']

                sql =   "SELECT pd.city_code FROM distance d, place po, place pd WHERE po.place_id = d.origin AND d.origin = %s AND pd.city_code NOT IN %s AND d.destination = pd.place_id AND d.travel_time = %s AND pd.category_id = 4"
                cursor.execute(sql, (place_id, block_list, travel_time))
                result = cursor.fetchone()
                return result['city_code']
        finally:
            print("")

    def getNearestAirportById(self, place_id):
        try:
            # SELECT SUBSTRING(pd.name,-4,3) AS 'airport' FROM distance d, place pd WHERE d.origin = %s AND d.destination = pd.place_id AND pd.category_id = 1 and d.travel_time = (SELECT MIN(d.travel_time) AS 'travel_time' FROM distance d, place pd WHERE d.origin = %s AND d.destination = pd.place_id AND pd.category_id = 1)
            with self.conn.cursor() as cursor:
                sql = "SELECT MIN(d.travel_time) AS 'travel_time' FROM distance d, place pd WHERE d.origin = %s AND d.destination = pd.place_id AND pd.category_id = 1"
                cursor.execute(sql, (place_id))
                travel_time = cursor.fetchone()['travel_time']

                sql = "SELECT SUBSTRING(pd.name,-4,3) AS 'airport' FROM distance d, place pd WHERE d.origin = %s AND d.destination = pd.place_id AND pd.category_id = 1 and d.travel_time = %s"
                cursor.execute(sql, (place_id, travel_time))
                result = cursor.fetchone()
                return result['airport']
        finally:
            print("")

    def getAirportByCity(self, city_code):
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * FROM city WHERE city_code = %s"
                cursor.execute(sql, city_code)
                result = cursor.fetchone()['airport']
                return result
        finally:
            print("")

    def setHotelId(self, place_id, hotel_id):
        try:
            with self.conn.cursor() as cursor:
                sql =   "UPDATE place set misc = %s WHERE place_id = %s"
                cursor.execute(sql, (hotel_id, place_id))
                self.conn.commit()
        finally:
            print("Success!!")

    ########################################## OLD ###############################################
    # def stillHasTripScheduleRequest(self):
    #     try:
    #         with self.conn.cursor() as cursor:
    #             sql =   "SELECT * FROM hr_tripschedule WHERE is_done = 0 ORDER BY created_at"
    #             cursor.execute(sql)
    #             result = cursor.fetchall()
    #             return True if len(result) > 0 else False
    #     finally:
    #         print("")
    #
    # def getTripScheduleRequestData(self):
    #     try:
    #         with self.conn.cursor() as cursor:
    #             result = {}
    #
    #             sql =   "SELECT * FROM hr_tripschedule WHERE is_done = 0 ORDER BY created_at"
    #             cursor.execute(sql)
    #             result['header'] = cursor.fetchone()
    #
    #             sql =   "SELECT * FROM dr_tripschedule WHERE schedule_id = %s ORDER BY offset"
    #             cursor.execute(sql, result['header']['schedule_id'])
    #             result['detail'] = cursor.fetchall()
    #
    #             return result
    #     finally:
    #         print("Load Trip Schedule Request Data Success!!")

    def stillHasTripScheduleRequest(self):
        try:
            with self.conn.cursor() as cursor:
                sql =  "SELECT * FROM tripschedule WHERE is_done = 0 ORDER BY created_at"
                cursor.execute(sql)
                result = cursor.fetchall()
                return True if len(result) > 0 else False
        finally:
            print("")

    def getTripScheduleRequestData(self):
        try:
            with self.conn.cursor() as cursor:
                result = {}

                sql = "SELECT * FROM tripschedule WHERE done_at IS NULL ORDER BY created_at"
                cursor.execute(sql)
                result['header'] = cursor.fetchone()

                return result
        finally:
            print("Load Trip Schedule Request Data Success!!")

    def setNewTrip(self, user_id, plan_data, city_plan_data, flight_plan, description, created_at):
        try:
            with self.conn.cursor() as cursor:
                sql = "INSERT INTO trip VALUES (NULL, %s, %s, %s, %s, 0, %s, %s)"
                cursor.execute(sql, (user_id, plan_data, city_plan_data, flight_plan, description, created_at))
                self.conn.commit()
        finally:
            print("Success save new trip!!")

    def updateDoneAtTripSchedule(self, schedule_id, done_at):
        try:
            with self.conn.cursor() as cursor:
                sql = "UPDATE tripschedule SET done_at = %s WHERE schedule_id = %s"
                cursor.execute(sql, (done_at, schedule_id))
                self.conn.commit()
        finally:
            print("Success update tripschedule!!")

    def getUserData(self, user_id):
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM user where id = %s"
            cursor.execute(sql, (user_id))
            result = cursor.fetchone()
            return result

    def getAllCurrency(self):
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM currency"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def setNewCurency(self, id, rate):
        try:
            with self.conn.cursor() as cursor:
                sql = "UPDATE currency set rate = %s WHERE id = %s"
                cursor.execute(sql, (rate, id))
                self.conn.commit()
        finally:
            print("Success!!")
