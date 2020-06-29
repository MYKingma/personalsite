# application.py for implementing a city guide webapp
#
# Maurice Kingma
# Minor Programmeren - Web App Studio
#
# python program for website


# import packages
import os
import requests
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
import datetime
import locale
import ast
import rq
import random
from redis import Redis
from runworker import conn

from models import *

# define constants
GOOGLE_API_KEY = "AIzaSyCph_mUz9AYLa0VlsSjsg98b92GRz6HedM"
API_TYPES = ["art_gallery", "bakery", "bar", "bicycle_store", "book_store", "bowling_alley", "cafe", "casino", "florist", "library", "liquor_store", "meal_delivery", "meal_takeaway", "movie_rental", "movie_theater", "museum", "night_club", "park", "restaurant", "spa", "stadium", "store", "tourist_attraction", "zoo", "brewery", "distillery", "wineshop", "coffeeroasters", "beerbar"]
TYPES_DICT = {"": "Geen voorkeur", "art_gallery": "Kunstgallerij", "bakery": "Bakkerij", "bar": "Bar", "bicycle_store": "Fietsenwinkel", "book_store": "Boekenwinkel", "bowling_alley": "Bowlingbaan", "cafe": "Cafe", "casino": "Casino", "florist": "Bloemenwinkel", "library": "Bibliotheek", "liquor_store": "Slijterij", "meal_delivery": "Bezorgrestaurant", "meal_takeaway": "Afhaalrestaurant", "movie_rental": "Videotheek", "movie_theater": "Bioscoop", "museum": "Museum", "night_club": "Nachtclub", "park": "Park", "restaurant": "Restaurant", "spa": "Spa", "stadium": "Stadion", "store": "Winkel", "tourist_attraction": "Toeristenattractie", "zoo": "Dierentuin", "brewery": "Brouwerij", "distillery": "Destileerderij", "wineshop": "Wijnwinkel", "coffeeroasters": "Koffiebranders", "beerbar": "Biercafé", "cocktailbar": "Cocktailbar"}
RESULT_FILTER = ["sexshop", "sex", "gay", "2020", "kamerverhuur", "fetish", "erotic", "xxx", "lust"]

# search categories
SEARCH_TYPES = ["", "bakery", "bar", "book_store", "cafe", "casino", "library", "liquor_store", "movie_theater", "museum", "night_club", "restaurant", "spa", "store"]
REC_SEARCH_TYPES = ["", "bakery", "bar", "cafe", "museum", "night_club", "restaurant", "store", "brewery", "distillery", "wineshop", "coffeeroasters", "beerbar"]

# icon dict
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

# configure admin interface
admin = Admin(app, name='Dashboard', index_view=AdminView(User, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Role, db.session))
admin.add_view(AdminView(Newsletter, db.session))
admin.add_view(AdminView(Blog, db.session))
admin.add_view(AdminView(Recommendation, db.session))
admin.add_view(AdminView(Highlight, db.session))
admin.add_view(AdminView(Review, db.session))
admin.add_view(AdminView(Event, db.session))
admin.add_view(AdminView(Request, db.session))

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

# set worker Queue
queue = rq.Queue('default', connection=conn)

# set Flask WTF CSRFProtect
csrf = CSRFProtect(app)


@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

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
    return redirect(request.referrer)

