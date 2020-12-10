import os
import csv
from dotenv import load_dotenv
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
SQLALCHEMY_DATABASE_URI_PRIVATE = os.getenv("SQLALCHEMY_DATABASE_URI_PRIVATE")
app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
  app.debug = True
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI_PRIVATE
else:
  app.debug = False
  app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/

class Main_store(db.Model):
  __tablename__ = 'main_store'
  store_id = db.Column (db.Integer, primary_key = True)
  main_store = db.Column(db.String(50), unique = True)

  detail_store_relationship = db.relationship('Store', backref= 'main_store', lazy=True)
  post_relationship = db.relationship('Post', backref= 'main_store', lazy=True)
  def __init__(self, main_store):
    self.main_store = main_store

class Store(db.Model):
  __tablename__ = 'store'
  detail_store_id = db.Column (db.String(5), primary_key = True)
  store_id = db.Column (db.Integer, db.ForeignKey('main_store.store_id'), onupdate ='CASCADE')
  store = db.Column (db.String(50), nullable=False, unique = True)
  address = db.Column (db.String(200))
  discription = db.Column (db.String(500))
  open_time = db.Column (db.String(150))
  latitude = db.Column (db.Numeric(10,8))
  longtitute = db.Column (db.Numeric(10,7))
  map_review = db.Column (db.Text(), nullable=False)
  region = db.Column (db.String(1))
  province = db.Column (db.String(3))
  soup = db.Column (db.String(150))
  transport=  db.Column (db.String(50))

  def __init__(self, store_id, store, address, discription,\
     open_time, latitude, longtitute, map_review, region, soup, transport):
    self.store_id = store_id
    self.store = store
    self.address = address
    self.discription = discription
    self.open_time = open_time
    self.latitude = latitude
    self.longtitute = longtitute
    self.map_review = map_review
    self.region = region
    self.province = province
    self.soup = soup
    self.transport =transport

class Post(db.Model):
  __tablename__ = 'post'
  post_id = db.Column (db.Integer, primary_key = True)
  store_id = db.Column (db.Integer, db.ForeignKey('main_store.store_id', onupdate ='CASCADE'))
  create_on = db.Column (db.String(50))
  ramen_name = db.Column (db.String(50))
  fb_review = db.Column (db.Text(), nullable=False)

  def __init__(self, store_id, create_on, ramen_name, fb_review):
    self.store_id = store_id
    self.create_on = create_on
    self.ramen_name = ramen_name
    self.fb_review = fb_review

# Python3 #打開cmd輸入以下code
# from app import db (app is the file name)
# db.create_all() #https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
# exit()

#query
soup_q = Store.query.all()
raw_soup = [{soup.province:soup.soup} for soup in soup_q]
# print(raw_soup)

#https://www.geeksforgeeks.org/python-concatenate-values-with-same-keys-in-a-list-of-dictionaries/
#Concatenate values with same keys in a list of dictionaries
soup_data = dict()

def concate_dicts(l, lst):
  for dict in l:
    for list in dict:
      if list in lst:
        lst[list] += (dict[list])
      else:
        lst[list] = dict[list]
  return lst

def remove_duplicate(l):
  return list(dict.fromkeys(l))
#remove tags:
#ramentw
#台灣拉麵愛好會
#拉麵
#(u'\xa0', u' ')
concate_dicts(raw_soup, soup_data)
# print(soup_data)
for k, v in soup_data.items():
  organized_v = v.replace('#ramentw','').replace('#台灣拉麵愛好會','').replace('#拉麵','')\
            .replace(u'\xa0', u' ').replace(' ','').split('#')
  soup_data[k] = organized_v

for k, v in soup_data.items():
  no_duplicate_v  = remove_duplicate(v)
  no_duplicate_v.pop(0)
  soup_data[k] = no_duplicate_v

for k, v in soup_data.items():
  v_string = ' '.join([str(elem) for elem in v])
  soup_data[k] = v_string 
  print(k, v_string)
# print(soup_data)

with open('soup.csv', 'w', encoding='UTF-8') as f:
    for key in soup_data.keys():
        f.write("%s,%s\n"%(key,soup_data[key]))

if __name__ == 'main':
  app.run(debug=True)
