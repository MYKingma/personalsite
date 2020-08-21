# application.py for implementing a city guide webapp
#
# Maurice Kingma
#
#
# python program for page routes stadsgids.mauricekingma.nl

import os
from config import *
from locationinfo import *
from functions import *

# declare constants and filters
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
API_TYPES = ["art_gallery", "bakery", "bar", "bicycle_store", "book_store", "bowling_alley", "cafe", "casino", "florist", "library", "liquor_store", "meal_delivery", "meal_takeaway", "movie_rental", "movie_theater", "museum", "night_club", "park", "restaurant", "spa", "stadium", "store", "tourist_attraction", "zoo", "brewery", "distillery", "wineshop", "coffeeroasters", "beerbar", "terrace", "icecream", "cocktailbar"]
TYPES_DICT = {"": "Geen voorkeur", "art_gallery": "Kunstgallerij", "bakery": "Bakkerij", "bar": "Bar", "bicycle_store": "Fietsenwinkel", "book_store": "Boekenwinkel", "bowling_alley": "Bowlingbaan", "cafe": "Cafe", "casino": "Casino", "florist": "Bloemenwinkel", "library": "Bibliotheek", "liquor_store": "Slijterij", "meal_delivery": "Bezorgrestaurant", "meal_takeaway": "Afhaalrestaurant", "movie_rental": "Videotheek", "movie_theater": "Bioscoop", "museum": "Museum", "night_club": "Nachtclub", "park": "Park", "restaurant": "Restaurant", "spa": "Spa", "stadium": "Stadion", "store": "Winkel", "tourist_attraction": "Toeristenattractie", "zoo": "Dierentuin", "brewery": "Brouwerij", "distillery": "Destileerderij", "wineshop": "Wijnwinkel", "coffeeroasters": "Koffiebranders", "beerbar": "Biercafé", "cocktailbar": "Cocktailbar", "terrace": "Terras", "icecream": "IJssalon"}
RESULT_FILTER = ["sexshop", "sex", "gay", "2020", "kamerverhuur", "fetish", "erotic", "xxx", "lust"]
SEARCH_TYPES = ["", "bakery", "bar", "book_store", "cafe", "casino", "library", "liquor_store", "movie_theater", "museum", "night_club", "restaurant", "spa", "store"]
REC_SEARCH_TYPES_NL = ["Bakkerij", "Bar", "Cafe", "Museum", "Nachtclub", "Restaurant", "Winkel", "Slijterij", "Brouwerij", "Destileerderij", "Wijnwinkel", "Koffiebranders", "Biercafé", "Terras", "IJssalon", "Cocktailbar"]
REC_SEARCH_TYPES = ["", "bakery", "bar", "cafe", "museum", "night_club", "restaurant", "store", "liquor_store", "brewery", "distillery", "wineshop", "coffeeroasters", "beerbar", "terrace", "icecream", "cocktailbar"]
ICON_DICT = {"bakery": "bread-slice", "book_store": "book", "casino": "dice", "library": "book-reader", "liquor_store": "wine-bottle", "cinema": "film", "museum": "palette", "night_club": "compact-disc", "spa": "hot-tub", "store": "shopping-basket", "restaurant": "utensils", "brewery": "beer", "beerbar": "beer", "cocktailbar": "cocktail", "coffeeroasters": "coffee", "wineshop": "wine-glass-alt", "distillery": "whiskey", "bar": "glass-cheers", "cafe": "mug-hot", "terrace": "umbrella-beach", "icecream": "ice-cream"}


# test route
@app.route('/test')
def test():
    return redirect(url_for('guide'))

# error handlers
@app.errorhandler(400)
def bad_request(e):
    raise Exception("Bad request")
    message = "Probleem met verzoek."
    return render_template('error.html', status_code="400", message=message), 400

@app.errorhandler(404)
def page_not_found(e):
    message = "De pagina die je probeert te bezoeken bestaat niet."
    return render_template('error.html', status_code="404", message=message), 404

@app.errorhandler(403)
def forbidden(e):
    message = "De pagina die je probeert te bezoeken is niet voor jou toegankelijk."
    return render_template('error.html', status_code=403, message=message), 403

