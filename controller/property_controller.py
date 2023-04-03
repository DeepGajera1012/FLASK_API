from app import app
from model import property_model as pm
from flask import request,send_file,jsonify
import os
import jwt
from auth_user import token_required


obj = pm.property_model()

@app.route("/property_details/<id>",methods=['GET'])
@token_required
def property_details(user_id,id):
    return obj.property_details(id)

@app.route("/property/interst",methods=['GET'])
@token_required
def property_interest(user_id):
    return obj.property_interest(user_id)

@app.route("/property/probably_not",methods=['GET'])
@token_required
def property_probably_not(user_id):
    return obj.property_probably_not(user_id)

@app.route("/property/apply_filter/<filter_id>",methods=["GET"])
@token_required
def apply_filter(user_id,filter_id):
    return obj.apply_filter(user_id,filter_id)

@app.route("/property/add_filter",methods=['POST'])
@token_required
def add_filter(user_id):
    return obj.add_filter(user_id,request.form)

@app.route("/property/like/<property_id>",methods=['POST'])
@token_required
def like_property(user_id,property_id):
    return obj.like_property(user_id,property_id)

@app.route("/property/dislike/<property_id>",methods=['POST'])
@token_required
def dislike_property(user_id,property_id):
    return obj.dislike_property(user_id,property_id)
