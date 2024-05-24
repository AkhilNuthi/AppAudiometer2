from . import db
from flask_login import UserMixin
import mysql.connector

class Audiogram(db.Model):
    """A class representing an audiogram, which is a graphical representation of hearing thresholds
    in the frequencies 500 Hz to 8 kHz."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    l500 =db.Column(db.Integer)
    l1000 = db.Column(db.Integer)
    l2000 = db.Column(db.Integer)
    l3000 = db.Column(db.Integer)
    l4000 = db.Column(db.Integer)
    l6000 = db.Column(db.Integer)
    l8000 = db.Column(db.Integer)

class Mysql():
    def __init__(self):
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="fyp")
        self.cursor =  mydb.cursor()
        self.mydb = mydb

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    audiogram = db.relationship('Audiogram')

