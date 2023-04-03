import mysql.connector
import pyotp
from datetime import datetime,timedelta
from flask import jsonify,request,make_response
import jwt
import os
import itertools

class property_model():
    def __init__(self):
        try:
            self.con = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('USER_NAME'), password=os.getenv('PASSWORD'), database = os.getenv('DATABASE'))
            self.con.autocommit = True
            self.cur = self.con.cursor(dictionary=True)
            print("done")
        except:
            print("error")

    def property_details(self,id):
        self.cur.execute(f'''SELECT (SELECT image FROM tbl_property_image pi WHERE p.id = pi.property_id LIMIT 1) as property_image, p.price,p.address,p.bedrooms,p.bathrooms,p.parkings,p.property_type,p.area,p.area_type,p.description,p.latitude,p.longitude,u.first_name,u.last_name,u.profile_image,u.phone
                            FROM tbl_property p 
                            JOIN tbl_users u on p.user_id = u.id 
                            WHERE p.id = {id}''')
        res = self.cur.fetchall()
        self.cur.execute(f"SELECT image FROM tbl_property_image WHERE property_id={id}")
        res2 = self.cur.fetchall()
        property_details = dict(itertools.islice(res[0].items(),12))
        agent_details = dict(itertools.islice(res[0].items(),12,16))
        return make_response({"property_details":property_details,
                              "agent_details" :agent_details,
                              "property_images":[i['image'] for i in res2]
                              })

    def property_interest(self,id):
        self.cur.execute(f'''SELECT p.id,(SELECT pi.image FROM tbl_property_image pi WHERE pi.property_id = lp.property_id LIMIT 1) as property_image,p.price,p.address,u.profile_image as agent_image FROM tbl_like_property lp 
                                JOIN tbl_property p on lp.property_id = p.id 
                                JOIN tbl_users u on p.user_id = u.id
                                WHERE lp.user_id={id}''')
        res = self.cur.fetchall()
        return jsonify({"intrest":res})

    def property_probably_not(self,id):
        self.cur.execute(f'''SELECT p.id,(SELECT pi.image FROM tbl_property_image pi WHERE pi.property_id = lp.property_id LIMIT 1) as property_image,p.price,p.address,u.profile_image as agent_image FROM tbl_dislike_property lp 
                                        JOIN tbl_property p on lp.property_id = p.id 
                                        JOIN tbl_users u on p.user_id = u.id
                                        WHERE lp.user_id={id}''')
        res = self.cur.fetchall()
        return jsonify({"probably_not": res})

    def apply_filter(self,user_id,filter_id):
        self.cur.execute(f"SELECT filter_for,property_type,lowest_price,highest_price,min_bedrooms,min_parkings,min_land_size FROM tbl_search_filter WHERE id ={filter_id} and user_id={user_id}")
        res = self.cur.fetchall()
        if res[0]['filter_for'] == "Buy":
            res[0]['filter_for'] = "Sale"
        self.cur.execute(f'''SELECT p.id,u.profile_image as agent_image,(SELECT pi.image FROM tbl_property_image pi WHERE pi.property_id = p.id LIMIT 1) as property_image,u.phone,p.price,p.address,p.bedrooms,p.bathrooms,p.parkings,p.property_type,p.area 
                            FROM tbl_property p 
                            JOIN tbl_users u on p.user_id = u.id
                            WHERE p.property_for = '{res[0]['filter_for']}' and (p.price BETWEEN {res[0]['lowest_price']} and {res[0]['highest_price']}) and p.bedrooms >= {res[0]['min_bedrooms']} and p.parkings >= {res[0]['min_parkings']} and p.area >= {res[0]['min_land_size']}''')
        res1 = self.cur.fetchall()
        return make_response(res1)

    def add_filter(self,user_id,data):
        self.cur.execute(f'''insert  into tbl_search_filter (user_id,filter_for,property_type,lowest_price,highest_price,min_bedrooms,min_parkings,min_land_size,land_size_type) 
                                values ({user_id},'{data['filter_for']}','{data['property_type']}',{data['lowest_price']},{data['highest_price']},{data['min_bedrooms']},{data['min_parkings']},{data['min_land_size']},'{data['land_size_type']}')''')
        return jsonify({"message":"filter added"})

    def like_property(self,user_id,property_id):
        self.cur.execute(f"insert into tbl_like_property (user_id,property_id) values ({user_id},{property_id})")

        return jsonify({"message":"property_liked"})

    def dislike_property(self, user_id, property_id):
        self.cur.execute(f"insert into tbl_dislike_property (user_id,property_id) values ({user_id},{property_id})")

        return jsonify({"message": "property_disliked"})