from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column('id',db.Integer, primary_key=True)
    username = db.Column('username',db.String(80))
    email = db.Column('email',db.String(120))
    contact = db.Column('contact',db.String(120))
    address = db.Column('address',db.String(120))
    password = db.Column('password',db.String(80))
    latitude = db.Column('latitude',db.String(40))
    longitude = db.Column('longitude',db.String(40))
db.create_all()