from app import app
from model import user_model as um
from flask import request, jsonify
import os,jwt
from auth_user import token_required

obj = um.user_model()

@app.route("/register_user", methods=['POST'])
def register_user():
    return obj.register_user(request.form)


@app.route("/user_login",methods=['GET'])
def user():
    token = obj.user_login(request.form)
    return jsonify({"message":token})

@app.route("/after_login")
@token_required
def after_login(id):
    return jsonify({"user_id":id})

@app.route("/validate_phone_send_otp",methods=['GET','PATCH','POST'])
def validate_phone_send_otp():
    user_id = obj.validate_phone(request.form)
    if user_id:
        try:
            token = jwt.encode({'id': user_id}, os.getenv('SECRET_KEY'), algorithm='HS256')
        except:
            return jsonify({"error":"token not generated"})
        if token:
            otp = obj.generate_otp(user_id)
            if otp:
                return jsonify({"token":str(token)[2:-1],"otp":otp})
            else:
                return jsonify({"message": "otp not generated"})
        else:
            return jsonify({"message": "token not generated"})
    else:
        return jsonify({"message": "user_id not generated"})

@app.route("/verify_otp",methods=['GET'])
@token_required
def verify_otp(user_id):
    return obj.verify_otp(request.form,user_id)

@app.route("/reset_password",methods=['PATCH','GET'])
@token_required
def reset_password(user_id):
    return obj.reset_password(user_id,request.form)