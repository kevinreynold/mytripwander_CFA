import pymysql

class db():
    def __init__(self, db_host = "127.0.0.1", db_user = "root", db_password = "", db_name = "trip_wander", city="HKG"):
        charSet = "utf8"
        cusrorType = pymysql.cursors.DictCursor
        self.conn = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, charset=charSet, cursorclass=cusrorType)
        self.city = city

    def getPlaceData(self): # list of dictionaries -> sementara negara hongkong saja
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 2 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Place Data Success!!")

    def getAirportData(self): # list of dictionaries -> sementara negara hongkong saja
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 1 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Airport Data Success!!")

    def getFoodData(self): # list of dictionaries -> sementara negara hongkong saja
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 3 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Food Data Success!!")

            #SELECT * from place WHERE category_id = 4 AND city_code = 'HKG' AND SUBSTRING(description, 1, 2)
    def getHotelData(self, budget): # list of dictionaries -> sementara negara hongkong saja
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

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Hotel Data Success!!")

    def getDataById(self, input):
        if len(input) > 0:
            try:
                with self.conn.cursor() as cursor:
                    if len(input) == 3:
                        sql = "SELECT * FROM place WHERE category_id = 1 AND SUBSTRING(name,-4,3) = %s"
                    else:
                        sql = "SELECT * FROM place WHERE place_id = %s"
                    cursor.execute(sql, input)
                    result = cursor.fetchone()
                    return result

                    # for idx, data in enumerate(result):
                    #     print(idx, ":", data["place_id"].encode("utf-8"))
            finally:
                # self.conn.close()
                print("Load Specific Data Success!!")

    def getDistanceData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                # sql =   "SELECT d.* FROM distance d, place p where d.origin = p.place_id and p.city_code = %s"
                # cursor.execute(sql, (self.city))
                sql =   "SELECT * from distance"
                cursor.execute(sql)
                # result = cursor.fetchall()
                # return result

                result = {}
                rows = cursor.fetchall()
                for row in rows:
                    origin = row['origin']
                    destination = row['destination']
                    travel_time = row['travel_time']
                    result[origin] = result.get(origin, {})
                    result[origin][destination] = travel_time
                return result


                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Distance Data Success!!")
