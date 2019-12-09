from flask import Flask

app = Flask(__name__)
key = 'secret'

from app import alchemy
from app import views
from app import admin_views