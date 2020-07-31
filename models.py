from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from functools import wraps
from flask_login import current_user, LoginManager
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for
import datetime
import time

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.String(128), nullable=False)
    lastname = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    register_date = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(128), nullable=False)
    newemail = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, nullable=False)
    email_confirmed_at = db.Column(db.DateTime(), nullable=True)
    newsletter = db.Column(db.Boolean, nullable=False)
    favourites = db.relationship('Favourite', cascade="all, delete-orphan")
    requests = db.relationship('Request', cascade="all, delete-orphan")
    reviews = db.relationship('Review', cascade="all, delete-orphan")
    roles = db.relationship('Role', secondary='user_roles')
    theme = db.Column(db.String(128), nullable=False)

    def __init__(self, username, firstname, lastname, password, email, newsletter):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.email = email
        self.newemail = None
        self.register_date = datetime.datetime.now()
        self.newsletter = True if newsletter else False
        self.confirmed = False
        self.active = False
        self.favourites = []
        self.requests = []
        self.reviews = []
        self.theme = "light"

    def get_user_roles(self):
        roles = []
        for role in self.roles:
            roles.append(role.name)
        return roles

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    place_id = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    review = db.Column(db.Text())
    tip = db.Column(db.Text())
    opening = db.Column(db.String())
    price_level = db.Column(db.Integer())
    visible = db.Column(db.Boolean(), nullable=False)

    def __init__(self, place_id, name, review, tip, opening, price_level, visible, type):
        self.place_id = place_id
        self.name = name
        self.date = datetime.datetime.now()
        self.review = review
        self.tip = tip
        self.opening = opening
        self.price_level = int(price_level)
        self.visible = visible
        self.type = type

class Favourite(db.Model):
    __tablename__ = 'favourites'
    id = db.Column(db.Integer(), primary_key=True)
    place_id = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, place_id, name):
        self.place_id = place_id
        self.name = name
        self.user_id = current_user.id

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    place_id = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    processed = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    user = db.relationship('User')

    def __init__(self, place_id, name):
        self.place_id = place_id
        self.user = current_user.id
        self.name = name
        self.processed = False
        self.date = datetime.datetime.now()
        self.user = current_user

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    blog_id = db.Column(db.Integer(), db.ForeignKey('blog.id', ondelete='CASCADE'), nullable=False)
    thread = db.Column(db.Integer(), db.ForeignKey('comments.id', ondelete='CASCADE'))
    date = db.Column(db.DateTime(), nullable=False)
    comment = db.Column(db.Text())
    user = db.relationship('User')
    checked = db.Column(db.Boolean, nullable=False)

    def __init__(self, blog_id, comment):
        self.blog_id = blog_id
        self.user_id = current_user.id
        self.date = datetime.datetime.now()
        self.user = current_user
        self.comment = comment
        self.checked = False

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    place_id = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    stars = db.Column(db.Integer(), nullable=False)
    review = db.Column(db.Text())
    checked = db.Column(db.Boolean, nullable=False)
    upvotes = db.relationship('Upvote', cascade="all, delete-orphan")
    user = db.relationship('User')

    def __init__(self, place_id, name, stars, review):
        self.place_id = place_id
        self.name = name
        self.user = current_user
        self.date = datetime.datetime.now()
        self.stars = stars
        self.review = review
        self.checked = False

    def get_upvote_count(self):
        count = 0
        for upvote in self.upvotes:
            count = count + 1
        return count

class Upvote(db.Model):
    __tablename__ = 'upvotes'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.Integer(), db.ForeignKey('reviews.id'), nullable=False)

    def __init__(self, review_id):
        self.review_id = review_id
        self.user_id = current_user.id

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer(), primary_key=True)
    place_id = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Highlight(db.Model):
    __tablename__ = 'highlights'
    id = db.Column(db.Integer(), primary_key=True)
    place_id = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    week = db.Column(db.DateTime(), nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    short = db.Column(db.Text(), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    visible = db.Column(db.Boolean, nullable=False)

class Newsletter(db.Model):
    __tablename__ = 'newsletters'
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), nullable=False)
    subject = db.Column(db.Text(), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    send = db.Column(db.Boolean, nullable=False)

class Hidden(db.Model):
    __tablename__ = 'hidden'
    id = db.Column(db.Integer(), primary_key=True)
    place_id = db.Column(db.String(128), nullable=False)

class AdminView(ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                if role.name == 'Administrator':
                    return True
            return False
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('guide'))
