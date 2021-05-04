#  Copyright (c) 2021 Romain ODET for Foodtruck Today
#
#

import imp
import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

wsgi = imp.load_source('wsgi', 'webserver.py')
application = wsgi.app
