import mysql.connector
import pyotp
from datetime import datetime,timedelta
from flask import jsonify,request,make_response
import jwt
import os
import itertools

class chat_model():
    def __init__(self):
        try:
            self.con = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('USER_NAME'), password=os.getenv('PASSWORD'), database = os.getenv('DATABASE'))
            self.con.autocommit = True
            self.cur = self.con.cursor(dictionary=True)
            print("done")
        except:
            print("error")

    def user_all_chat(self,user_id):
        self.cur.execute(f'''
                            SELECT c.property_id as property_id ,(SELECT pi.image FROM tbl_property_image pi WHERE pi.property_id = c.property_id LIMIT 1) as property_image, u.profile_image as agent_image, p.address , c.message, c.created_at
                            FROM tbl_chat c 
                            JOIN tbl_property p on c.property_id=p.id 
                            JOIN tbl_users u on p.user_id = u.id 
                            WHERE c.id in (SELECT max(id) FROM tbl_chat WHERE sender_id={user_id} or reciver_id={user_id} GROUP BY property_id)
                            ''')
        res = self.cur.fetchall()
        return jsonify({'data':res})

    def user_agent_chat(self,user_id,property_id):
        self.cur.execute(f'''SELECT concat(u.first_name,' ',u.last_name) as name, u.profile_image, p.address, u.phone 
                                FROM tbl_property p 
                                JOIN tbl_users u on p.user_id=u.id 
                                WHERE p.id={property_id}''')
        res1 = self.cur.fetchall()
        self.cur.execute(f'''SELECT c.*, CASE WHEN c.sender_id =1 THEN "right" ELSE "left" END as align
                                FROM `tbl_chat` c 
                                JOIN tbl_property p on c.property_id = p.id 
                                WHERE property_id = {property_id} and ((c.sender_id = {user_id} and c.reciver_id = p.user_id) or (c.sender_id = p.user_id and c.reciver_id = {user_id}))''')
        res = self.cur.fetchall()
        for j,i in enumerate(res):
            if i['message_type'] == 'meeting':
                print(i['message'])
                self.cur.execute(f'''select meeting_date,start_time,end_time,status from tbl_schedule_meeting where id = {i['message']}''')
                res2 = self.cur.fetchall()
                print(res2[0]['meeting_date'])
                res2[0]['meeting_date'] = res2[0]['meeting_date'].strftime('%d-%m-%Y')
                print(res2[0]['meeting_date'])
                res2[0]['start_time'] = str(res2[0]['start_time'])
                res2[0]['end_time'] = str(res2[0]['end_time'])



                res[j]  = res2[0]
        return jsonify({'head':res1[0],'data': res})

    def schedule_meeting(self,data,user_id,property_id):
        try:
            self.cur.execute(f'''insert into tbl_schedule_meeting (user_id,property_id,date,start_time,end_time) 
                                values ({user_id},{property_id},'{data['date']}','{data['start_time']}','{data['end_time']}')''')
            self.cur.execute(f'''SELECT user_id as agent_id FROM tbl_property where id={property_id}''')
            res = self.cur.fetchall()
            agent_id = res[0]['agent_id']
            self.cur.execute(f'''SELECT id FROM tbl_schedule_meeting 
                                WHERE user_id=1 and property_id=1 and status = 'pending' 
                                ORDER by id DESC LIMIT 1''')
            res = self.cur.fetchall()
            meeting_id = res[0]['id']
            self.cur.execute(f'''insert into tbl_chat (property_id,sender_id,reciver_id,message_type,message) 
                                values ({property_id},{user_id},{agent_id},'meeting','{meeting_id}')''')
            return jsonify({'message':'done'})
        except Exception as e:
            return jsonify({'error':e})