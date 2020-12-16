import os
import csv
import secrets
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

ENV = 'prod'

if ENV == 'dev':
  from dotenv import load_dotenv
  load_dotenv()
  SQLALCHEMY_DATABASE_URI_PRIVATE = os.getenv("SQLALCHEMY_DATABASE_URI_PRIVATE")
  app.debug = True
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI_PRIVATE
else:
  DATABASE_URL = os.environ.get('DATABASE_URL')
  app.debug = False
  app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# # #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# #---------------------------------initialize tables--------------------------
class Main_store(db.Model):
  __tablename__ = 'main_store'
  store_id = db.Column (db.Integer, primary_key = True)
  main_store = db.Column(db.String(50), nullable=False, unique = True)

  detail_store_relationship = db.relationship('Store', backref= 'main_store', lazy=True)
  post_relationship = db.relationship('Post', backref= 'main_store', lazy=True)
  def __init__(self, main_store):
    self.main_store = main_store

class Store(db.Model):
  __tablename__ = 'store'
  detail_store_id = db.Column (db.String(10), primary_key = True)
  store_id = db.Column (db.Integer, db.ForeignKey('main_store.store_id'), nullable=False, onupdate ='CASCADE')
  store = db.Column (db.String(50), nullable=False, unique = True)
  still_there = db.Column (db.Boolean, nullable=False)
  address = db.Column (db.String(200))
  discription = db.Column (db.String(500))
  open_time = db.Column (db.String(200))
  latitude = db.Column (db.Numeric(10,8), nullable=False,)
  longtitute = db.Column (db.Numeric(11,8),  nullable=False)
  map_review = db.Column (db.Text())
  region = db.Column (db.String(1))
  province = db.Column (db.String(3))
  soup = db.Column (db.String(200))
  transport =  db.Column (db.String(100))

  store_favorite_relationship = db.relationship('Favorite', backref= 'store', lazy=True)

  def __init__(self, store_id, store, still_there, address, discription,\
     open_time, latitude, longtitute, map_review, region, province, soup, transport):
    self.store_id = store_id
    self.store = store
    self.still_there = still_there
    self.address = address
    self.discription = discription
    self.open_time = open_time
    self.latitude = latitude
    self.longtitute = longtitute
    self.map_review = map_review
    self.region = region
    self.province = province
    self.soup = soup
    self.transport = transport

class Post(db.Model):
  __tablename__ = 'post'
  post_id = db.Column (db.String(10), primary_key = True)
  store_id = db.Column (db.Integer, db.ForeignKey('main_store.store_id'), nullable=False, onupdate ='CASCADE')
  stores = db.Column (db.String(30))
  create_on = db.Column (db.DateTime)
  ramen_name = db.Column (db.String(100))
  fb_review = db.Column (db.Text())

  post_favorite_relationship = db.relationship('Favorite', backref= 'post', lazy=True)

  def __init__(self, store_id, stores, create_on, ramen_name, fb_review):
    self.store_id = store_id
    self.stores = stores
    self.create_on = create_on
    self.ramen_name = ramen_name
    self.fb_review = fb_review

class Favorite(db.Model):
  __tablename__ = 'favorite'
  favorite_id = db.Column (db.String(10), primary_key = True)
  detail_store_id = db.Column (db.String(10), db.ForeignKey('store.detail_store_id'), nullable=False, onupdate ='CASCADE')
  post_id = db.Column (db.String(10), db.ForeignKey('post.post_id'), nullable=False, onupdate ='CASCADE')
  line_id = db.Column (db.String(20),nullable=False)

  def __init__(self, detail_store_id, post_id, line_id):
    self.detail_store_id = detail_store_id
    self.post_id= post_id
    self.line_id = line_id






## Python3 #打開cmd輸入以下code
# from app import db (app is the file name)
# db.create_all() #https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
# exit()

## query
# .filter(Store.soup.contains('二郎風'))
# .add_columns(Store.soup, Store.province, Store.store, Store.address,\
#                           Store.discription, Store.open_time, Store.transport,\
#                           Post.create_on, Post.ramen_name, Post.fb_review)\
# print(province_soup_q) #(<Main_store 0>, <Store 2223>, <Post 3331>)