@app.route('/deleteevent/<event_id>/<name>')
def delete_event(event_id, name):
    # delete own review
    event = Event.query.filter_by(id=event_id).first()
    db.session.delete(event)
    db.session.commit()
    flash(f"Evenement verwijderd", "success")
    return redirect(request.referrer)

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
    link = request.url_root + "stadsgids/emailbevestigen/" + token
    msg.html = render_template('confirmmail.html')
    job = queue.enqueue('task.send_mail', msg)
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
        newfavourite = Favourite(place_id=place_id, name=name)
        db.session.add(newfavourite)
        db.session.commit()
        return jsonify({"success": True})

    if button == "recommend":

        # check if request already made
        for req in user.requests:
            if place_id == req.place_id:
                return jsonify({"success": False})

        # send email for request /stadsgids/locatie/<name>/<place_id>
        link = request.url_root + "stadsgids/locatie/" + name + "/" + place_id
        msg = Message(f"Ontvangstbevestiging informatieaanvraag voor {location.name}", recipients=["mauricekingma@me.com"])
        msg.html = render_template("recommendmail.html", name=user.firstname, location=name, website=website, place_id=place_id)
        job = queue.enqueue('task.send_mail', msg)
        newreq = Request(place_id=place_id, name=name)
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
    if "stadsgids." in request.url:
        return guide()
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")

    # get form information
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # send email to sender
    msg = Message("Onvangstbevestiging mauricekingma.nl", recipients=[email])
    msg.html = render_template('confirmmessagemail.html', name=name, email=email, message=message)
    job = queue.enqueue('task.send_mail', msg)

    # send email to author
    msg = Message(f"{name} heeft je een bericht gestuurd via mauricekingma.nl", recipients=["mauricekingma@me.com"])
    msg.html = render_template('contactmail.html', name=name, email=email, message=message)
    job = queue.enqueue('task.send_mail', msg)
    flash("E-mail verstuurd", 'info')

    return render_template('contact.html')

@app.route('/stadsgids', methods=["GET", "POST"])
def guide():
    if request.method == "GET":
        weeknum = datetime.datetime.now().isocalendar()[1]
        highlights = Highlight.query.all()
        for location in highlights:
            if location.week.isocalendar()[1] == weeknum:
                highlight = location
                break

        highlightDetails = {}
        # google places api request for location
        res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": highlight.place_id, "fields": "name,formatted_address,photo,opening_hours,price_level,rating,place_id,types", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
        if res.status_code == 200:
            data = res.json()
            highlightDetails["name"] = data["result"]["name"]
            highlightDetails["rating"] = data["result"]["rating"]
            highlightDetails["place_id"] = data["result"]["place_id"]
            if "price_level" in data["result"]:
                highlightDetails["price_level"] = data["result"]["price_level"] * "€"
            highlightDetails["formatted_address"] = data["result"]["formatted_address"].split(",")

            if "photos" in data["result"]:

                # google places photo api request for thumbnail
                photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "250", "photoreference": data["result"]["photos"][0]["photo_reference"]})
                if photo.status_code == 200:
                    highlightDetails["photos"] = photo.url
                else:
                    highlightDetails["photos"] = None
            highlightDetails["types"] = data["result"]["types"]
        recommendation = Recommendation.query.filter_by(place_id=highlight.place_id).first()
        if recommendation:
            highlightDetails["recommended"] = True
            highlightDetails["types"] = recommendation.type.replace("}", "").replace("{", "").split(",")
            highlightDetails["price_level"] = recommendation.price_level * "€"
        else:
            highlightDetails["recommended"] = False

        recommendations = Recommendation.query.filter_by(visible=True).order_by(Recommendation.date.desc()).limit(3).all()
        newRecommendations = []
        for recommendation in recommendations:
            result = {}

            # google places api request for location
            res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": recommendation.place_id, "fields": "name,formatted_address,photo,opening_hours,price_level,rating,place_id,types", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
            if res.status_code == 200:
                data = res.json()
                result["name"] = data["result"]["name"]
                result["rating"] = data["result"]["rating"]
                result["place_id"] = data["result"]["place_id"]
                if "price_level" in data["result"]:
                    result["price_level"] = data["result"]["price_level"] * "€"
                result["formatted_address"] = data["result"]["formatted_address"].split(",")

                if "photos" in data["result"]:

                    # google places photo api request for thumbnail
                    photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "250", "photoreference": data["result"]["photos"][0]["photo_reference"]})
                    if photo.status_code == 200:
                        result["photos"] = photo.url
                    else:
                        result["photos"] = None
                result["types"] = data["result"]["types"]
            guiderecommendation = Recommendation.query.filter_by(place_id=recommendation.place_id).first()
            if guiderecommendation:
                result["recommended"] = True
                result["types"] = guiderecommendation.type.replace("}", "").replace("{", "").split(",")
                result["price_level"] = guiderecommendation.price_level * "€"
            else:
                result["recommended"] = False
            newRecommendations.append(result)


        blogposts = Blog.query.filter_by(visible=True).order_by(Blog.date.desc()).limit(2).all()
        randomrec = random.choice(Recommendation.query.all())
        frontpageevent = Event.query.filter(Event.date > datetime.datetime.now()).order_by(Event.date).all()
        reviews = Review.query.order_by(Review.date.desc()).limit(3).all()
        return render_template("guide.html", highlight=highlight, highlightDetails=highlightDetails, TYPES_DICT=TYPES_DICT, ICON_DICT=ICON_DICT, newRecommendations=newRecommendations, blogposts=blogposts, tip=randomrec, events=frontpageevent, reviews=reviews)

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
    newsletter = request.form.get('newsletter')
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
    new_user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=password, newsletter=newsletter)

    # add user role
    role = Role.query.filter_by(name='User').first()
    new_user.roles.append(role)

    # generate token confirmation email
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

    # send email for confirmation
    msg = Message("Bevestig je e-mailadres om je account te activeren", recipients=[email])
    link = request.url_root + "stadsgids/emailbevestigen/" + token
    msg.html = render_template('confirmmail.html', firstname=firstname, email=email, link=link)
    job = queue.enqueue('task.send_mail', msg)

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