@app.errorhandler(410)
def gone(e):
    message = "De pagina die je probeert te bezoeken bestaat niet meer."
    return render_template('error.html', status_code=410, message=message), 410

@app.errorhandler(500)
def server_error(e):
    # note that we set the 404 status explicitly
    message = "Server-fout."
    return render_template('error.html', status_code=500, message=message), 500


# redirect routes
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
    # delete event
    event = Event.query.filter_by(id=event_id).first()
    db.session.delete(event)
    db.session.commit()
    flash(f"Evenement verwijderd", "success")
    return redirect(request.referrer)

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
    link = request.url_root + "emailbevestigen/" + token
    msg.html = render_template('confirmmail.html')
    job = queue.enqueue('task.send_mail', msg)
    flash(f"E-mail verstuurd naar {email} met een nieuwe bevestigingslink", "success")
    return redirect(url_for('guide'))

# decorators
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # message and route for unathorized users
    flash("Pagina alleen voor gebruikers, log in om te bekijken", 'info')
    return redirect(url_for('guide'))

# request routes
@app.route('/hidelocation', methods=["POST"])
def hide_location():
    place_id = request.form.get('place_id')
    name = request.form.get('name')

    newHidden = Hidden(name=name, place_id=place_id)
    db.session.add(newHidden)
    db.session.commit()

    return jsonify({"success": True})

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

        details = get_location_link_information(place_id=place_id)
        # send confirmation email for request /locatie/<name>/<place_id>
        link = request.url_root + "locatie/" + name + "/" + place_id
        msg = Message(f"Ontvangstbevestiging informatieaanvraag voor {name}", recipients=[user.email])
        msg.html = render_template("recommendmail.html", name=user.firstname, location=name, website=website, result=details, TYPES_DICT=TYPES_DICT, ICON_DICT=ICON_DICT)
        job = queue.enqueue('task.send_mail', msg)

        # add request in database
        newreq = Request(place_id=place_id, name=name)
        db.session.add(newreq)
        db.session.commit()
        return jsonify({"success": True})

    if button == "upvote":
        # get review
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

@app.route('/autocomplete', methods=["POST"])
def autocomplete():
    recommendations = Recommendation.query.filter(Recommendation.name.ilike(f"%{request.form.get('query').lower()}%"), Recommendation.visible).all()
    autolist = {}
    recommList = {}
    categList = {}
    if recommendations:
        doubles = []
        for item in recommendations:
            if item.doubles:
                place_ids = get_double_place_ids(item.place_id)
                for double_place_id in place_ids:
                    doubles.append(double_place_id)

        resultsNoDoubles = []
        for item in recommendations:
            if item.place_id not in doubles:
                resultsNoDoubles.append(item)

        recommendations = resultsNoDoubles


        for item in recommendations:
            recommList[item.name] = item.place_id
        autolist["recommList"] = recommList

    for type in REC_SEARCH_TYPES_NL:
        if request.form.get('query').lower() in type.lower():
            typeList = Recommendation.query.filter(Recommendation.type.ilike(f"%{type.lower()}%"), Recommendation.visible).all()
            for key, value in TYPES_DICT.items():
                if value == type:
                    categTitle = key
            if typeList:
                categList[categTitle] = {}

                doubles = []
                for item in typeList:
                    if item.doubles:
                        place_ids = get_double_place_ids(item.place_id)
                        for double_place_id in place_ids:
                            doubles.append(double_place_id)

                resultsNoDoubles = []
                for item in typeList:
                    if item.place_id not in doubles:
                        resultsNoDoubles.append(item)

                typeList = resultsNoDoubles


                for item in typeList:
                    categList[categTitle][item.name] = item.place_id
    if categList:
        autolist["categList"] = categList
        autolist["ICON_DICT"] = ICON_DICT
        autolist["TYPES_DICT"] = TYPES_DICT
    return jsonify(autolist)

