# application.py for implementing a city guide webapp
#
# Maurice Kingma
# Minor Programmeren - Web App Studio
#
# python program for website


# import packages
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_session import Session
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit
from hashlib import blake2b
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.sql import func
import datetime
import requests
import locale

from models import *

# define constants
GOOGLE_API_KEY = "AIzaSyCph_mUz9AYLa0VlsSjsg98b92GRz6HedM"
API_TYPES = ["art_gallery", "bakery", "bar", "bicycle_store", "book_store", "bowling_alley", "cafe", "casino", "florist", "library", "liquor_store", "meal_delivery", "meal_takeaway", "movie_rental", "movie_theater", "museum", "night_club", "park", "restaurant", "spa", "stadium", "store", "tourist_attraction", "zoo"]
TYPES_DICT = {"": "Geen voorkeur", "art_gallery": "Kunstgallerij", "bakery": "Bakkerij", "bar": "Bar", "bicycle_store": "Fietsenwinkel", "book_store": "Boekenwinkel", "bowling_alley": "Bowlingbaan", "cafe": "Cafe", "casino": "Casino", "florist": "Bloemenwinkel", "library": "Bibliotheek", "liquor_store": "Slijterij", "meal_delivery": "Bezorgrestaurant", "meal_takeaway": "Afhaalrestaurant", "movie_rental": "Videotheek", "movie_theater": "Bioscoop", "museum": "Museum", "night_club": "Nachtclub", "park": "Park", "restaurant": "Restaurant", "spa": "Spa", "stadium": "Stadion", "store": "Winkel", "tourist_attraction": "Toeristenattractie", "zoo": "Dierentuin"}
RESULT_FILTER = ["sexshop", "sex", "gay", "2020", "kamerverhuur", "fetish", "erotic", "xxx", "lust"]
# configure Flask app
app = Flask(__name__)

# configure Secret-Key
app.secret_key = os.getenv('SECRET_KEY')

# configure database
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# configure session, use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure migrations
Migrate(app, db, compare_type=True, render_as_batch=True)

# configure admin interface
admin = Admin(app, name='Dashboard', index_view=AdminView(User, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Role, db.session))
admin.add_view(AdminView(UserRoles, db.session))
admin.add_view(AdminView(Recommendation, db.session))
admin.add_view(AdminView(Review, db.session))
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
app.config['SECURITY_PASSWORD_SALT'] = os.getenv("SECURITY_PASSWORD_SALT")

# set locale to dutch
locale.setlocale(locale.LC_ALL, "nl_NL")


# test code
@app.route('/test')
def test():
    return redirect(url_for('guide'))

# handlers
@app.route('/loguit')
def logout():
    # log out user
    logout_user()
    flash("Successvol uitgelogd", 'success')
    return redirect(url_for('guide'))

@app.route('/deletereview/<name>/<place_id>')
def deletereview(place_id, name):
    # delete own review
    review = Review.query.filter_by(place_id=place_id, user_id=current_user.id).first()
    db.session.delete(review)
    db.session.commit()
    flash(f"Review verwijderd", "success")
    return redirect(url_for('location', place_id=place_id, name=name))

@app.route('/stadsgids/resetwachtwoord', methods=["POST"])
def reset():
    # get email and passwords
    email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    # check if input exists
    if not password1 or not password2:
        flash("Niet alle velden waren ingevuld", 'password' )
        return render_template("resetpass.html", email=email)

    # check if passswords match
    if password1 != password2:
        flash("Wachtwoorden komen niet overeen", 'password')
        return render_template("resetpass.html", email=email)

    # hash password
    password = blake2b(password1.encode()).hexdigest()

    # get user and set password
    user = User.query.filter_by(email=email).first()
    user.password = password
    db.session.commit()

    # show message
    flash("Wachtwoord opnieuw ingesteld, je kunt gelijk inloggen", "success")
    return redirect(url_for('guide'))

# custom decorators
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # check if user is logged in and has active roles
            if not current_user.is_authenticated:
               return login_manager.unauthorized()
            roles = current_user.get_user_roles()
            if role not in roles:
                return login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# handlers
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # message and route for unathorized users
    flash("Pagina alleen voor gebruikers, log in om te bekijken", 'info')
    return redirect(url_for('guide'))

