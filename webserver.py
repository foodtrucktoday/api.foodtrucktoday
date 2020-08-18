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
import os

from model import Model
from flask import *
from flask_httpauth import HTTPDigestAuth
import dotenv
import json

dotenv.load_dotenv()  # for python-dotenv method

# Create flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = '817C38A0721CE4E8FD8E340FEFBE247E78B2A4'
app.config['DEBUG'] = True
# Define all routes (URL)
auth = HTTPDigestAuth()

users = json.loads(os.environ.get('api_users'))


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

# main application
if __name__ == '__main__':
    # under windows, there is a bug in a module which prevents the usage of debug=True
    # the bug should be fixed within days or weeks, but in the meantime do not enable debug
    app.run()