@app.route('/loadhighlight', methods=["POST"])
def loadhighlight():
    week = request.form.get('week')
    shift = request.form.get('shift')
    weeknum = int(week) + int(shift)
    data = {}

    highlights = Highlight.query.all()
    for location in highlights:
        if location.week.isocalendar()[1] == weeknum:
            data["description"] = location.description
            data["name"] = location.name
            data["week"] = location.week.isocalendar()[1]
            data["totalshift"] = int(datetime.datetime.now().isocalendar()[1]) - weeknum
            data["linkinfo"] = get_location_link_information(location.place_id)
            data["types"] = []
            for type in data["linkinfo"]["types"]:
                for key, value in TYPES_DICT.items():
                    if type == value:
                        if key in ICON_DICT:
                            data["types"].append(ICON_DICT[key])
            for type in data["linkinfo"]["types"]:
                if type in ICON_DICT:
                    data["types"].append(ICON_DICT[type])
            break

    data["previous"] = False
    for location in highlights:
        if location.week.isocalendar()[1] == weeknum - 1:
            data["previous"] = True
            break

    data["next"] = True
    if datetime.datetime.now().isocalendar()[1] == weeknum:
        data["next"] = False

    return jsonify(data)



# page routes
@app.route('/')
def index():
    if "stadsgids." in request.url or "stadsgidsadam" in request.url or "stadsgids-ams" in request.url:
        return redirect(url_for('guide'))
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

@app.route('/home', methods=["GET", "POST"])
def guide():
    if request.method == "GET":

        # get weeknumber and corresponding highlight
        weeknum = datetime.datetime.now().isocalendar()[1]
        highlights = Highlight.query.all()
        for location in highlights:
            if location.week.isocalendar()[1] == weeknum:
                highlight = location
                break

        # get details for highlight-location link
        highlightDetails = get_location_link_information(place_id=highlight.place_id)

        # get 3 last added recommendations
        recommendations = Recommendation.query.filter_by(visible=True).order_by(Recommendation.date.desc()).limit(3).all()
        newRecommendations = []

        # get details for location-links
        for recommendation in recommendations:
            linkDetails = get_location_link_information(place_id=recommendation.place_id)
            newRecommendations.append(linkDetails)

        # get 3 recent added blogposts
        blogposts = Blog.query.filter_by(visible=True).filter(Blog.title!="Privacyverklaring").filter(Blog.title!="Over Stadsgids").order_by(Blog.date.desc()).limit(2).all()

        # get random recommendation-tip
        randomrec = random.choice(Recommendation.query.filter_by(visible=True).filter(Recommendation.tip!="").all())

        # get events and reviews for front-page
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

    if not user:
        user = User.query.filter_by(email=username).first()

    # check if username exists otherwise show message
    if not user:
        flash("Gebruikersnaam of emailadres niet bekend, heb je je al geregistreerd? Je kunt ook met een e-mailadres inloggen.", 'warning')
        return redirect(request.referrer)

    # if password is a match set session details and login user
    elif user.password == hpassword:
        if user.confirmed == False:
            flash(f"E-mailadres nog niet bevestigd, vraag hier een nieuwe link aan als deze verlopen is", 'warning')
            return redirect(url_for('not_confirmed'))
        login_user(user)
        flash(f"Ingelogd, welkom {user.username}", 'success')
        return redirect(request.referrer)

    # else return for wrong password
    else:
        flash("Wachtwoord onjuist, probeer het nog eens of vraag een nieuw wachtwoord aan", 'warning')
        return redirect(request.referrer)

@app.route('/registreren', methods=["GET", "POST"])
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
    link = request.url_root + "emailbevestigen/" + token
    msg.html = render_template('confirmmail.html', firstname=firstname, email=email, link=link, username=username)
    job = queue.enqueue('task.send_mail', msg)

    # show succes message
    flash("Registratie geslaagd, check je inbox om je account te activeren", 'success')

    # add new user
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('register'))

@app.route('/emailbevestigen')
def not_confirmed():
    return render_template("confirm.html")

@app.route('/emailbevestigen/<token>')
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

@app.route('/emailwijzigen/<token>')
def change_email(token):
    # configure serializer and check token (3600s is 1h)
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    expiration = 3600
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)

    # return not confirmed error if expired
    except:
        flash("Link verlopen, vraag via de profielpagina een nieuwe aan", "warning")
        return redirect(url_for('guide'))
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