@app.route('/stadsgids/emailwijzigen/<token>')
def change_email(token):
    # configure serializer and check token (3600s is 1h)
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    expiration = 3600
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)

    # return not_confirmed route if expired
    except: return redirect(url_for('not_confirmed'))
    user = User.query.filter_by(newemail=email).first()

    # check if already confirmed
    if user.newemail == None:
        flash("E-mailadres al gewijzigd", "success")
        return redirect(url_for('guide'))

    # set to confirmed in database
    user.email_confirmed_at = datetime.datetime.now()
    user.email = user.newemail
    user.newemail = None
    db.session.commit()
    flash("E-mailadres gewijzigd", 'success')
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
    link = request.url_root + "stadsgids/resetwachtwoord/" + token
    msg.html = render_template('resetpassmail.html', firstname=user.firstname, link=link)
    job = queue.enqueue('task.send_mail', msg)

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

    # check if location has events an get event info when date is yet to come
    events = Event.query.filter_by(place_id=place_id).order_by(Event.date).all()
    for event in events:
        if event.date < datetime.datetime.now():
            events.remove(event)

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
        res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": place_id, "fields": "name,formatted_address,formatted_phone_number,icon,type,photo,website,opening_hours,price_level,rating,business_status,place_id,review", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})

        # set location variables
        if res.status_code == 200:
            data = res.json()
            location["name"] = data["result"]["name"]
            location["address"] = data["result"]["formatted_address"].split(",")
            location["applemapslink"] = location["address"][0]
            location["icon"] = data["result"]["icon"]
            location["place_id"] = data["result"]["place_id"]
            if "formatted_phone_number" in data["result"]:
                location["phone"] = data["result"]["formatted_phone_number"]
            if "formatted_phone_number" in data["result"]:
                location["phone"] = data["result"]["formatted_phone_number"]
            location["opening"] = True
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
                location["opening"] = False

            # google photos api request for a maximum of 3 photos
            if "photos" in data["result"]:
                photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "1000", "photoreference": data["result"]["photos"][0]["photo_reference"]})
                if photo.status_code == 200:
                    location["photo1source"] = data["result"]["photos"][0]["html_attributions"][0]
                    location["photo1"] = photo.url
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
            else:
                location["price_level"] = False
            if "rating" in data["result"]:
                location["rating"] = data["result"]["rating"]
            if "reviews" in data["result"]:
                location["totalrate"] = len(data["result"]["reviews"])
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
        return render_template("location.html", location=location, recommendation=recommendation, visible=visible, events=events)

    # get review information
    stars = request.form.get('rating')
    review = request.form.get('review')

    # add review to database
    newreview = Review(place_id=place_id, stars=stars, review=review, name=name)
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
        return render_template("search.html", search=False, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)

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
                    result["guidetype"] = recommendation.type.replace("{", "").replace("}", "").split(",")
        return render_template("search.html", search=True, results=results, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)

    # get filters if advanced search
    minprice = int(request.form.get('minprice'))
    maxprice = int(request.form.get('maxprice'))
    type = request.form.get('type')
    opennow = request.form.get('opennow')
    keyword = request.form.get('query')
    recommended = request.form.get('recommended')
    print(recommended)

    if not recommended:
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
                    result["guidetype"] = recommendation.type.replace("{", "").replace("}", "").split(",")
        return render_template("search.html", search=True, results=results, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)

    if type:
        type = TYPES_DICT[type]

    locations = Recommendation.query.filter(Recommendation.name.like(f"%{keyword}%"),Recommendation.type.like(f"%{type}%"),Recommendation.price_level > minprice,Recommendation.price_level <= maxprice).all()

    for location in locations:
        result = {}
        result["price_level"] = location.price_level * "€"
        result["recommended"] = True
        result["guidetype"] = location.type.replace("{", "").replace("}", "").split(",")


        # google places api request for location
        res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": location.place_id, "fields": "name,icon,formatted_address,photo,opening_hours,price_level,rating,place_id", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
        if res.status_code == 200:
            data = res.json()
            result["name"] = data["result"]["name"]
            if "open_now" in data["result"]["opening_hours"]:
                if data["result"]["opening_hours"]["open_now"]:
                    result["opening_hours"] = "Nu open"
                else:
                    result["opening_hours"] = "Gesloten"
            else:
                result["opening_hours"] = ""

            result["icon"] = data["result"]["icon"]
            result["rating"] = data["result"]["rating"]
            result["place_id"] = data["result"]["place_id"]

            result["formatted_address"] = data["result"]["formatted_address"].split(",")

            if "photos" in data["result"]:

                # google places photo api request for thumbnail
                photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "250", "photoreference": data["result"]["photos"][0]["photo_reference"]})
                if photo.status_code == 200:
                    result["photos"] = photo.url
                else:
                    result["photos"] = None
        results.append(result)
        if opennow:
            for result in results:
                if not result["opening_hours"] == "Nu open":
                    results.remove(result)





    return render_template("search.html", search=True, results=results, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)