# request routes
@app.route('/usernamecheck', methods=["POST"])
def usernamecheck():
    # get form information
    username = request.form.get("username")

    # check if available
    user = User.query.filter_by(username=username).first()

    # send result
    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/emailcheck', methods=["POST"])
def emailcheck():
    # get form information
    email = request.form.get("email").lower()

    # check if available
    user = User.query.filter_by(email=email).first()

    # send result
    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/nieuwebevestiging', methods=["POST"])
def new_conformation():
    # get form info
    email = request.form.get('email').lower()

    # get user
    user = User.query.filter_by(email=email).first()

    # check if user exists
    if not user:
        flash("E-mail adres niet bekend", 'warning')
        return redirect(url_for('not_confirmed'), "303")

    # check if email already confirmed
    if user.confirmed == True:
        flash("E-mailadres al bevestigd", "success")
        return redirect(url_for('guide'))

    # generate token confirmation email
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

    # send email for confirmation
    msg = Message("Bevestig je e-mailadres om je account te activeren", recipients=[email])
    msg.body = "klik op de volgende link: http://127.0.0.1:5000/stadsgids/emailbevestigen/" + token
    mail.send(msg)
    flash(f"E-mail verstuurd naar {email} met een nieuwe bevestigingslink", "success")
    return redirect(url_for('guide'))

@app.route('/location/action', methods=["POST"])
def action_location():

    # get form information
    place_id = request.form.get('place_id')
    button = request.form.get('button')
    user = User.query.get(current_user.id)
    name = request.form.get('locationname')
    website = request.form.get('website')

    # check what action should be performed
    if button == "favourite":
        for favourite in user.favourites:

            # delete favourite if relation exists
            if place_id == favourite.place_id:
                db.session.delete(favourite)
                db.session.commit()
                return jsonify({"success": True})

        # add new favourite if relation does not exist
        newfavourite = Favourite(place_id=place_id)
        db.session.add(newfavourite)
        db.session.commit()
        return jsonify({"success": True})

    if button == "recommend":

        # check if request already made
        for req in user.requests:
            if place_id == req.place_id:
                return jsonify({"success": False})

        # send email for request
        msg = Message(f"{user.firstname} vraagt zich af of {name} een leuke plek is om te bezoeken", recipients=["mauricekingma@me.com"])
        msg.html = render_template("recommendmail.html", name=user.firstname, email=user.email, location=name, website=website, place_id=place_id)
        mail.send(msg)
        newreq = Request(place_id=place_id)
        db.session.add(newreq)
        db.session.commit()
        return jsonify({"success": True})

    if button == "upvote":
        review = Review.query.filter_by(id=request.form.get('review_id')).first()
        for upvote in review.upvotes:

            # delete upvote if relation exists
            if upvote.user_id == current_user.id:
                db.session.delete(upvote)
                db.session.commit()
                return jsonify({"success": True, "count": review.get_upvote_count(), "status": "deleted"})

        # add upvote if relation does not exist
        newupvote = Upvote(review_id=request.form.get('review_id'))
        db.session.add(newupvote)
        db.session.commit()
        return jsonify({"success": True, "count": review.get_upvote_count(), "status": "added"})

# page routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/stadsgids', methods=["GET", "POST"])
def guide():
    if request.method == "GET":
        return render_template("guide.html")

    # get form information
    username = request.form.get("username")
    password = request.form.get("password")

    # hash password
    hpassword = blake2b(password.encode()).hexdigest()

    # get user info
    user = User.query.filter_by(username=username).first()

    # check if username exists otherwise show message
    if not user:
        flash("Gebruikersnaam niet bekend, heb je je al geregistreerd?", 'warning')
        return redirect(request.referrer)

    # if password is a match set session details and login user
    elif user.password == hpassword:
        if user.confirmed == False:
            flash(f"E-mailadres nog niet bevestigd, vraag hier een nieuwe link aan als deze verlopen is", 'warning')
            return redirect(url_for('not_confirmed'))
        login_user(user)
        flash(f"Ingelogd, welkom {username}", 'success')
        return redirect(request.referrer)

    # else return for wrong password
    else:
        flash("Wachtwoord onjuist, probeer het nog eens of vraag een nieuw wachtwoord aan", 'warning')
        return redirect(request.referrer)

