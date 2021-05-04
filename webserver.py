#  Copyright (c) 2021 Romain ODET for Foodtruck Today

import os

from model import Model
from flask import *
from flask_httpauth import HTTPBasicAuth
import dotenv
import json
import requests
import re
import mimetypes
from itertools import groupby

dotenv.load_dotenv()  # for python-dotenv method

# Create flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = '817C38A0721CE4E8FD8E340FEFBE247E78B2A4'
# Define all routes (URL)
auth = HTTPBasicAuth()

# print(os.environ.get('api_users'))
users = json.loads(os.environ.get('api_users'))

mimetypes.add_type('image/svg+xml', '.svg')


# Define all routes (URL)
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


# defintion de la page d'accueil
@app.route('/index.html', methods=['GET', 'POST'])  # / is the URL
@app.route('/accueil/', methods=['GET', 'POST'])  # / is the URL
@app.route('/', methods=['GET', 'POST'])  # / is the URL
def index():
    return render_template('index.html')  # afficher la page index html

@app.route('/api/docs')
@auth.login_required
def get_docs():
    return render_template('swaggerui.html')


@app.route('/day/<id>/', methods=['GET', 'POST'])  # / is the URL
@auth.login_required
def Day_Selector(id):
    with Model() as model:
        requestReturn = model.GetFoodtruckDay(id)  # appel de la requete sql

    return jsonify(requestReturn)


@app.route('/all/', methods=['GET', 'POST'])  # / is the URL
@auth.login_required
def All_Foodtruck():
    with Model() as model:
        requestReturn = model.GetAllFoodtruck()  # appel de la requete sql

    return jsonify(requestReturn)


@app.route('/places/<place>/day/<dayid>/', methods=['GET', 'POST'])  # / is the URL
@auth.login_required
def GetPlacesIDandDayId(place, dayid):
    with Model() as model:
        requestReturn = model.GetFoodtruckByPlaceByDay(place, dayid)  # appel de la requete sql

    return jsonify(requestReturn)

@app.route('/v2/places/day/foodtruck/<foodtruckId>/', methods=['GET', 'POST'])
@auth.login_required
def GetPlacesFromFoodtruckId(foodtruckId):
    with Model() as model:
        requestReturn = model.GetPlacesFromFoodtruckId(foodtruckId)

    response = Response(json.dumps(requestReturn, ensure_ascii=False).encode('utf8'), content_type="application/json; charset=utf-8")
    return response

@app.route('/v2/foodtruck/day/places/<placesId>/', methods=['GET', 'POST'])
@auth.login_required
def GetFoodtruckFromPlacesId(placesId):
    with Model() as model:
        requestReturn = model.getFoodtruckFromPlacesId(placesId)

    response = Response(json.dumps(requestReturn, ensure_ascii=False).encode('utf8'), content_type="application/json; charset=utf-8")
    return response

@app.route('/v2/foodtruck/<id>/', methods=['GET', 'POST'])
@auth.login_required
def GetFoodtruckFromId(id):
    with Model() as model:
        requestReturn = model.getFoodtruckFromId(id)

    response = Response(json.dumps(requestReturn, ensure_ascii=False).encode('utf8'), content_type="application/json; charset=utf-8")
    return response

@app.route('/v2/<latitude>/<longitude>/<dayid>/', methods=['GET', 'POST'])  # / is the URL
@auth.login_required
def apiV2(latitude, longitude, dayid):
    with Model() as model:
        latitude = float(latitude)
        longitude = float(longitude)

        requestReturn = model.apiv2(latitude, longitude, dayid)  # appel de la requete sql

        # then use groupby with the same key
        groups = groupby(requestReturn, lambda content: content['pl_id'])

        result = ""

        result += "["
        j = 0

        for pl_id, group in groups:
            if j > 0:
                result += ','

            requestPlId = model.getPlacebyid(pl_id, latitude, longitude)
            parsePlId = requestPlId[0]

            result += str('{"pl_name":"')
            result += str(parsePlId['pl_name'])
            result += str('","pl_id":')
            result += str(parsePlId['pl_id'])
            result += str(',"pl_address":"')
            result += str(parsePlId['pl_address'].replace('\r\n', ','))
            result += str('","pl_latitude":')
            result += str(parsePlId['pl_latitude'])
            result += str(',"pl_longitude":')
            result += str(parsePlId['pl_longitude'])
            result += str(',"pl_website":"')
            result += str(parsePlId['pl_website'])
            result += str('","distance_meters":')
            result += str(parsePlId['distance_meters'])

            result += str(',"foodtrucks":[')

            i = 0
            for content in group:
                if i > 0:
                    result += ','
                result += str(content).replace("'", '"')
                i += 1

            result += ']}'
            j += 1

        result += "]"

    # json_string = json.dumps(result,ensure_ascii = False).strip('"')
    # creating a Response object to set the content type and the encoding
    response = Response(result, content_type="application/json; charset=utf-8")
    return response

@app.route('/v2/places/<latitude>/<longitude>/')
@auth.login_required
def getPlaceBydistance(latitude, longitude):
    latitude = float(latitude)
    longitude = float(longitude)
    with Model() as model:
        requestPlId = model.getPlacebydistance(latitude, longitude)
        print(requestPlId)

    return jsonify(requestPlId)

@app.route('/v2/places/<id>/')
@auth.login_required
def getPlaceById(id):

    with Model() as model:
        requestPlId = model.getPlaceVerifiedbyid(id)

    parsePlId = requestPlId[0]

    result1 = ""

    result1 += str('[{"pl_name":"')
    result1 += str(parsePlId['pl_name'])
    result1 += str('","pl_id":')
    result1 += str(parsePlId['pl_id'])
    result1 += str(',"pl_address":"')
    result1 += str(parsePlId['pl_address'].replace('\r\n', ','))
    result1 += str('","pl_latitude":')
    result1 += str(parsePlId['pl_latitude'])
    result1 += str(',"pl_longitude":')
    result1 += str(parsePlId['pl_longitude'])
    result1 += str(',"pl_website":"')
    result1 += str(parsePlId['pl_website'])
    result1 += str('","verified":')
    result1 += str(parsePlId['verified'])
    result1 += str('}]')

    response = Response(result1, content_type="application/json; charset=utf-8")
    return response

@app.route('/icon/<id>/<color>/')
@app.route('/icons/<id>/<color>/')
def getIcon(id, color):
    r = requests.get('https://static.foodtrucktoday.fr/images/icons/' + str(id) + '.svg')
    print('https://static.foodtrucktoday.fr/images/icons/' + str(id) + '.svg')
    if r.status_code == 200:
        if color:
            print('OK')
            data = re.sub(' xmlns="[^"]+"', '', r.content.decode('utf-8'), count=1)
            print(data)
            newdata = data.replace('<path', '<path fill="#' + color + '" stroke="#' + color + '"')
            print(newdata)
            return Response(newdata, mimetype='image/svg+xml')
        else:
            return 'no color', 400

    else:
        return 'no icon', 404


# main application
if __name__ == '__main__':
    # under windows, there is a bug in a module which prevents the usage of debug=True
    # the bug should be fixed within days or weeks, but in the meantime do not enable debug
    app.run()