@app.route('/stadsgids/weekend')
@login_required
def weekend():
    return render_template("weekend.html")

@app.route('/stadsgids/profiel', methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first()
    favourites = []
    for favourite in user.favourites:
        result = {}
        # google places api request for location
        res = requests.get("https://maps.googleapis.com/maps/api/place/details/json", params={"key": GOOGLE_API_KEY, "place_id": favourite.place_id, "fields": "name,formatted_address,photo,opening_hours,price_level,rating,place_id,types", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
        if res.status_code == 200:
            data = res.json()
            result["name"] = data["result"]["name"]
            result["rating"] = data["result"]["rating"]
            result["place_id"] = data["result"]["place_id"]
            if "price_level" in data["result"]:
                result["price_level"] = data["result"]["price_level"] * "€"
            result["formatted_address"] = data["result"]["formatted_address"].split(",")

            if "photos" in data["result"]:

                # google places photo api request for thumbnail
                photo = requests.get("https://maps.googleapis.com/maps/api/place/photo", params={"key": GOOGLE_API_KEY, "maxwidth": "250", "photoreference": data["result"]["photos"][0]["photo_reference"]})
                if photo.status_code == 200:
                    result["photos"] = photo.url
                else:
                    result["photos"] = None
            result["types"] = data["result"]["types"]
        recommendation = Recommendation.query.filter_by(place_id=favourite.place_id).first()
        if recommendation:
            result["recommended"] = True
            result["types"] = recommendation.type.replace("}", "").replace("{", "").split(",")
            result["price_level"] = recommendation.price_level * "€"
        else:
            result["recommended"] = False
        favourites.append(result)


    if request.method == "GET":
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT)

    action = request.form.get('action')

    if action == "newsletter":
        if request.form.get('newsletter'):
            user.newsletter = True
            flash("Je bent nu ingeschreven voor de nieuwsbrief", "success")
        else:
            user.newsletter = False
            flash("Je bent nu uitgeschreven voor de nieuwsbrief", "success")

    if action == "filter":
        filter = request.form.get('filter')
        if filter != "":
            filtered = []
            for favourite in favourites:
                if filter in favourite["types"]:
                    filtered.append(favourite)
            favourites = filtered
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT, filter=filter)


    if action == "changemail":
        print("change")
        email = request.form.get('email')
        other_user = User.query.filter_by(email=email).first()
        if other_user:
            flash(f"E-mailadres {email} al in gebruik", "email")
            return redirect(url_for('profile'))
        user.newemail = email

        # generate token confirmation email
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

        # send email for confirmation
        msg = Message("Bevestig je nieuwe e-mailadres", recipients=[email])
        link = request.url_root + "stadsgids/emailwijzigen/" + token
        db.session.commit()
        msg.html = render_template('changeemail.html', firstname=user.firstname, email=email, link=link)
        job = queue.enqueue('task.send_mail', msg)
        flash(f"Link naar e-mailadres {email} gestuurd ter bevestiging wijzigen email", "success")
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT)

    if action == "changepass":
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # check if passswords match
        if password1 != password2:
            flash("Wachtwoorden komen niet overeen", 'password')
            return redirect(url_for('profile'), "303")

        # hash and set password
        password = blake2b(password1.encode()).hexdigest()
        user.password = password
        flash("Wachtwoord gewijzigd", "success")
        db.session.commit()
        return redirect(url_for('profile'))