@app.route('/stadsgids/registreren', methods=["GET", "POST"])
def register():
    # check for login otherwise return registration.html
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for('guide'))
        else:
            return render_template('register.html')

    # get form information
    username = request.form.get("username")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email").lower()
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    # check if all fields are filled
    if not username or not firstname or not lastname or not email or not password1 or not password2:
        flash("Niet alle velden waren ingevuld", 'password' )
        return redirect(url_for('register'), "303")

    # check if details are available
    user = User.query.filter_by(username=username).first()
    if user:
        flash(f"Gebruikersnaam {username} al in gebruik", 'username')
        return redirect(url_for('register'), "303")

    user = User.query.filter_by(email=email).first()
    if user:
        flash(f"E-mailadres {email} al in gebruik", 'email')
        return redirect(url_for('register'), "303")

    # check if passswords match
    if password1 != password2:
        flash("Wachtwoorden komen niet overeen", 'password')
        return redirect(url_for('register'), "303")

    # hash password
    password = blake2b(password1.encode()).hexdigest()

    # create new user
    new_user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password)

    # add user role
    role = Role.query.filter_by(name='User').first()
    new_user.roles.append(role)

    # generate token confirmation email
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

    # send email for confirmation
    msg = Message("Bevestig je e-mailadres om je account te activeren", recipients=[email])
    msg.body = "klik op de volgende link: http://127.0.0.1:5000/stadsgids/emailbevestigen/" + token

    try:
        mail.send(msg)
    except:
        flash("Registratie mislukt, controleer of je een geldig e-mailadres hebt ingevoerd", "warning")
        return redirect(url_for('register'), "303")


    # show succes message
    flash("Registratie geslaagd, check je inbox om je account te activeren", 'success')

    # add new user
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('register'))

@app.route('/stadsgids/emailbevestigen')
def not_confirmed():
    return render_template("confirm.html")

@app.route('/stadsgids/emailbevestigen/<token>')
def confirm_email(token):
    # configure serializer and check token (3600s is 1h)
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    expiration = 3600
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)

    # return not_confirmed route if expired
    except: return redirect(url_for('not_confirmed'))
    user = User.query.filter_by(email=email).first()

    # check if already confirmed
    if user.confirmed == True:
        flash("E-mailadres al bevestigd", "success")
        return redirect(url_for('guide'))

    # set to confirmed in database
    user.confirmed = True
    user.email_confirmed_at = datetime.datetime.now()
    db.session.commit()
    flash("E-mailadres bevestigd", 'success')
    login_user(user)
    return redirect(url_for('guide'))

@app.route('/stadsgids/wachtwoordvergeten', methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")

    # get form info
    email = request.form.get("email").lower()
    user= User.query.filter_by(email=email).first()

    # check if user exists
    if not user:
        flash("E-mail adres niet bekend", 'warning')
        return redirect(url_for('forgot'), "303")

    # generate token reset password
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

    # send email for confirmation
    msg = Message("Reset je wachwoord", recipients=[email])
    msg.body = "klik op de volgende link om je wachtwoord opnieuw in te stellen: http://127.0.0.1:5000/stadsgids/resetwachtwoord/" + token
    try:
        mail.send(msg)
    except:
        flash("Sturen wachtwoord mislukt, problemen met e-mail server", "warning")
        return redirect(url_for('guide'), "303")

    flash(f"E-mail met wachtwoordreset link verstuurd naar {email}", 'success')
    return redirect(url_for('forgot'), "303")

@app.route('/stadsgids/resetwachtwoord/<token>')
def resetpass(token):
    # configure serializer and check token (3600s is 1h)
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    expiration = 3600
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)

    # check if link is expired
    except:
        flash("Link verlopen, vraag een nieuwe link aan", "warning")
        return redirect(url_for('forgot'))
    return render_template("resetpass.html", email=email)

