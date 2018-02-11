import pymysql
import json

class db():
    def __init__(self, db_host = "127.0.0.1", db_user = "root", db_password = "", db_name = "trip_wander"):
        charSet = "utf8"
        cusrorType = pymysql.cursors.DictCursor
        self.conn = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, charset=charSet, cursorclass=cusrorType)
        self.place = self.getPlaceData()
        self.distance = self.getDistanceData()

        # test = json.loads('{"day":["0000-2400","0000-2400","0000-2400","0000-2400","0000-2400","0000-2400","0000-2400"]}')

        # origin = "ChIJDfcSIsGSaDUR7DKMmkKpoxU"
        # destination = "ChIJ6dYWDMKjfDURO6faY0bxLsI"
        # # ChIJDfcSIsGSaDUR7DKMmkKpoxU	ChIJ6dYWDMKjfDURO6faY0bxLsI	343623	24821	NONE	-1
        # self.new_distance = self.getDistanceByRoute(origin, destination)

    def getPlaceData(self): # list of dictionaries -> sementara negara hongkong saja
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from place where city_code = 'HKG'"
                cursor.execute(sql)
                result = cursor.fetchall()
                return result

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Place Data Success!!")

    def getPlaceByID(self, place_id): #dictionary
        return [x for x in self.place if x['place_id'] == place_id]

    def getDistanceData(self): # list of dictionaries
        try:
            with self.conn.cursor() as cursor:
                sql = "SELECT * from distance"
                cursor.execute(sql)
                result = cursor.fetchall()
                return result

                # for idx, data in enumerate(result):
                #     print(idx, ":", data["place_id"].encode("utf-8"))
        finally:
            # self.conn.close()
            print("Load Distance Data Success!!")

    def getDistanceByRoute(self, origin, destination): #dictionary
        return [x for x in self.distance if x['origin'] == origin and x['destination'] == destination]