## query
# def query_province_soup(p, s):
#   province_soup_q = db.session.query(Main_store, Store, Post)\
#                       .outerjoin(Post, Post.store_id == Main_store.store_id)\
#                       .outerjoin(Store, Store.store_id == Main_store.store_id)\
#                       .filter(Store.province == p)\
#                       .filter(Store.soup.contains(s))\
#                       .filter(Store.still_there == True)
#   return province_soup_q
# def query_province_direct(p):
#   province_soup_q = db.session.query(Main_store, Store, Post)\
#                       .outerjoin(Post, Post.store_id == Main_store.store_id)\
#                       .outerjoin(Store, Store.store_id == Main_store.store_id)\
#                       .filter(Store.province == p)\
#                       .filter(Store.still_there == True)
#   return province_soup_q
# def convert_string_to_lst(string,c): 
#     li = list(string.split(c)) 
#     return li 

# city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市"\
#             ,"台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]
# user_select = '直接推薦:苗栗縣'
# #---------------------------------query 直接推薦、湯頭推薦、看更多類似推薦--------------------------
# if ':' in user_select:
#   select_first_param = user_select[:user_select.index(':')]
#   select_second_param = user_select[user_select.index(':')+1:]
#   # print(select_second_param)
#   if (select_first_param == '直接推薦') or (select_first_param == '看更多推薦'):
#     #query withOUT soup
#     result = query_province_direct(select_second_param)
#     # print(type(result))
#     #random here
  
#   elif select_first_param in city_name:
#     #query with soup
#     result = query_province_soup(select_first_param, select_second_param)
#     # print(type(result))
#     #random here
# #---------------------------------put all data in a string--------------------------
# ouput_database_fb = ''
# ouput_database_map = ''
# output_before_random = ''
# for r in result:
#   try:
#     ouput_database_fb += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
#         FB_R_CREATE:{r[2].create_on},FB_R_RAMEN:{r[2].ramen_name},FB_R_CONTENT:{r[2].fb_review},\
#         CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
#     # print('PROVINCE:{} STORE:{} ADDRESS:{} SOUP:{} MAP:{} \
#     #   create_on:{} ramen_name:{} FB:{} '\
#     #   .format(r[1].province, r[1].store, r[1].address, r[1].soup,r[1].map_review,\
#     #     r[2].create_on,r[2].ramen_name, r[2].fb_review))
#   except AttributeError as error:
#     ouput_database_map += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
#         MAP_REVIEW:{r[1].map_review},\
#         CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
  
#     # print('STORE:{} SOUP:{} MAP:{}'.format(r[1].store, r[1].soup, r[1].map_review))

# # print(ouput_database_fb)
# # print(ouput_database_map)
# output_before_random += ouput_database_fb
# output_before_random += ouput_database_map
# output_before_random_clear = output_before_random.replace(u'\xa0', u' ').replace(' ','')
# # print(output_before_random)
# #---------------------------------change data to a list of datas--------------------------
# output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
# for data in output_whole_lst:
#   if data == '':
#     output_whole_lst.remove(data)
# # print(output_whole_lst)
# #---------------------------------random(everytime renew can auto random)--------------------------
# output_s = secrets.choice(output_whole_lst)
# output_lst = convert_string_to_lst(output_s, ',')
# print(output_lst)




# #soup query
# soup_q = Store.query.all()
# print(soup_q)
# raw_soup = [{soup.province:soup.soup} for soup in soup_q]
# print(raw_soup)

# #https://www.geeksforgeeks.org/python-concatenate-values-with-same-keys-in-a-list-of-dictionaries/
# #Concatenate values with same keys in a list of dictionaries
# soup_data = dict()

# def concate_dicts(l, lst):
#   for dict in l:
#     for list in dict:
#       if list in lst:
#         lst[list] += (dict[list])
#       else:
#         lst[list] = dict[list]
#   return lst

# def remove_duplicate(l):
#   return list(dict.fromkeys(l))
# #remove tags:
# #ramentw
# #台灣拉麵愛好會
# #拉麵
# #(u'\xa0', u' ')
# concate_dicts(raw_soup, soup_data)
# # print(soup_data)
# for k, v in soup_data.items():
#   organized_v = v.replace('#ramentw','').replace('#台灣拉麵愛好會','').replace('#拉麵','')\
#             .replace(u'\xa0', u' ').replace(' ','').split('#')
#   soup_data[k] = organized_v

# for k, v in soup_data.items():
#   no_duplicate_v  = remove_duplicate(v)
#   no_duplicate_v.pop(0)
#   soup_data[k] = no_duplicate_v

# for k, v in soup_data.items():
#   v_string = ' '.join([str(elem) for elem in v])
#   soup_data[k] = v_string 
#   print(k, v_string)
# # print(soup_data)

# with open('soup.csv', 'w', encoding='UTF-8') as f:
#     for key in soup_data.keys():
#         f.write("%s,%s\n"%(key,soup_data[key]))

if __name__ == 'main':
  app.run(debug=True)