@app.route('/stadsgids/locatie/<name>/<place_id>', methods=["GET", "POST"])
def location(place_id, name):
    # declare location variables
    location = {}
    user = None
    visible = None

    # check if location is recommended and get recommendation info
    recommendation = Recommendation.query.filter_by(place_id=place_id).first()
    if recommendation:
        if not recommendation.visible:
            recommendation = None
            visible = False
        else:
            visible = True

    # check for login and get user-location info
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        for favourite in user.favourites:

            # set shape icons (fas = solid, far = outline)
            if place_id == favourite.place_id:
                location["favourite"] = "fas"
                break
            else:
                location["favourite"] = "far"
        if len(user.favourites) == 0:
            location["favourite"] = "far"

        for req in user.requests:
            if place_id == req.place_id:
                location["req"] = "fas"
                break
            else:
                location["req"] = "far"
        if len(user.requests) == 0:
            location["req"] = "far"

        # get reviews for location and declare variables
        allreviews = Review.query.filter_by(place_id=place_id).all()
        location["reviews"] = []
        location["ownreview"] = None
        location["guiderating"] = ""
        location["count"] = False

        # set review variables
        if allreviews:
            mean = 0.00
            for review in allreviews:
                mean = mean + review.stars
                if review.user_id is current_user.id:
                    location["ownreview"] = review
                else:
                    location["reviews"].append(review)

            location["guiderating"] = round(mean / len(allreviews), 1)
            location["count"] = len(allreviews)
    if request.method == "GET":

        # google places api request for location
        res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": place_id, "fields": "name,formatted_address,formatted_phone_number,icon,type,photo,website,opening_hours,price_level,rating,business_status,place_id", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})

        # set location variables
        if res.status_code == 200:
            data = res.json()
            location["name"] = data["result"]["name"]
            location["address"] = data["result"]["formatted_address"].split(",")
            location["icon"] = data["result"]["icon"]
            location["place_id"] = data["result"]["place_id"]
            if "formatted_phone_number" in data["result"]:
                location["phone"] = data["result"]["formatted_phone_number"]
            if "formatted_phone_number" in data["result"]:
                location["phone"] = data["result"]["formatted_phone_number"]
            if "opening_hours" in data["result"]:
                if "weekday_text" in data["result"]["opening_hours"]:
                    for i in range(len(data["result"]["opening_hours"]["weekday_text"])):
                        data["result"]["opening_hours"]["weekday_text"][i] = data["result"]["opening_hours"]["weekday_text"][i].split()[1]
                    location["opening_hours"] = data["result"]["opening_hours"]["weekday_text"]
            elif data["result"]["business_status"] == "CLOSED_TEMPORARILY":
                location["open"] = "Tijdelijk gesloten"
            elif data["result"]["business_status"] == "CLOSED_PERMANENTLY":
                location["open"] = "Permanent gesloten"
            else:
                location["open"] = "Onbekend"

            # google photos api request for a maximum of 3 photos
            if "photos" in data["result"]:
                photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "1000", "photoreference": data["result"]["photos"][0]["photo_reference"]})
                if photo.status_code == 200:
                    location["photo1source"] = data["result"]["photos"][0]["html_attributions"][0]
                    location["photo1"] = photo.url
                    print(location["photo1source"])
                if len(data["result"]["photos"]) > 1:
                    photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "1000", "photoreference": data["result"]["photos"][1]["photo_reference"]})
                    if photo.status_code == 200:
                        location["photo2source"] = data["result"]["photos"][1]["html_attributions"][0]
                        location["photo2"] = photo.url
                if len(data["result"]["photos"]) > 2:
                    location["photo3source"] = data["result"]["photos"][2]["html_attributions"][0]
                    photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "1000", "photoreference": data["result"]["photos"][2]["photo_reference"]})
                    if photo.status_code == 200:
                        location["photo3"] = photo.url

            # set location varibles
            if "price_level" in data["result"]:
                 location["price_level"] = data["result"]["price_level"] * "€"
            if "rating" in data["result"]:
                location["rating"] = data["result"]["rating"]
            if "user_ratings_total" in data["result"]:
                location["totalrate"] = data["result"]["user_ratings_total"]
            if "website" in data["result"]:
                location["website"] = data["result"]["website"]
            if "types" in data["result"]:
                types = []
                for type in data["result"]["types"]:
                    if type in TYPES_DICT:
                        for value, key in TYPES_DICT.items():
                            if type == value:
                                types.append(key)
                location["types"] = types

            # google embed maps api request for location
            map = requests.get("https://www.google.com/maps/embed/v1/place", params={"key": GOOGLE_API_KEY, "q": "place_id:" + place_id})
            if map.status_code == 200:
                location["map"] = map.url
        return render_template("location.html", location=location, recommendation=recommendation, visible=visible)

    # get review information
    stars = request.form.get('rating')
    review = request.form.get('review')

    # add review to database
    newreview = Review(place_id=place_id, stars=stars, review=review)
    db.session.add(newreview)
    db.session.commit()
    flash(f"Review geplaatst", "success")
    return redirect(url_for('location', place_id=place_id, name=name))