@app.route('/stadsgids/dashboard')
@role_required('Administrator')
def dashboard():
    return render_template("dashboard.html")

@app.route('/stadsgids/dashboard/nieuw', methods=["GET", "POST"])
@role_required('Administrator')
def controlnew():
    if request.method == "GET":
        recommendations = Recommendation.query.all()
        return render_template("controlnew.html", recommendations=recommendations, types=TYPES_DICT)

    action = request.form.get('action')
    if action == "filter":
        filter = request.form.get('type')
        filtered = []
        recommendations = Recommendation.query.all()
        for recommendation in recommendations:
            if TYPES_DICT[filter] in recommendation.type.replace("}", "").replace("{", "").split(",") or filter == "":
                filtered.append(recommendation)
        return render_template("controlnew.html", recommendations=filtered, types=TYPES_DICT)

    # get recommendation info
    name = request.form.get('name')
    place_id = request.form.get('place_id')
    review = request.form.get('review')
    tip = request.form.get('tip')
    types = request.form.getlist('type')
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
        if time == "" or time == "Onbekend" or time == "onbekend":
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
        newrecommendation = Recommendation(place_id=place_id, review=review, tip=tip, visible=visible, price_level=price_level, opening=opening, type=types, name=name)
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
        recommendation.type = types
        recommendation.date = datetime.datetime.now()
        db.session.commit()
        flash("Aanbeveling gewijzigd", 'success' )
    return redirect(url_for('location', place_id=place_id, name=name))

@app.route('/stadsgids/dashboard/nieuw/wijzigen/<name>/<place_id>/<types>/<opening>/<price_level>')
@role_required('Administrator')
def changenew(place_id, name, types, opening, price_level):
    # get recommendation and set variable for existing weektext
    recommendation = Recommendation.query.filter_by(place_id=place_id).first()
    events = Event.query.filter_by(place_id=place_id).order_by(Event.date).all()
    weektext = type(recommendation.opening) == list
    typeslist = ast.literal_eval(types)
    return render_template("changenew.html", recommendation=recommendation, weektext=weektext, name=name, events=events, types=typeslist, API_TYPES=API_TYPES, TYPES_DICT=TYPES_DICT, opening=opening, price_level=price_level)

