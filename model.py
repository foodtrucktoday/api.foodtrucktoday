#  Copyright (c) 2021 Romain ODET for Foodtruck Today

import pymysql
import os

import dotenv

dotenv.load_dotenv()  # for python-dotenv method


class Model:
    # Constructor, connect to database
    def __init__(self):
        host = os.environ.get('bdd_host')
        port = int(os.environ.get('bdd_port'))
        user = os.environ.get('bdd_user')
        password = os.environ.get('bdd_password')
        db = os.environ.get('bdd_name')

        self.con = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.
                                   DictCursor)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    # Destructor, disconnect from database
    def __exit__(self, type, value, traceback):
        if self.con:
            self.con.close()

    def GetFoodtruckDay(self, id):
        return self.sqlQuery("""
            select foodtruck.id as f_id, foodtruck.name as f_name, category.name as c_name, foodtruck.phone as f_phone,
                   foodtruck.email as f_email, foodtruck.website as f_website, foodtruck.facebook as f_facebook,
                   places.name as pl_name, planning.active as active,  places.latitude as pl_latitude,
                   places.longitude as pl_longitude, places.address as pl_address, category.id as category_id
            
            from foodtruck
                     left join category on foodtruck.category_id = category.id
                     left join planning on foodtruck.id = planning.foodtruck_id
                     inner join places on places.id = planning.places_id
            
            where planning.day_id = '%s'
            order by places.id
        """ % id)

    def GetAllFoodtruck(self):
        return self.sqlQuery("""
            select foodtruck.id as f_id, foodtruck.name as f_name, category.name as c_name, foodtruck.phone as f_phone,
                   foodtruck.email as f_email, foodtruck.website as f_website, foodtruck.facebook as f_facebook,
                   places.name as pl_name, planning.active as active,  places.latitude as pl_latitude,
                   places.longitude as pl_longitude, places.address as pl_address, category.id as category_id
            
            from foodtruck
                     left join category on foodtruck.category_id = category.id
                     left join planning on foodtruck.id = planning.foodtruck_id
                     inner join places on places.id = planning.places_id
            
            order by places.id
""")

    def GetFoodtruckByPlaceByDay(self, placeid, dayid):
        return self.sqlQuery(
            """
                select foodtruck.id as f_id, foodtruck.name as f_name, category.name as c_name, foodtruck.phone as f_phone,
                       foodtruck.email as f_email, foodtruck.website as f_website, foodtruck.facebook as f_facebook,
                       places.name as pl_name, planning.active as active,  places.latitude as pl_latitude,
                       places.longitude as pl_longitude, places.address as pl_address, category.id as category_id, planning.day_id
                
                from foodtruck
                         left join category on foodtruck.category_id = category.id
                         left join planning on foodtruck.id = planning.foodtruck_id
                         inner join places on places.id = planning.places_id
                
                where places.id = '%s' and planning.day_id = '%s' and planning.active = 1
            """ % (placeid, dayid))

    def apiv2(self, latitude, longitude, dayid):
        return self.sqlQuery(
            """
                select foodtruck.id as f_id, foodtruck.name as f_name, category.name as c_name, foodtruck.phone as f_phone,
                       foodtruck.email as f_email, foodtruck.website as f_website, foodtruck.facebook as f_facebook,
                       planning.active as active, places.id as pl_id, category.id as category_id,
                       case
                           when a.type_control = 'foodtruck' THEN if( a.place_control = foodtruck.id, TRUE, FALSE)
                           else false
                           end as verified,
                       (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) + COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) * 1609.34 AS distance_meters
                
                from foodtruck
                         left join category on foodtruck.category_id = category.id
                         left join planning on foodtruck.id = planning.foodtruck_id
                         left join admin a on a.place_control = foodtruck.id
                         inner join places on places.id = planning.places_id
                
                where planning.day_id = '%s' AND (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) + COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) * 1609.34 <= 10000
                
                
                order by distance_meters
            """ % (latitude, latitude, longitude, dayid, latitude, latitude, longitude)
        )

    def getPlacebyid(self, id, latitude, longitude):
        return self.sqlQuery(
            """
                select places.name as pl_name, places.latitude as pl_latitude,
                       places.longitude as pl_longitude, places.address as pl_address, places.id as pl_id, places.website as pl_website,
                       (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) + COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) * 1609.34 AS distance_meters
                
                from places
                where places.id = '%s'
            """ % (latitude, latitude, longitude, id)
        )

    def getPlaceVerifiedbyid(self, id):
        return self.sqlQuery(
            """
                select places.name as pl_name, places.latitude as pl_latitude,
                       places.longitude as pl_longitude, places.address as pl_address, places.id as pl_id, places.website as pl_website,
                       case
                           when a.type_control = 'places' THEN if( a.place_control = places.id, TRUE, FALSE)
                           else false
                           end as verified
                
                from places
                         left join admin a on a.place_control = places.id
                where places.id = '%s'
            """ % (id)
        )

    def GetPlacesFromFoodtruckId(self, foodtruckId):
        return self.sqlQuery("""
            select f.id as f_id, pl.id as pl_id, pl.name as pl_name, d.id as d_id
            from places as pl
                     inner join planning p on pl.id = p.places_id
                     inner join foodtruck f on p.foodtruck_id = f.id
                     inner join day d on p.day_id = d.id
            where f.id = '%s'
    """ % foodtruckId)

    def getFoodtruckFromPlacesId(self, placeId):
        return self.sqlQuery("""
            select f.id as f_id, f.name as f_name, pl.id as pl_id, pl.name as pl_name, d.id as d_id
            from places as pl
                     inner join planning p on pl.id = p.places_id
                     inner join foodtruck f on p.foodtruck_id = f.id
                     inner join day d on p.day_id = d.id
            where pl.id = '%s'
""" % placeId)

    def getPlacebydistance(self, latitude, longitude):
        return self.sqlQuery("""
            select places.id   as pl_id, places.name as pl_name,
                   (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) +
                         COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) *
                   1609.34     AS distance_meters
            
            from places
            
            where (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) +
                        COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) *
                  1609.34 <= 10000
            
            
            order by distance_meters
        """ % (latitude, latitude, longitude, latitude, latitude, longitude,))

    def getFoodtruckFromId(self, id):
        return self.sqlQuery("""
            select foodtruck.id       as f_id,
                   foodtruck.name     as f_name,
                   category.name      as c_name,
                   foodtruck.phone    as f_phone,
                   foodtruck.email    as f_email,
                   foodtruck.website  as f_website,
                   foodtruck.facebook as f_facebook,
                   category.id        as category_id,
                   case
                       when a.type_control = 'foodtruck' THEN if(a.place_control = foodtruck.id, TRUE, FALSE)
                       else false
                       end            as verified
            from foodtruck
                     left join category on foodtruck.category_id = category.id
                     left join admin a on a.place_control = foodtruck.id
            where foodtruck.id = '%s'
        """ % (id))


    # Execute an SQL query and returns the result
    def sqlQuery(self, q):
        res = self.cur.execute(q)
        return self.cur.fetchall()