@app.route('/stadsgids/nieuw')
def new():
    return render_template("new.html")

@app.route('/stadsgids/zoeken', methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html", types=TYPES_DICT)

    # declare result list
    results = []

    # check type of search
    if request.form.get('form') == "regular":

        # google place search api request
        res = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json", params={"key": GOOGLE_API_KEY, "input": request.form.get('search'), "inputtype": "textquery", "fields": "name,formatted_address,place_id,types,photos,opening_hours,price_level,rating,icon", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
        if res.status_code == 200:
            data = res.json()
            for candidate in data["candidates"]:

                # check if place in amsterdam and filter for types and adult content
                if "Amsterdam" in candidate["formatted_address"].replace(',', '').split() and any(item in API_TYPES for item in candidate["types"]) and not any(item in RESULT_FILTER for item in candidate["name"].lower().split()):

                    # set result variables
                    candidate["formatted_address"] = candidate["formatted_address"].split(", ")
                    if "photos" in candidate:

                        # google places photo api request for thumbnail
                        photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "125", "photoreference": candidate["photos"][0]["photo_reference"]})
                        if photo.status_code == 200:
                            candidate["photos"] = photo.url
                        else:
                            candidate["photos"] = None

                    # set result variables
                    if "opening_hours" in candidate:
                        if "open_now" in candidate["opening_hours"]:
                            if candidate["opening_hours"]["open_now"] == True:
                                candidate["opening_hours"] = "Nu open"
                            elif candidate["opening_hours"]["open_now"] == False:
                                candidate["opening_hours"] = "Gesloten"
                        else:
                            candidate["opening_hours"] = ""
                    if "price_level" in candidate:
                        candidate["price_level"] = candidate["price_level"] * "€"

                    # append candidate to resultlist
                    results.append(candidate)

        # check if recommendation on page should be visible
        for result in results:
            recommendation = Recommendation.query.filter_by(place_id=result["place_id"]).first()
            if recommendation:
                if recommendation.visible:
                    result["recommended"] = True
        return render_template("search.html", results=results, types=TYPES_DICT)

    # get filters if advanced search
    minprice = int(request.form.get('minprice'))
    maxprice = int(request.form.get('maxprice'))
    type = request.form.get('type')
    opennow = request.form.get('opennow')
    keyword = request.form.get('query')

    # set params for request
    params = {"key": GOOGLE_API_KEY, "keyword": keyword, "location": "52.348460,4.885954", "radius": "10000"}

    # add params for filters
    if opennow:
        params["opennow"] = ""
    if minprice != 0 or maxprice != 4:
        params["minprice"] = request.form.get('minprice')
        params["maxprice"] = request.form.get('maxprice')
    if type:
        params["type"] = type

    # google places nearby search api request
    res = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params=params)
    data = res.json()

    for result in data["results"]:
        # check if place in amsterdam and filter for types and adult content
        if "Amsterdam" in result["vicinity"].replace(',', '').split() and any(item in API_TYPES for item in result["types"]) and not any(item in RESULT_FILTER for item in result["name"].lower().split()):

            # set result variables
            result["formatted_address"] = result["vicinity"].split(", ")
            if "photos" in result:

                # google places photo api request for thumbnail
                photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "250", "photoreference": result["photos"][0]["photo_reference"]})
                if photo.status_code == 200:
                    result["photos"] = photo.url
                else:
                    result["photos"] = None

            # set result variables
            if "opening_hours" in result:
                if "open_now" in result["opening_hours"]:
                    if result["opening_hours"]["open_now"] == True:
                        result["opening_hours"] = "Nu open"
                    elif result["opening_hours"]["open_now"] == False:
                        result["opening_hours"] = "Gesloten"
                else:
                    result["opening_hours"] = ""
            if "price_level" in result:
                result["price_level"] = result["price_level"] * "€"
            results.append(result)

    # check if recommendation should be visible
    for result in results:
        recommendation = Recommendation.query.filter_by(place_id=result["place_id"]).first()
        if recommendation:
            if recommendation.visible:
                result["recommended"] = True
    return render_template("search.html", results=results, types=TYPES_DICT)

