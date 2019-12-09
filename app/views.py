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

# app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/ARPIT/projects/another/database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/ARPIT/projects/velway_project/database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'secret'
jwt = JWTManager(app)
app.config['JWT_TOKEN_LOCATION']= 'cookies'

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
#         if not token:
#             return jsonify({"message":"token is missing"}), 401
#         try:
#             data = jwt.decode(token, app.config["SECRET_KEY"])
#             current_user = Customer.query.filter_by(username=data['username']).first()
#         except:
#             return jsonify({"message":"token is invalid"}), 401
#         return f(current_user, *args, **kwargs)
#     return decorated

@app.template_filter("clean_date")
def clean_date(date):
    return date.strftime("%d %b %Y")

@app.route("/")
def index():
    # a = Customer.query.filter_by(username="arpit").first()
    # return "Hello "+ a.username
    return render_template("public/index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        req = request.values
        number = req["number"]
        if(int(len(number)) == 10):
            rand = random.randint(1000,9999)
            response = {"message":"Your OTP","otp":rand,"status":1}
            print(type(rand))

            return response
        else:
            error= {"message":"Invalid Number","status":0}
            return error
        # return render_template("public/register.html", rand=rand,number=number)
    return render_template("public/register.html")

@app.route("/sign_up", methods=["GET","POST"])
def sign_up():
    if request.method == "POST":
        # req = request.values
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
            print(user.contact)
        
        if not users:
            # return make_response('could not verify',401,{'www-authenticate':'basic realm="Login required"'})
            return jsonify({"message":"Contact number not found"})
        if check_password_hash(user.password,password):
            #token = jwt.encode({'username':user.username,'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)
            # return jsonify(access_token=access_token), 200
            resp = redirect(url_for('getdata'))

            set_access_cookies(resp, access_token)   #access cookie and verify jwt token
            set_refresh_cookies(resp, refresh_token)
            return resp
        return render_template("public/login.html")
    return render_template("public/login.html")
            # return jsonify(username=user.username,email=user.email,contact=user.contact,address=user.address,latitude=user.latitude,longitude=user.longitude,token=access_token,message="login success",status=1) #for postman use
        # return jsonify(message="wrong password") # for postman use

    # if request.method == "POST":
        # req = request.values
        # # req = request.form
        # contact = req["contact"]
        # password = req["password"]

@app.route("/getdata")
@jwt_required
def getdata():
    user = get_jwt_identity()
    print(user)
    users = Customer.query.filter_by(username=user).all()
    # users = Customer.query.all()
    for user in users: #for postman use
        return jsonify(username=user.username,contact=user.contact,email=user.email,address=user.address,latitude=user.latitude,longitude=user.longitude)
    # return jsonify(user)
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    print("hello")
    return jsonify(logged_in_as=current_user), 200

@app.route('/git')
@jwt_required
def git():
    current_user = get_jwt_identity()
    return render_template("public/git.html")