@app.route('/wachtwoordvergeten', methods=["GET", "POST"])
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
    link = request.url_root + "resetwachtwoord/" + token
    msg.html = render_template('resetpassmail.html', firstname=user.firstname, link=link, username=user.username)
    job = queue.enqueue('task.send_mail', msg)

    flash(f"E-mail met wachtwoordreset link verstuurd naar {email}", 'success')
    return redirect(url_for('forgot'), "303")

@app.route('/resetwachtwoord', methods=["POST"])
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

@app.route('/resetwachtwoord/<token>')
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

@app.route('/locatie/<name>/<place_id>', methods=["GET", "POST"])
def location(place_id, name):
    # declare location variables
    location = {}
    user = None
    visible = None
    sameRec = None
    doubles = None

    # check if location is recommended and get recommendation info
    recommendation = Recommendation.query.filter_by(place_id=place_id).first()
    if recommendation:
        if not recommendation.visible:
            visible = False
        else:
            visible = True
        sameRec = get_info_parent_rec_from_double_if_sameRec(place_id)

        doubles = get_link_info_doubles(get_double_place_ids(place_id))


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
                if "periods" in data["result"]["opening_hours"]:
                    location["opening_hours"] = ["Gesloten", "Gesloten", "Gesloten", "Gesloten", "Gesloten", "Gesloten", "Gesloten"]
                    for item in data["result"]["opening_hours"]["periods"]:
                        day = item["open"]["day"] - 1
                        if location["opening_hours"][day] == "Gesloten":
                            location["opening_hours"][day] = item["open"]["time"][:2] + ":" + item["open"]["time"][2:] + "-" + item["close"]["time"][:2] + ":" + item["close"]["time"][2:]
                        else:
                            location["opening_hours"][day] = location["opening_hours"][day].split("-")[0] + "-" + item["close"]["time"][:2] + ":" + item["close"]["time"][2:]

                elif "weekday_text" in data["result"]["opening_hours"]:
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

        return render_template("location.html", location=location, recommendation=recommendation, visible=visible, events=events, sameRec=sameRec, doubles=doubles)

    # get review information
    stars = request.form.get('rating')
    review = request.form.get('review')

    # add review to database
    newreview = Review(place_id=place_id, stars=stars, review=review, name=name)
    db.session.add(newreview)
    db.session.commit()
    flash(f"Review geplaatst", "success")
    return redirect(url_for('location', place_id=place_id, name=name))

@app.route('/nieuw')
def new():
    return render_template("new.html")