@app.route('/stadsgids/dashboard/nieuw/opstellen/<name>/<place_id>/<types>/<opening>/<price_level>')
@role_required('Administrator')
def createnew(name, place_id, types, opening, price_level):
    typeslist = ast.literal_eval(types)
    return render_template("createnew.html", name=name, place_id=place_id, types=typeslist, API_TYPES=API_TYPES, TYPES_DICT=TYPES_DICT, opening=opening, price_level=price_level)

@app.route('/stadsgids/dashboard/nieuw/evenement/<name>/<place_id>', methods=["GET", "POST"])
@role_required('Administrator')
def create_event(name, place_id):
    if request.method == "GET":
        return render_template("createevent.html", name=name, place_id=place_id)

    title = request.form.get("title")
    date = request.form.get("date")
    time = request.form.get("time")
    description = request.form.get("description")
    date_string = date + "/" + time
    try:
        datetime_object = datetime.datetime.strptime(date_string, '%d%m%Y/%H%M')
    except:
        flash("Datumvelden niet goed ingevoerd", 'warning' )
        return redirect(url_for("location", name=request.form.get("name"), place_id=request.form.get("place_id")))

    event = Event(title=title, date=datetime_object, description=description, place_id=place_id, name=name)
    db.session.add(event)
    db.session.commit()
    flash("Evenement geplaatst", 'success' )
    return redirect(url_for("location", name=request.form.get("name"), place_id=request.form.get("place_id")))

@app.route('/stadsgids/dashboard/nieuwsbrief', methods=['GET', 'POST'])
@role_required('Administrator')
def newsletter():
    if request.method == "GET":
        newsletters = Newsletter.query.all()
        return render_template("newsletter.html", newsletters=newsletters)
    newsletter = Newsletter(date=datetime.datetime.now(), subject="", body="", send=False)
    db.session.add(newsletter)
    db.session.commit()
    return redirect(url_for('createnewsletter', newsletter_id=newsletter.id))


@app.route('/stadsgids/dashboard/nieuwsbrief/opstellen/<newsletter_id>', methods=["GET", "POST"])
@role_required('Administrator')
def createnewsletter(newsletter_id):
    newsletter = Newsletter.query.filter_by(id=newsletter_id).first()
    if request.method == "GET":
        return render_template("createnewsletter.html", newsletter=newsletter)

    # get textarea info
    action = request.form.get("action")
    body = request.form.get("editor1")
    subject=request.form.get("subject")


    newsletter.subject = subject
    newsletter.body = body
    db.session.commit()
    if action == "save":
        flash("Wijzigingen opgeslagen", 'success')
    if action == "test":
        return render_template("newsletterbase.html", body=body, name="Naam")
    if action == "delete":
        db.session.delete(newsletter)
        db.session.commit()
        flash("Nieuwsbrief verwijderd", 'success')
        return redirect(url_for('newsletter'))
    if action == "send":
        recipients = User.query.filter_by(newsletter=True).all()
        for recipient in recipients:
            msg = Message(newsletter.subject, recipients=recipient)
            msg.html = render_template("newsletterbase.html", name=recipient.firstname, body=newsletter.body)
            job = queue.enqueue('task.send_mail', msg)



    return render_template("createnewsletter.html", newsletter=newsletter)

@app.route('/stadsgids/dashboard/blog', methods=['GET', 'POST'])
@role_required('Administrator')
def blog():
    if request.method == 'GET':
        blogposts = Blog.query.all()
        return render_template("blog.html", blogposts=blogposts)

    blogpost = Blog(date=datetime.datetime.now(), title="", short="", body="", visible=False)
    db.session.add(blogpost)
    db.session.commit()
    return redirect(url_for('createblog', blog_id=blogpost.id))