@app.route('/stadsgids/weekend')
@login_required
def weekend():
    return render_template("weekend.html")

@app.route('/stadsgids/profiel')
@login_required
def profile():
    return render_template("profile.html")

@app.route('/stadsgids/dashboard')
@role_required('Administrator')
def dashboard():
    return render_template("dashboard.html")

@app.route('/stadsgids/dashboard/nieuw', methods=["GET", "POST"])
@role_required('Administrator')
def controlnew():
    if request.method == "GET":
        return render_template("controlnew.html")

    # get recommendation info
    action = request.form.get('action')
    place_id = request.form.get('place_id')
    review = request.form.get('review')
    tip = request.form.get('tip')
    visible = True if request.form.get('visible') else False
    if int(request.form.get('price_level')) != 0:
        price_level = int(request.form.get('price_level'))
    else:
        price_level = 0

    # get opening info and convert depending on input (24 = 24h/7 none = unknown)
    opentimes = []
    opening = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in opening:
        time = request.form.get(day)
        if time == "" or time == "Onbekend":
            opening = "Onbekend"
            break
        elif time == '24' or time == "24 uur per dag geopend":
            opening = "24 uur per dag geopend"
            break
        else:
            opentimes.append(time)
    if len(opentimes) == 7:
        opening = []
        opening = opentimes

    # check if new recommendation or change existing
    if action == "new":
        newrecommendation = Recommendation(place_id=place_id, review=review, tip=tip, visible=visible, price_level=price_level, opening=opening)
        db.session.add(newrecommendation)
        db.session.commit()
        flash("Aanbeveling toegevoegd", 'success' )
    else:
        recommendation = Recommendation.query.filter_by(place_id=place_id).first()
        recommendation.review = review
        recommendation.tip = tip
        recommendation.visible = visible
        recommendation.price_level = price_level
        recommendation.opening = opening
        db.session.commit()
        flash("Aanbeveling gewijzigd", 'success' )
    return render_template("controlnew.html")

@app.route('/stadsgids/dashboard/nieuw/wijzigen/<name>/<place_id>')
@role_required('Administrator')
def changenew(place_id, name):
    # get recommendation and set variable for existing weektext
    recommendation = Recommendation.query.filter_by(place_id=place_id).first()
    weektext = type(recommendation.opening) == list
    return render_template("changenew.html", recommendation=recommendation, weektext=weektext, name=name)

@app.route('/stadsgids/dashboard/nieuw/opstellen/<name>/<place_id>')
@role_required('Administrator')
def createnew(name, place_id):
    return render_template("createnew.html", name=name, place_id=place_id)

@app.route('/stadsgids/dashboard/nieuwsbrief')
@role_required('Administrator')
def newsletter():
    return render_template("newsletter.html")

@app.route('/stadsgids/dashboard/nieuwsbrief/opstellen')
@role_required('Administrator')
def createnewsletter():
    return render_template("createnewsletter.html")

@app.route('/stadsgids/dashboard/checkreviews')
@role_required('Administrator')
def check():
    return render_template("check.html")
