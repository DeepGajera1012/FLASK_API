from app import app
from model import chat_model as cm
from flask import request,send_file,jsonify
import os
import jwt
from auth_user import token_required

obj = cm.chat_model()

@app.route("/user/all_chats",methods=['GET'])
@token_required
def user_chat(user_id):
    return obj.user_all_chat(user_id)

@app.route("/user/agent/chat",methods=['GET'])
@token_required
def user_agent_chat(user_id):
    return obj.user_agent_chat(user_id,request.headers.get('property_id'))

@app.route("/user/schedule_meeting",methods=['GET','POST'])
@token_required
def schedule_meeting(user_id):
    return obj.schedule_meeting(request.form,user_id,request.headers.get('property_id'))