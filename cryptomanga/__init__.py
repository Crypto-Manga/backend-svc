from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQL_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MONGO_URI"] = f"mongodb+srv://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@cluster0.xr9mv.mongodb.net/cm"
db = SQLAlchemy(app)
mongo = PyMongo(app)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
