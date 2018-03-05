import pymysql

class db():
    def __init__(self, db_host = "127.0.0.1", db_user = "root", db_password = "", db_name = "trip_wander"):
        charSet = "utf8"
        cusrorType = pymysql.cursors.DictCursor
        self.conn = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, charset=charSet, cursorclass=cusrorType)
        self.city = 'TPE'
        # test = json.loads('{"day":["0000-2400","0000-2400","0000-2400","0000-2400","0000-2400","0000-2400","0000-2400"]}')
        #
        # origin = "ChIJDfcSIsGSaDUR7DKMmkKpoxU"
        # destination = "ChIJ6dYWDMKjfDURO6faY0bxLsI"
        # ChIJDfcSIsGSaDUR7DKMmkKpoxU	ChIJ6dYWDMKjfDURO6faY0bxLsI	343623	24821	NONE	-1
        # self.new_distance = self.getDistanceByRoute(origin, destination)

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

    def getHotelData(self): # list of dictionaries -> sementara negara hongkong saja
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place WHERE category_id = 4 AND city_code = %s"
                cursor.execute(sql, (self.city))
                result = cursor.fetchall()
                return result

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Hotel Data Success!!")

    def getDistanceData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                sql =   "SELECT d.* FROM distance d, place p where d.origin = p.place_id and p.city_code = %s"
                cursor.execute(sql, (self.city))
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