@app.route('/zoeken', methods=["GET", "POST"])
def search():
    if request.method == "GET":
        # get amount of recommendations
        amountRecommendations = int(len(Recommendation.query.filter_by(visible=True).all()))
        return render_template("search.html", search=False, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT, amountRecommendations=amountRecommendations)

    # declare result list
    results = []

    # check type of search
    if request.form.get('form') == "regular":

        # google place search api request
        res = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json", params={"key": GOOGLE_API_KEY, "input": request.form.get('search'), "inputtype": "textquery", "fields": "name,formatted_address,place_id,types,photos,opening_hours,price_level,rating,icon", "locationbias": "circle:10000@52.348460,4.885954", "language": "nl"})
        if res.status_code == 200:
            data = res.json()

            hidden = []
            toHide = Hidden.query.all()
            for hide in toHide:
                hidden.append(hide.place_id)

            doubles = []
            for candidate in data["candidates"]:
                parentRec = get_parent_rec_from_double(candidate["place_id"])
                if parentRec:
                    place_ids = get_double_place_ids(parentRec.place_id)
                    for double_place_id in place_ids:
                        doubles.append(double_place_id)

            resultsNoDoubles = []
            for candidate in data["candidates"]:
                if candidate["place_id"] not in doubles and candidate["place_id"] not in hidden:
                    resultsNoDoubles.append(candidate)

            data["candidates"] = resultsNoDoubles

            for candidate in data["candidates"][:10]:

                # check if place in amsterdam and filter for types and adult content
                if "Amsterdam" in candidate["formatted_address"].replace(',', '').split() and any(item in API_TYPES for item in candidate["types"]) and not any(item in RESULT_FILTER for item in candidate["name"].lower().split()):

                    # set result variables
                    candidate["formatted_address"] = candidate["formatted_address"].split(", ")
                    if "photos" in candidate:
                        candidate["photos"] = get_photo_url(candidate["photos"][0]["photo_reference"])

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
                result["recommended"] = True
                result["types"] = recommendation.type.replace("{", "").replace("}", "").split(",")
                result["price_level"] = recommendation.price_level * "€"
                if recommendation.visible:
                    result["visible"] = True
        return render_template("search.html", search=True, results=results, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)

    # get filters if advanced search
    minprice = int(request.form.get('minprice'))
    maxprice = int(request.form.get('maxprice'))
    type = request.form.get('type')
    opennow = request.form.get('opennow')
    keyword = request.form.get('query')
    recommended = request.form.get('recommended')

    if not recommended:
        # set params for request
        params = {"key": GOOGLE_API_KEY, "keyword": keyword, "location": "52.348460,4.885954", "radius": "10000", "language": "nl"}

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

        doubles = []
        for result in data["results"]:
            parentRec = get_parent_rec_from_double(result["place_id"])
            if parentRec:
                place_ids = get_double_place_ids(parentRec.place_id)
                for double_place_id in place_ids:
                    doubles.append(double_place_id)

        resultsNoDoubles = []
        for result in data["results"]:
            if result["place_id"] not in doubles:
                resultsNoDoubles.append(result)

        data["results"] = resultsNoDoubles


        for result in data["results"][:10]:
            # check if place in amsterdam and filter for types and adult content
            if "Amsterdam" in result["vicinity"].replace(',', '').split() and any(item in API_TYPES for item in result["types"]) and not any(item in RESULT_FILTER for item in result["name"].lower().split()):

                # set result variables
                result["formatted_address"] = result["vicinity"].split(", ")
                if "photos" in result:
                    result["photos"] = get_photo_url(result["photos"][0]["photo_reference"])

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
                result["recommended"] = True
                result["types"] = recommendation.type.replace("{", "").replace("}", "").split(",")
                result["price_level"] = recommendation.price_level * "€"
                if recommendation.visible:
                    result["visible"] = True
        return render_template("search.html", search=True, results=results, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)

    # set filter when needed
    if type:
        type = TYPES_DICT[type]

    locations = Recommendation.query.filter(Recommendation.name.ilike(f"%{keyword}%"),Recommendation.type.like(f"%{type}%"),Recommendation.visible == True,Recommendation.price_level > minprice,Recommendation.price_level <= maxprice).all()

    doubles = []
    for location in locations:
        parentRec = get_parent_rec_from_double(location.place_id)
        if parentRec:
            place_ids = get_double_place_ids(parentRec.place_id)
            for double_place_id in place_ids:
                doubles.append(double_place_id)

    resultsNoDoubles = []
    for location in locations:
        if location.place_id not in doubles:
            resultsNoDoubles.append(location)

    locations = resultsNoDoubles

    # get link details
    for location in locations:
        details = get_location_link_information(place_id=location.place_id)
        results.append(details)
        if opennow:
            for result in results:
                if not result["opening_hours"] == "Nu open":
                    results.remove(result)


    return render_template("search.html", search=True, results=results, TYPES_DICT=TYPES_DICT, REC_SEARCH_TYPES=REC_SEARCH_TYPES, SEARCH_TYPES=SEARCH_TYPES, ICON_DICT=ICON_DICT)

@app.route('/weekend')
@login_required
def weekend():
    return render_template("weekend.html")

