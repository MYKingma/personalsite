# config.py for implementing a city guide webapp
#
# Maurice Kingma
#
#
# python program for  the configuration of stadsgids.mauricekingma.nl

import os
import requests
import datetime
import locale
import ast
import rq
import random
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_session import Session
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from flask_wtf.csrf import CSRFProtect
from hashlib import blake2b
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.sql import func
from redis import Redis

from models import *

# define constants
GOOGLE_API_KEY = os.getenv("GOOLE_API_KEY")
API_TYPES = ["art_gallery", "bakery", "bar", "bicycle_store", "book_store", "bowling_alley", "cafe", "casino", "florist", "library", "liquor_store", "meal_delivery", "meal_takeaway", "movie_rental", "movie_theater", "museum", "night_club", "park", "restaurant", "spa", "stadium", "store", "tourist_attraction", "zoo", "brewery", "distillery", "wineshop", "coffeeroasters", "beerbar"]
TYPES_DICT = {"": "Geen voorkeur", "art_gallery": "Kunstgallerij", "bakery": "Bakkerij", "bar": "Bar", "bicycle_store": "Fietsenwinkel", "book_store": "Boekenwinkel", "bowling_alley": "Bowlingbaan", "cafe": "Cafe", "casino": "Casino", "florist": "Bloemenwinkel", "library": "Bibliotheek", "liquor_store": "Slijterij", "meal_delivery": "Bezorgrestaurant", "meal_takeaway": "Afhaalrestaurant", "movie_rental": "Videotheek", "movie_theater": "Bioscoop", "museum": "Museum", "night_club": "Nachtclub", "park": "Park", "restaurant": "Restaurant", "spa": "Spa", "stadium": "Stadion", "store": "Winkel", "tourist_attraction": "Toeristenattractie", "zoo": "Dierentuin", "brewery": "Brouwerij", "distillery": "Destileerderij", "wineshop": "Wijnwinkel", "coffeeroasters": "Koffiebranders", "beerbar": "Biercafé", "cocktailbar": "Cocktailbar"}
RESULT_FILTER = ["sexshop", "sex", "gay", "2020", "kamerverhuur", "fetish", "erotic", "xxx", "lust"]

# search categories
SEARCH_TYPES = ["", "bakery", "bar", "book_store", "cafe", "casino", "library", "liquor_store", "movie_theater", "museum", "night_club", "restaurant", "spa", "store"]
REC_SEARCH_TYPES = ["", "bakery", "bar", "cafe", "museum", "night_club", "restaurant", "store", "brewery", "distillery", "wineshop", "coffeeroasters", "beerbar"]

# category icon dict
ICON_DICT = {"bakery": "bread-slice", "book_store": "book", "casino": "dice", "library": "book-reader", "liqour_store": "wine-bottle", "cinema": "film", "museum": "palette", "night_club": "compact-disc", "spa": "hot-tub", "store": "shopping-basket", "restaurant": "utensils", "brewery": "beer", "beerbar": "beer", "coacktailbar": "cocktail", "cofferoasters": "coffee", "wineshop": "wine-glass-alt", "distillery": "whiskey", "bar": "glass-cheers", "cafe": "mug-hot"}

# configure Flask app
app = Flask(__name__)

# configure Secret-Key
app.secret_key = os.getenv('SECRET_KEY')

# configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'
db.init_app(app)

# configure session, use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# configure migrations
Migrate(app, db, compare_type=True, render_as_batch=True)

# configure admin interface tabs
admin = Admin(app, name='Dashboard', index_view=AdminView(User, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Role, db.session))
admin.add_view(AdminView(Newsletter, db.session))
admin.add_view(AdminView(Blog, db.session))
admin.add_view(AdminView(Recommendation, db.session))
admin.add_view(AdminView(Highlight, db.session))
admin.add_view(AdminView(Review, db.session))
admin.add_view(AdminView(Event, db.session))
admin.add_view(AdminView(Request, db.session))

# configure
admin.add_link(MenuLink(name='Back to site', url='/stadsgids/dashboard'))


# configure Flask-login
login_manager = LoginManager()
login_manager.init_app(app)


# configure Flask-Mail
app.config['MAIL_SERVER']='smtp.mail.me.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = "mauricekingma@me.com"
mail = Mail(app)

# set password for timestamp-emailtoken
if not os.getenv("SECURITY_PASSWORD_SALT"):
    raise RuntimeError("SECURITY_PASSWORD_SALT is not set")
else:
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv("SECURITY_PASSWORD_SALT")

# set locale to dutch
locale.setlocale(locale.LC_ALL, "nl_NL")

# set Flask WTF CSRFProtect
csrf = CSRFProtect(app)


if os.getenv("PRODUCTION_SERVER"):

    # import worker
    from runworker import conn

    # set worker Queue
    queue = rq.Queue('default', connection=conn)

    # set redirect to https
    @app.before_request
    def before_request():
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)
