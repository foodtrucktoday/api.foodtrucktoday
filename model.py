#  Copyright (c) 2020 Romain ODET
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
       (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) + COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) * 1609.34 AS distance_meters

from foodtruck
         left join category on foodtruck.category_id = category.id
         left join planning on foodtruck.id = planning.foodtruck_id
         inner join places on places.id = planning.places_id

where planning.day_id = '%s' AND (ACOS(SIN(RADIANS('%s')) * SIN(RADIANS(places.latitude)) + COS(RADIANS('%s')) * COS(RADIANS(places.latitude)) * COS(RADIANS(places.longitude - '%s'))) * 3959) * 1609.34 <= 10000


order by distance_meters


            """ % (latitude, latitude, longitude, dayid, latitude, latitude, longitude)
        )

    def getPlacebyid(self, id):
        return self.sqlQuery(
            """
            select places.name as pl_name, places.latitude as pl_latitude,
       places.longitude as pl_longitude, places.address as pl_address, places.id as pl_id
            from places
            where places.id = '%s'
            
            """ % id
        )

    # Execute an SQL query and returns the result
    def sqlQuery(self, q):
        res = self.cur.execute(q)
        return self.cur.fetchall()