@app.route('/profiel', methods=["GET", "POST"])
@login_required
def profile():
    # get current user
    user = User.query.filter_by(id=current_user.id).first()

    # get user favourites and get link details
    favourites = []
    for favourite in user.favourites:
        details = get_location_link_information(favourite.place_id)
        favourites.append(details)
    if request.method == "GET":
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT)

    # get type of action
    action = request.form.get('action')

    # change theme
    if action == "theme":
        if request.form.get('theme') == "dark":
            user.theme = "dark"
            flash("Dark-mode voorkeur opgeslagen", "success")
        elif request.form.get('theme') == "light":
            user.theme = "light"
            flash("Light-mode voorkeur opgeslagen", "success")
        elif request.form.get('theme') == "auto":
            user.theme = "auto"
            flash("Thema past zich nu aan het thema van de computer aan", "success")
        db.session.commit()
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT)

    # change newsletter subscription
    if action == "newsletter":
        if request.form.get('newsletter'):
            user.newsletter = True
            flash("Je bent nu ingeschreven voor de nieuwsbrief", "success")
        else:
            user.newsletter = False
            flash("Je bent nu uitgeschreven voor de nieuwsbrief", "success")
        db.session.commit()
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT)

    # filter favourites
    if action == "filter":
        recommendations = Recommendation.query.all()
        if request.form.get('filter') != "":
            filtered = []
            for favourite in favourites:
                if favourite["recommended"]:
                    filter = TYPES_DICT[request.form.get('filter')]
                else:
                    filter = request.form.get('filter')
                if filter in favourite["types"]:
                    filtered.append(favourite)
            favourites = filtered
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT, filter=request.form.get('filter'))

    # change email address
    if action == "changemail":
        email = request.form.get('email')
        other_user = User.query.filter_by(email=email).first()
        if other_user:
            flash(f"E-mailadres {email} al in gebruik", "warning")
            return redirect(url_for('profile'))
        user.newemail = email

        # generate token confirmation email
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

        # send email for confirmation
        msg = Message("Bevestig je nieuwe e-mailadres", recipients=[email])
        link = request.url_root + "emailwijzigen/" + token
        db.session.commit()
        msg.html = render_template('changeemail.html', firstname=user.firstname, email=email, link=link)
        job = queue.enqueue('task.send_mail', msg)
        flash(f"Link naar e-mailadres {email} gestuurd ter bevestiging wijzigen email", "success")
        return render_template("profile.html", user=user, TYPES_DICT=TYPES_DICT, favourites=favourites, ICON_DICT=ICON_DICT)

    # change password
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

@app.route('/dashboard')
@role_required('Administrator')
def dashboard():
    return render_template("dashboard.html")

@app.route('/dashboard/nieuw', methods=["GET", "POST"])
@role_required('Administrator')
def controlnew():
    if request.method == "GET":
        # get all recommendations
        recommendations = Recommendation.query.all()
        return render_template("controlnew.html", recommendations=recommendations, types=TYPES_DICT)

    # get type of action
    action = request.form.get('action')

    # filter recommendations
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
        if time == "Onbekend" or time == "Onbekend" or time == "onbekend":
            opening = "Onbekend"
            break
        elif time == '24' or time == "24 uur per dag geopend":
            opening = "24 uur per dag geopend"
            break
        elif time == "" or time == None:
            opening = "notspecified"
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
        if request.form.get('double'):
            sameRec = False
            if request.form.get('sameRec'):
                sameRec = True
            parentRec = Recommendation.query.filter_by(place_id=request.form.get('double')).first()
            parentRec.add_double_location(place_id=place_id, same_recommendation=sameRec)
        else:
            parentRec = get_parent_rec_from_double(place_id)
            if parentRec:
                parentRec.delete_double_if_exist(place_id)

        db.session.commit()
        flash("Aanbeveling gewijzigd", 'success' )
    return redirect(url_for('location', place_id=place_id, name=name))

@app.route('/dashboard/nieuw/wijzigen/<name>/<place_id>/<types>/<opening>/<price_level>')
@role_required('Administrator')
def changenew(place_id, name, types, opening, price_level):
    # get recommendation and set variable for existing weektext
    recommendation = Recommendation.query.filter_by(place_id=place_id).first()
    events = Event.query.filter_by(place_id=place_id).order_by(Event.date).all()
    recommendations = Recommendation.query.all()
    possibleDoubles = []
    for double in recommendations:
        if similar(name, double.name) >= 0.6 and double.place_id != place_id:
            possibleDoubles.append(double)
    databaseDouble = Double.query.filter(Double.double_place_id.like(f"%{place_id}%")).first()
    sameRec = False
    if databaseDouble:
        doubleDict = ast.literal_eval(databaseDouble.double_place_id)
        if place_id in doubleDict:
            if doubleDict[place_id]:
                sameRec = True
    if "00" in recommendation.opening:
        weektext = recommendation.opening.replace('{', '').replace('}', '').split(',')
    else:
        weektext = False
    typeslist = ast.literal_eval(types)
    return render_template("changenew.html", recommendation=recommendation, weektext=weektext, name=name, events=events, types=typeslist, API_TYPES=API_TYPES, TYPES_DICT=TYPES_DICT, opening=opening, price_level=price_level, possibleDoubles=possibleDoubles, databaseDouble=databaseDouble, sameRec=sameRec)

