from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    sex = db.Column(db.String(150))
    age = db.Column(db.Integer)
    type = db.Column(db.Integer)
    password = db.Column(db.String(150))
    occupation = db.Column(db.Integer)
    number_viewed = db.Column(db.Integer)
    viewed_movies = db.Column(db.String(1000))
    demographic_preferences = db.Column(db.String(150))
    #Colaborative
    colaborative_preferences = db.Column(db.String(150))
    number_col_g = db.Column(db.String(150))
    neighbor_number = db.Column(db.Integer)
    ids_neighbors = db.Column(db.String(300))
    neighbors_affinity = db.Column(db.String(300))

class UserType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(150))
    preferences = db.Column(db.String(150))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Integer)
    title = db.Column(db.String(150))
    genres = db.Column(db.String(300))

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer)
    movie = db.Column(db.Integer)
    val = db.Column(db.Integer)