@app.route('/stadsgids/dashboard/blog/opstellen/<blog_id>', methods=['GET', 'POST'])
@role_required('Administrator')
def createblog(blog_id):
    blogpost = Blog.query.filter_by(id=blog_id).first()
    if request.method == "GET":
        return render_template("createblog.html", blogpost=blogpost)

    action = request.form.get('action')
    title = request.form.get('title')
    short = request.form.get('short')
    body = request.form.get('editor1')

    blogpost.title = title
    blogpost.short = short
    blogpost.body = body
    db.session.commit()

    if action == "save":
        flash("Wijzigingen opgeslagen", 'success')
    if action == "publish":
        blogpost.visible = True
        blogpost.date = datetime.datetime.now()
        db.session.commit()
        flash("Post gepubliceerd", 'success')
    if action == "delete":
        db.session.delete(blogpost)
        db.session.commit()
        flash("Post verwijderd", 'success')
        return redirect(url_for('blog'))
    return render_template("createblog.html", blogpost=blogpost)


@app.route('/stadsgids/dashboard/checkreviews', methods=["GET", "POST"])
@role_required('Administrator')
def check():
    reviews = Review.query.all()

    if request.method == "GET":
        return render_template("check.html", reviews=reviews)

    # get action and review_id
    action = request.form.get('action')
    review_id = request.form.get('review_id')

    review = Review.query.filter_by(id=review_id).first()

    if action == "accept":
        review.checked = True
        db.session.commit()
        flash("Review geaccepteerd", 'success')

    if action == "block":
        review.checked = True
        review.review = "De inhoud van deze recensie is aanstootgevend en dus verwijderd."
        db.session.commit()
        flash("Review geblokkeerd", 'warning')

    return render_template("check.html", reviews=reviews)

@app.route('/stadsgids/dashboard/uitgelicht', methods=["GET", "POST"])
@role_required('Administrator')
def highlight():
    if request.method == "GET":
        highlights = Highlight.query.all()
        return render_template('highlight.html', highlights=highlights)
    place_id = request.form.get('place_id')
    name = request.form.get('name')
    previous = Highlight.query.order_by(Highlight.id.desc()).first()
    date = previous.week + datetime.timedelta(days=7)
    highlight = Highlight(place_id=place_id, name=name, week=date, description="")
    db.session.add(highlight)
    db.session.commit()
    return redirect(url_for('createhighlight', highlight_id=highlight.id))


@app.route('/stadsgids/dashboard/uitgelicht/wijzigen/<highlight_id>', methods=["GET", "POST"])
@role_required('Administrator')
def createhighlight(highlight_id):
    highlight = Highlight.query.filter_by(id=highlight_id).first()
    if request.method == "GET":
        return render_template('createhighlight.html', highlight=highlight)

    action = request.form.get('action')
    description = request.form.get('editor1')

    highlight.description = description
    db.session.commit()
    if action == "save":
        flash("Wijzigingen opgeslagen", 'success')
        return redirect(url_for('createhighlight', highlight_id=highlight.id))
    if action == "delete":
        db.session.delete(highlight)
        db.session.commit()
        flash("Uitgelicht verwijderd", "success")
        return redirect(url_for('highlight'))


@app.route('/stadsgids/dashboard/aanvragen')
@role_required('Administrator')
def inforequest():
    inforequests = Request.query.all()
    return render_template('requests.html', requests=inforequests)


@app.route('/stadsgids/dashboard/aanvragen/verwerken/<request_id>', methods=["GET", "POST"])
@role_required('Administrator')
def processrequests(request_id):
    inforequest = Request.query.filter_by(id=request_id).first()

    if request.method == "GET":
        return render_template('processrequests.html', request=inforequest)

    msg = Message(f"Meer informatie over {location.name}", recipients=[inforequest.user.email])
    msg.html = render_template("newsletterbase.html", name=inforequest.user.firstname, body=request.form.get('editor1'))
    job = queue.enqueue('task.send_mail', msg)
    inforequest.processed = True
    db.session.commit()
    flash("Informatieaanvraag verwerkt", "success")
    return redirect(url_for('inforequest'))

@app.route('/stadsgids/blog/<blog_id>')
def blogpost(blog_id):
    blog = Blog.query.filter_by(id=blog_id).first()
    return render_template('blogpost.html', blog=blog)