@app.route('/dashboard/nieuw/opstellen/<name>/<place_id>/<types>/<opening>/<price_level>')
@role_required('Administrator')
def createnew(name, place_id, types, opening, price_level):
    typeslist = ast.literal_eval(types)
    recommendations = Recommendation.query.all()
    possibleDoubles = []
    for double in recommendations:
        if similar(name, double.name) >= 0.6 and double.place_id != place_id:
            possibleDoubles.append(double)
    return render_template("createnew.html", name=name, place_id=place_id, types=typeslist, API_TYPES=API_TYPES, TYPES_DICT=TYPES_DICT, opening=opening, price_level=price_level, possibleDoubles=possibleDoubles)

@app.route('/dashboard/nieuw/evenement/<name>/<place_id>', methods=["GET", "POST"])
@role_required('Administrator')
def create_event(name, place_id):
    if request.method == "GET":
        return render_template("createevent.html", name=name, place_id=place_id)

    # get event info and check input
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

    # create event
    event = Event(title=title, date=datetime_object, description=description, place_id=place_id, name=name)
    db.session.add(event)
    db.session.commit()
    flash("Evenement geplaatst", 'success' )
    return redirect(url_for("location", name=request.form.get("name"), place_id=request.form.get("place_id")))

@app.route('/dashboard/nieuwsbrief', methods=['GET', 'POST'])
@role_required('Administrator')
def newsletter():
    if request.method == "GET":
        # get all newsletters
        newsletters = Newsletter.query.all()
        return render_template("newsletter.html", newsletters=newsletters)

    # create new newsletter
    newsletter = Newsletter(date=datetime.datetime.now(), subject="", body="", send=False)
    db.session.add(newsletter)
    db.session.commit()
    return redirect(url_for('createnewsletter', newsletter_id=newsletter.id))

@app.route('/dashboard/nieuwsbrief/opstellen/<newsletter_id>', methods=["GET", "POST"])
@role_required('Administrator')
def createnewsletter(newsletter_id):
    # get newsletter to change
    newsletter = Newsletter.query.filter_by(id=newsletter_id).first()

    if request.method == "GET":
        return render_template("createnewsletter.html", newsletter=newsletter)

    # get textarea info
    action = request.form.get("action")
    body = request.form.get("editor1")
    subject=request.form.get("subject")

    # set newsletter variables and save in database
    newsletter.subject = subject
    newsletter.body = body
    db.session.commit()

    # check action and act accordingly
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

@app.route('/dashboard/blog', methods=['GET', 'POST'])
@role_required('Administrator')
def blog():
    if request.method == 'GET':

        # get all blogposts
        blogposts = Blog.query.all()
        return render_template("blog.html", blogposts=blogposts)

    blogpost = Blog(date=datetime.datetime.now(), title="", short="", body="", visible=False)
    db.session.add(blogpost)
    db.session.commit()
    return redirect(url_for('createblog', blog_id=blogpost.id))

@app.route('/dashboard/blog/opstellen/<blog_id>', methods=['GET', 'POST'])
@role_required('Administrator')
def createblog(blog_id):

    # get blogpost to change
    blogpost = Blog.query.filter_by(id=blog_id).first()
    if request.method == "GET":
        return render_template("createblog.html", blogpost=blogpost)

    # get form info
    action = request.form.get('action')
    title = request.form.get('title')
    short = request.form.get('short')
    body = request.form.get('editor1')

    # set blogpost variables and save in database
    blogpost.title = title
    blogpost.short = short
    blogpost.body = body
    db.session.commit()

    # check action and act accordingly
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

