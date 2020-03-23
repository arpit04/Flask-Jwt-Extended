from app import app
from flask import Flask, render_template, request, redirect, make_response,jsonify, send_from_directory, abort, url_for
import datetime
import os
import jwt
from werkzeug.utils import secure_filename
import random
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app.alchemy import Customer
from functools import wraps
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, set_access_cookies, jwt_refresh_token_required,
    get_jwt_identity, create_refresh_token, set_refresh_cookies, unset_jwt_cookies
)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'
jwt = JWTManager(app)
app.config['JWT_TOKEN_LOCATION']= 'cookies'

@app.template_filter("clean_date")
def clean_date(date):
    return date.strftime("%d %b %Y")

@app.route("/")
def index():
    return render_template("public/index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        req = request.values
        number = req["number"]
        if(int(len(number)) == 10):
            rand = random.randint(1000,9999)
            response = {"message":"Your OTP","otp":rand,"status":1}
            return response
        else:
            error= {"message":"Invalid Number","status":0}
            return error
    return render_template("public/register.html")

@app.route("/sign_up", methods=["GET","POST"])
def sign_up():
    if request.method == "POST":
        req = request.form
        username = req["username"]
        email = req["email"]
        contact = req["contact"]
        address = req["address"]
        password = generate_password_hash(req["password"],method='sha256')
        latitude = req["latitude"]
        longitude = req["longitude"]
            
        result = Customer(username=username,email=email,contact=contact,address=address,
                            password=password,latitude=latitude,longitude=longitude)
        db.session.add(result)
        db.session.commit()
        response = {"message":"sign_up success","status":1}
        return response
    return render_template("public/sign_up.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        req = request.values
        contact = req["contact"]
        password = req["password"]
        users = Customer.query.filter_by(contact=req["contact"]).all()
        for user in users:
            pass # user.contact
        
        if not users:
            return jsonify({"message":"Contact number not found"})
        if check_password_hash(user.password,password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)
            resp = redirect(url_for('git'))

            set_access_cookies(resp, access_token)   #access cookie and verify jwt token
            set_refresh_cookies(resp, refresh_token)
            return resp
        return render_template("public/login.html")
    return render_template("public/login.html")

@app.route("/getdata")
@jwt_required
def getdata():
    user = get_jwt_identity()
    users = Customer.query.filter_by(username=user).all()
    for user in users: #for postman use
        return jsonify(username=user.username,contact=user.contact,email=user.email,address=user.address,latitude=user.latitude,longitude=user.longitude)

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/git')
@jwt_required
def git():
    current_user = get_jwt_identity()
    return render_template("public/git.html",current_user=current_user)