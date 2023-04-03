import mysql.connector
import pyotp
from datetime import datetime,timedelta
from flask import jsonify,request
import jwt
import os
class user_model():
    def __init__(self):
        try:
            self.con = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('USER_NAME'), password=os.getenv('PASSWORD'), database = os.getenv('DATABASE'))
            self.con.autocommit = True
            self.cur = self.con.cursor(dictionary=True)
            print("done1")
        except:
            print("error")

    def register_user(self,data):
        self.cur.execute(f"insert into tbl_users (first_name,last_name,password,phone,role) values ('{data['first_name']}','{data['last_name']}','{data['password']}','{data['phone']}','{data['role']}')")
        return jsonify({"message":"user registered successfully"})

    def user_login(self,data):
        self.cur.execute(f"select id,first_name,last_name from tbl_users where phone='{data['phone']}' and password='{data['password']}'")
        res = self.cur.fetchall()
        return res[0]['id']

    def validate_phone(self,data):
        self.cur.execute(f"select id from tbl_users where phone='{data['phone']}'")
        res = self.cur.fetchall()
        return res[0]['id']

    def generate_otp(self,user_id):
        dt = datetime.now()
        exp_time = dt + timedelta(minutes=10)
        totp_secret = pyotp.random_base32()
        totp = pyotp.TOTP(totp_secret)
        otp = totp.now()
        # totp.verify(user_otp)
        self.cur.execute(f"INSERT INTO tbl_otp (user_id, otp, expire_time) VALUES ({user_id}, {otp}, {round(exp_time.timestamp())})")
        return otp

    def verify_otp(self,data,id):
        self.cur.execute(f"SELECT otp,expire_time FROM `tbl_otp` WHERE user_id={id} ORDER by id DESC LIMIT 1")
        res = self.cur.fetchall()
        print(res[0]['expire_time'],round(datetime.now().timestamp()))
        if int(res[0]['otp']) == int(data['otp']) and int(res[0]['expire_time']) > round(datetime.now().timestamp()):
            return jsonify({"message":"otp verified"})
        else:
            return jsonify({"message":"otp not verified or time expired"})




    def reset_password(self,user_id,data):
        if data['password'] == data['cpassword']:
            self.cur.execute(f"update tbl_users set password = '{data['password']}' where id = {user_id}")
            if self.cur.rowcount > 0:
                return jsonify({"message":"password updated successfully"})
            else:
                return jsonify({"message":"password is same as old password"})
        else:
            return jsonify({"message":"confirm password not matched"})