@app.route('/dashboard/checkreviews', methods=["GET", "POST"])
@role_required('Administrator')
def check():

    # get all reviews
    reviews = Review.query.all()

    if request.method == "GET":
        return render_template("check.html", reviews=reviews)

    # get action and review_id
    action = request.form.get('action')
    review_id = request.form.get('review_id')

    # look up review in database
    review = Review.query.filter_by(id=review_id).first()

    # check action and act accordingly
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

@app.route('/dashboard/uitgelicht', methods=["GET", "POST"])
@role_required('Administrator')
def highlight():
    if request.method == "GET":

        # get all highlights
        highlights = Highlight.query.all()
        return render_template('highlight.html', highlights=highlights)

    # set highlight variables and save in database
    place_id = request.form.get('place_id')
    name = request.form.get('name')
    previous = Highlight.query.order_by(Highlight.id.desc()).first()
    date = previous.week + datetime.timedelta(days=7)
    highlight = Highlight(place_id=place_id, name=name, week=date, description="")
    db.session.add(highlight)
    db.session.commit()
    return redirect(url_for('createhighlight', highlight_id=highlight.id))

@app.route('/dashboard/uitgelicht/wijzigen/<highlight_id>', methods=["GET", "POST"])
@role_required('Administrator')
def createhighlight(highlight_id):

    # get highlight to change
    highlight = Highlight.query.filter_by(id=highlight_id).first()
    if request.method == "GET":
        return render_template('createhighlight.html', highlight=highlight)

    # get form info
    action = request.form.get('action')
    description = request.form.get('editor1')

    # set highlight variables
    highlight.description = description
    db.session.commit()

    # check action and act accordingly
    if action == "save":
        flash("Wijzigingen opgeslagen", 'success')
        return redirect(url_for('createhighlight', highlight_id=highlight.id))
    if action == "delete":
        db.session.delete(highlight)
        db.session.commit()
        flash("Uitgelicht verwijderd", "success")
        return redirect(url_for('highlight'))
    if action == "preview":
        return render_template('guidepreview.html', highlight=highlight)

@app.route('/dashboard/aanvragen')
@role_required('Administrator')
def inforequest():

    # get all requests
    inforequests = Request.query.all()
    return render_template('requests.html', requests=inforequests)

@app.route('/dashboard/aanvragen/verwerken/<request_id>', methods=["GET", "POST"])
@role_required('Administrator')
def processrequests(request_id):

    # get request to process
    inforequest = Request.query.filter_by(id=request_id).first()

    if request.method == "GET":
        return render_template('processrequests.html', request=inforequest)

    # send request info to user via email and save that request is processed
    msg = Message(f"Meer informatie over {inforequest.name}", recipients=[inforequest.user.email])
    msg.html = render_template("requestmailbase.html", name=inforequest.user.firstname, body=request.form.get('editor1'))
    job = queue.enqueue('task.send_mail', msg)
    inforequest.processed = True
    db.session.commit()
    flash("Informatieaanvraag verwerkt", "success")
    return redirect(url_for('inforequest'))

@app.route('/<blog_id>/<title>', methods=["GET", "POST"])
def blogpost(blog_id, title):
    if request.method == "GET":
        # get blogpost and render
        blog = Blog.query.filter_by(id=blog_id).first()
        blogposts = Blog.query.filter(Blog.id != blog_id).filter(Blog.title!="Privacyverklaring").filter(Blog.title!="Over Stadsgids").order_by(Blog.date.desc()).all()
        comments = Comment.query.filter_by(blog_id=blog_id).all()
        return render_template('blogpost.html', blog=blog, blogposts=blogposts, comments=comments)

    # get form info
    comment = request.form.get('comment')

    comment = Comment(blog_id=blog_id, comment=comment)
    db.session.add(comment)
    db.session.commit()
    flash("Reactie geplaatst", "success")
    return redirect(url_for('blogpost', blog_id=blog_id, title=title))


@app.route('/over')
def aboutguide():

    # show about page (blogpost as about)
    blog = Blog.query.filter_by(id=9).first()
    return render_template('blogpost.html', blog=blog)
