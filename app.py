from flask import Flask

app = Flask(__name__)
from controller import *
@app.route("/")
def welcome():
    return "welcome1"

# $env:FLASK_ENV = "development"
