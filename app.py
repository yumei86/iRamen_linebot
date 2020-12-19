from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json
import os

from flask_sqlalchemy import SQLAlchemy
import secrets
import csv

#----------------呼叫我們的line bot(這邊直接取用heroku的環境變數)-----------------

app = Flask(__name__)

USER = os.environ.get('CHANNEL_ACCESS_TOKEN')
PASS = os.environ.get('CHANNEL_SECRET')

line_bot_api = LineBotApi(USER)
handler = WebhookHandler(PASS)

#----------------資料庫設定-----------------

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
  latitude = db.Column (db.Numeric(10,8))
  longtitute = db.Column (db.Numeric(10,7))
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

def query_province_soup(p, s):
    province_soup_q = db.session.query(Main_store, Store, Post)\
                        .outerjoin(Post, Post.store_id == Main_store.store_id)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.province == p)\
                        .filter(Store.soup.contains(s))\
                        .filter(Store.still_there == True)
    return province_soup_q

def query_province_direct(p):
    province_soup_q = db.session.query(Main_store, Store, Post)\
                        .outerjoin(Post, Post.store_id == Main_store.store_id)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.province == p)\
                        .filter(Store.still_there == True)
    return province_soup_q

def convert_string_to_lst(string,c): 
    li = list(string.split(c)) 
    return li 


#----------------官方設定-----------------

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
       abort(400)

    return 'OK'

#----------------設定回覆訊息介面-----------------

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    msg = msg.encode('utf-8')  

    if event.message.text == "問題回報":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "ooops...\uDBC0\uDC17 \n請點選以下連結回報問題：https://reurl.cc/14RmVW"))


#----------------拉麵推薦介面-----------------

    #讀需要的json資料
    f = open('json_files_for_robot/json_for_app.json') 
    data = json.load(f) 
    

    if event.message.text == "拉麵推薦":

        flex_message = FlexSendMessage(
                        alt_text='拉麵推薦',
                        contents= data[0]
        )

        line_bot_api.reply_message(event.reply_token,flex_message)

#----------------不同區域的介面設定-----------------

    TWregion = ["北部","中部","南部","東部"]
    times = 1

    for item in TWregion:
        if event.message.text == item:
            flex_message1 = FlexSendMessage(
                           alt_text= item+'的縣市',
                           contents=  data[times]
            )
        
            line_bot_api.reply_message(event.reply_token,flex_message1) 
        times += 1

    
    f.close()

#----------------選擇湯頭/直接推薦介面-----------------

    city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]

    for city in city_name:
        if event.message.text == city:
            flex_message5 = FlexSendMessage(
                        alt_text='依據你的喜好選擇吧！',
                        contents= 
                                    {
                                        "type": "bubble",
                                        "body": {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                            "type": "text",
                                            "text": "推薦方式 ",
                                            "weight": "bold",
                                            "size": "xl",
                                            "style": "normal",
                                            "decoration": "none",
                                            "align": "start",
                                            "gravity": "top",
                                            "color": "#876C5A",
                                            "position": "relative"
                                            },
                                            {
                                            "type": "box",
                                            "layout": "vertical",
                                            "margin": "lg",
                                            "spacing": "sm",
                                            "contents": [
                                                {
                                                "type": "text",
                                                "text": "我有口味偏好 -> 請選湯頭推薦",
                                                "size": "sm"
                                                },
                                                {
                                                "type": "text",
                                                "text": "我想來點驚喜 -> 請選直接推薦",
                                                "size": "sm"
                                                },
                                                {
                                                "type": "separator",
                                                "margin": "lg"
                                                }
                                            ]
                                            }
                                        ]
                                        },
                                        "footer": {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                            {
                                            "type": "button",
                                            "style": "primary",
                                            "height": "sm",
                                            "action": {
                                                "type": "message",
                                                "label": "湯頭推薦",
                                                "text": "湯頭推薦:"+city
                                            },
                                            "color": "#797D62",
                                            "margin": "md",
                                            "offsetTop": "none",
                                            "offsetBottom": "none",
                                            "offsetStart": "none",
                                            "offsetEnd": "none",
                                            "gravity": "center"
                                            },
                                            {
                                            "type": "button",
                                            "style": "primary",
                                            "height": "sm",
                                            "action": {
                                                "type": "message",
                                                "label": "直接推薦",
                                                "text": "直接推薦:"+city
                                            },
                                            "color": "#797D62",
                                            "margin": "md"
                                            },
                                            {
                                            "type": "spacer",
                                            "size": "sm"
                                            }
                                        ]
                                        }
                                    }
        )
        
            line_bot_api.reply_message(event.reply_token,flex_message5) 
    
    if event.message.text == "嘉義縣":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "抱歉！\uDBC0\uDC7c 這邊尚未有拉麵店，請至附近其他縣市看看!"))

#----------------湯頭推薦-----------------

    #分成四區去叫不同的json檔（為了整理方便分成四區）

    n_city = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市"]
    c_city = ["台中市","彰化縣","南投縣","雲林縣"]
    s_city = ["嘉義市","台南市","高雄市","屏東縣"]
    e_city = ["宜蘭縣","花蓮縣","台東縣"]

    all_city = [n_city,c_city,s_city,e_city]
    region = ["north","center","south","east"]

    #用迴圈去讀湯頭選單
    #讀需要的推薦介面json資料
    for i in range(len(region)):
        f = open('json_files_for_robot/soup_'+region[i]+'_city.json') 
        data = json.load(f) 
        city_cond = all_city[i]
        count = 0

        for name in city_cond:
            cond = "湯頭推薦:"+name
            if event.message.text == cond :
                flex_message2 = FlexSendMessage(
                            alt_text='快回來看看我幫你找到的湯頭！',
                            contents= data[count]
                )
    
                line_bot_api.reply_message(event.reply_token,flex_message2)
            count += 1

        f.close()

#----------------直接推薦/縣市看更多類似推薦-----------------
    

    for city in city_name:

        cond = "直接推薦:"+city
        more = "看更多推薦:"+city

        #---------------------------query 直接推薦、湯頭推薦、看更多類似推薦--------------------------
        if ':' in cond:
            select_first_param = cond[:cond.index(':')]
            select_second_param = cond[cond.index(':')+1:]
            
            if (select_first_param == '直接推薦') or (select_first_param == '看更多推薦'):                
                result = query_province_direct(select_second_param)
                        
            elif select_first_param in city_name:
                result = query_province_soup(select_first_param, select_second_param)
                   
        #---------------------------put all data in a string--------------------------
        ouput_database_fb = ''
        ouput_database_map = ''
        output_before_random = ''
        for r in result:
            try:
                ouput_database_fb += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                    FB_R_CREATE:{r[2].create_on},FB_R_RAMEN:{r[2].ramen_name},FB_R_CONTENT:{r[2].fb_review},\
                    LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},\
                    CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'

            except AttributeError:
                ouput_database_map += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                    MAP_REVIEW:{r[1].map_review},\
                    LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},\
                    CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
                

        output_before_random += ouput_database_fb
        output_before_random += ouput_database_map
        output_before_random_clear = output_before_random.replace(u'\xa0', u' ').replace(' ','')
               
        #---------------------------------change data to a list of datas--------------------------
        output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
        for data in output_whole_lst:
            if data == '':
                output_whole_lst.remove(data)
        #---------------------------------random(everytime renew can auto random)--------------------------
        output_s = secrets.choice(output_whole_lst)
        output_lst = convert_string_to_lst(output_s, ',')
        
        store_n = output_lst[0][output_lst[0].index(':')+1:]
        address = output_lst[1][output_lst[1].index(':')+1:]
        descrip = output_lst[2][output_lst[2].index(':')+1:]
        trans = output_lst[3][output_lst[3].index(':')+1:]
        
        if len(output_lst) == 11:
            #FB評論
            c1 = output_lst[4][output_lst[4].index(':')+1:]
            c2 = output_lst[5][output_lst[5].index(':')+1:]
            c3 = output_lst[6][output_lst[6].index(':')+1:]
            comment = f'貼文時間：\n{c1}\n品項：\n{c2}\n評論：\n{c3}'
            lon = output_lst[7][output_lst[7].index(':')+1:]
            lat = output_lst[8][output_lst[8].index(':')+1:]

        elif len(output_lst) == 9:
            #googleMap
            comment = output_lst[4][output_lst[4].index(':')+1:]
            lon = output_lst[5][output_lst[5].index(':')+1:]
            lat = output_lst[6][output_lst[6].index(':')+1:]  


        if event.message.text == cond :

            flex_message3 = FlexSendMessage(
                            alt_text='快回來看看我幫你找到的店家！',
                            contents= {
                                        "type": "carousel",
                                        "contents": [
                                            {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "text",
                                                    "text": store_n,
                                                    "align": "start",
                                                    "size": "md",
                                                    "gravity": "center",
                                                    "color": "#ffffff",
                                                    "wrap": True
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [],
                                                    "width": "80px",
                                                    "height": "20px"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "+到最愛",
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單:"+store_n
                                                        }
                                                    }
                                                    ],
                                                    "width": "60px",
                                                    "height": "25px",
                                                    "backgroundColor": "#FFCB69",
                                                    "cornerRadius": "20px",
                                                    "position": "absolute",
                                                    "offsetEnd": "xxl",
                                                    "offsetTop": "lg"
                                                }
                                                ],
                                                "paddingTop": "15px",
                                                "paddingAll": "15px",
                                                "paddingBottom": "16px",
                                                "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "地址：",
                                                        "color": "#797D62",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "↓↓點擊下方地址可以直接幫你傳送位置噢！",
                                                        "color": "#CA8E68",
                                                        "size": "xs",
                                                        "wrap": True,
                                                        "weight": "regular"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": address,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": "正在幫你找到:"+lon+":"+lat
                                                    },
                                                    "margin": "md"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "lg"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "特色：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": descrip,
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "margin": "md"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "lg"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "鄰近交通資訊：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "text": trans,
                                                        "margin": "md"
                                                    }
                                                    ],
                                                    "paddingBottom": "18px"
                                                }
                                                ],
                                                "spacing": "md",
                                                "paddingAll": "12px"
                                            },
                                            "footer": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city
                                                    },
                                                    "color": "#D08C60"
                                                }
                                                ]
                                            },
                                            "styles": {
                                                "footer": {
                                                "separator": False
                                                }
                                            }
                                            },
                                            {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "text",
                                                    "text": store_n,
                                                    "align": "start",
                                                    "size": "md",
                                                    "gravity": "center",
                                                    "color": "#ffffff",
                                                    "wrap": True
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [],
                                                    "width": "80px",
                                                    "height": "20px"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "+到最愛",
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單:"+store_n
                                                        }
                                                    }
                                                    ],
                                                    "width": "60px",
                                                    "height": "25px",
                                                    "backgroundColor": "#FFCB69",
                                                    "cornerRadius": "20px",
                                                    "position": "absolute",
                                                    "offsetEnd": "xxl",
                                                    "offsetTop": "lg"
                                                }
                                                ],
                                                "paddingTop": "15px",
                                                "paddingAll": "15px",
                                                "paddingBottom": "16px",
                                                "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "網友評論：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "margin": "md",
                                                        "text": comment
                                                    }
                                                    ],
                                                    "paddingBottom": "18px"
                                                }
                                                ],
                                                "spacing": "md",
                                                "paddingAll": "12px"
                                            },
                                            "footer": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city
                                                    },
                                                    "color": "#D08C60"
                                                }
                                                ]
                                            },
                                            "styles": {
                                                "footer": {
                                                "separator": False
                                                }
                                            }
                                            }
                                        ]
                                        }

            )

            line_bot_api.reply_message(event.reply_token,flex_message3)


        if event.message.text == more :

            flex_message4 = FlexSendMessage(
                            alt_text='快回來看看我幫你找到的店家！',
                            contents= {
                                        "type": "carousel",
                                        "contents": [
                                            {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "text",
                                                    "text": store_n,
                                                    "align": "start",
                                                    "size": "md",
                                                    "gravity": "center",
                                                    "color": "#ffffff",
                                                    "wrap": True
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [],
                                                    "width": "80px",
                                                    "height": "20px"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "+到最愛",
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單:"+store_n
                                                        }
                                                    }
                                                    ],
                                                    "width": "60px",
                                                    "height": "25px",
                                                    "backgroundColor": "#FFCB69",
                                                    "cornerRadius": "20px",
                                                    "position": "absolute",
                                                    "offsetEnd": "xxl",
                                                    "offsetTop": "lg"
                                                }
                                                ],
                                                "paddingTop": "15px",
                                                "paddingAll": "15px",
                                                "paddingBottom": "16px",
                                                "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "地址：",
                                                        "color": "#797D62",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "↓↓點擊下方地址可以直接幫你傳送位置噢！",
                                                        "color": "#CA8E68",
                                                        "size": "xs",
                                                        "wrap": True,
                                                        "weight": "regular"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": address,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": address
                                                    },
                                                    "margin": "md"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "lg"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "特色：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": descrip,
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "margin": "md"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "lg"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "鄰近交通資訊：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "text": trans,
                                                        "margin": "md"
                                                    }
                                                    ],
                                                    "paddingBottom": "18px"
                                                }
                                                ],
                                                "spacing": "md",
                                                "paddingAll": "12px"
                                            },
                                            "footer": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city
                                                    },
                                                    "color": "#D08C60"
                                                }
                                                ]
                                            },
                                            "styles": {
                                                "footer": {
                                                "separator": False
                                                }
                                            }
                                            },
                                            {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "text",
                                                    "text": store_n,
                                                    "align": "start",
                                                    "size": "md",
                                                    "gravity": "center",
                                                    "color": "#ffffff",
                                                    "wrap": True
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [],
                                                    "width": "80px",
                                                    "height": "20px"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "+到最愛",
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單:"+store_n
                                                        }
                                                    }
                                                    ],
                                                    "width": "60px",
                                                    "height": "25px",
                                                    "backgroundColor": "#FFCB69",
                                                    "cornerRadius": "20px",
                                                    "position": "absolute",
                                                    "offsetEnd": "xxl",
                                                    "offsetTop": "lg"
                                                }
                                                ],
                                                "paddingTop": "15px",
                                                "paddingAll": "15px",
                                                "paddingBottom": "16px",
                                                "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "網友評論：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "margin": "md",
                                                        "text": comment
                                                    }
                                                    ],
                                                    "paddingBottom": "18px"
                                                }
                                                ],
                                                "spacing": "md",
                                                "paddingAll": "12px"
                                            },
                                            "footer": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city
                                                    },
                                                    "color": "#D08C60"
                                                }
                                                ]
                                            },
                                            "styles": {
                                                "footer": {
                                                "separator": False
                                                }
                                            }
                                            }
                                        ]
                                        }

            )

            line_bot_api.reply_message(event.reply_token,flex_message4)

#----------------位置經緯度資訊-----------------
    if "正在幫你找到" in event.message.text:

        #line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "測試"))


        text_list = event.message.text.split(":")
        lonti = float(text_list[1])
        lati  = float(text_list[2])
        line_bot_api.reply_message(event.reply_token,LocationSendMessage(title='點擊帶你前往！', address='', latitude=lati, longitude=lonti))
    

        #location_message = LocationSendMessage(
        #                title= 'location',
        ##                address= '請點擊畫面跳轉google map!',
         #               latitude= lonti,
         #               longitude= lati
         #                   )
        #line_bot_api.reply_message(event.reply_token,location_message)

#----------------選完湯頭介面/湯頭看更多類似推薦-----------------

    #各縣市湯頭清單
    #北部
    taipei = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "雞豚", "淡麗系", "其他"]
    new_taipei = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "淡麗系", "煮干", "素食"]
    keelung = ["豚骨", "素食"]
    taoyuan = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "柑橘", "淡麗", "煮干", "大骨"]
    miaoli = ["豚骨", "咖哩"]
    hsinchu_county = ["豚骨"]
    hsinchu_city = ["豚骨", "醬油", "魚介", "雞清", "素食", "背脂", "淡麗系"]

    #中部
    taichung = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "雞豚", "味噌", "其他"]
    chuanghua = ["豚骨", "雞白", "家系"]
    nantou = ["豚骨"]
    #到雲林豚骨有bug
    yunlin = ["雞白", "魚介"]

    #南部
    chiayi = ["豚骨", "沾麵", "家系"]
    tainan = ["豚骨", "雞白", "魚介", "沾麵", "雞清", "雞豚", "咖哩", "淡麗系", "煮干", "其他"]
    kaohsiung = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "雞豚", "淡麗系", "其他"]
    pintung = ["豚骨", "醬油", "雞白", "雞清", "家系"]

    #東部
    yilan = ["豚骨", "三星蔥"]
    hualien = ["豚骨", "魚白"]
    taitung = ["豚骨"]

    city_soup = [taipei,new_taipei,keelung,taoyuan,miaoli,hsinchu_county,hsinchu_city, \
                 taichung,chuanghua,nantou,yunlin, \
                 chiayi,tainan,kaohsiung,pintung, \
                 yilan,hualien,taitung] 

    
    for i in range(len(city_soup)):

        cond = str(city_name[i])+":"
        soup = city_soup[i] 
        
        #----------------選完湯頭介面不同湯頭介面-----------------
        for item in soup:
            n = cond+item
            #---------------------------------query 直接推薦、湯頭推薦、看更多類似推薦--------------------------
            if ':' in n:
                select_first_param = n[:n.index(':')]
                select_second_param = n[n.index(':')+1:]
                
                if (select_first_param == '直接推薦') or (select_first_param == '看更多推薦'):                
                    result = query_province_direct(select_second_param)
                            
                elif select_first_param in city_name:
                    result = query_province_soup(select_first_param, select_second_param)
                    
            #---------------------------------put all data in a string--------------------------
            ouput_database_fb = ''
            ouput_database_map = ''
            output_before_random = ''
            for r in result:
                try:
                    ouput_database_fb += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                        FB_R_CREATE:{r[2].create_on},FB_R_RAMEN:{r[2].ramen_name},FB_R_CONTENT:{r[2].fb_review},\
                        CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'

                except AttributeError:
                    ouput_database_map += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                        MAP_REVIEW:{r[1].map_review},\
                        CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
                    

            output_before_random += ouput_database_fb
            output_before_random += ouput_database_map
            output_before_random_clear = output_before_random.replace(u'\xa0', u' ').replace(' ','')
                
            #---------------------------------change data to a list of datas--------------------------
            output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
            for data in output_whole_lst:
                if data == '':
                    output_whole_lst.remove(data)
            #---------------------------------random(everytime renew can auto random)--------------------------
            output_s = secrets.choice(output_whole_lst)
            output_lst = convert_string_to_lst(output_s, ',')
            
            store_n = output_lst[0][output_lst[0].index(':')+1:]
            address = output_lst[1][output_lst[1].index(':')+1:]
            descrip = output_lst[2][output_lst[2].index(':')+1:]
            trans = output_lst[3][output_lst[3].index(':')+1:]

            if len(output_lst) == 9:
                #FB評論
                c1 = output_lst[4][output_lst[4].index(':')+1:]
                c2 = output_lst[5][output_lst[5].index(':')+1:]
                c3 = output_lst[6][output_lst[6].index(':')+1:]
                comment = f'貼文時間：\n{c1}\n品項：\n{c2}\n評論：\n{c3}'
            elif len(output_lst) == 7:
                #googleMap
                comment = output_lst[4][output_lst[4].index(':')+1:]

            if event.message.text == n:

                flex_message5 = FlexSendMessage(
                            alt_text='快回來看看我幫你找到的店家！',
                            contents= {
                                        "type": "carousel",
                                        "contents": [
                                            {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "text",
                                                    "text": store_n,
                                                    "align": "start",
                                                    "size": "md",
                                                    "gravity": "center",
                                                    "color": "#ffffff",
                                                    "wrap": True
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [],
                                                    "width": "80px",
                                                    "height": "20px"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "+到最愛",
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單:"+store_n
                                                        }
                                                    }
                                                    ],
                                                    "width": "60px",
                                                    "height": "25px",
                                                    "backgroundColor": "#FFCB69",
                                                    "cornerRadius": "20px",
                                                    "position": "absolute",
                                                    "offsetEnd": "xxl",
                                                    "offsetTop": "lg"
                                                }
                                                ],
                                                "paddingTop": "15px",
                                                "paddingAll": "15px",
                                                "paddingBottom": "16px",
                                                "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "地址：",
                                                        "color": "#797D62",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "↓↓點擊下方地址可以直接幫你傳送位置噢！",
                                                        "color": "#CA8E68",
                                                        "size": "xs",
                                                        "wrap": True,
                                                        "weight": "regular"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": address,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": address
                                                    },
                                                    "margin": "md"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "lg"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "特色：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": descrip,
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "margin": "md"
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "lg"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "鄰近交通資訊：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "text": trans,
                                                        "margin": "md"
                                                    }
                                                    ],
                                                    "paddingBottom": "18px"
                                                }
                                                ],
                                                "spacing": "md",
                                                "paddingAll": "12px"
                                            },
                                            "footer": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+cond[0:-1]
                                                    },
                                                    "color": "#D08C60"
                                                }
                                                ]
                                            },
                                            "styles": {
                                                "footer": {
                                                "separator": False
                                                }
                                            }
                                            },
                                            {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "text",
                                                    "text": store_n,
                                                    "align": "start",
                                                    "size": "md",
                                                    "gravity": "center",
                                                    "color": "#ffffff",
                                                    "wrap": True
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [],
                                                    "width": "80px",
                                                    "height": "20px"
                                                },
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "+到最愛",
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單:"+store_n
                                                        }
                                                    }
                                                    ],
                                                    "width": "60px",
                                                    "height": "25px",
                                                    "backgroundColor": "#FFCB69",
                                                    "cornerRadius": "20px",
                                                    "position": "absolute",
                                                    "offsetEnd": "xxl",
                                                    "offsetTop": "lg"
                                                }
                                                ],
                                                "paddingTop": "15px",
                                                "paddingAll": "15px",
                                                "paddingBottom": "16px",
                                                "backgroundColor": "#876C5A"
                                            },
                                            "body": {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "網友評論：",
                                                        "size": "md",
                                                        "wrap": True,
                                                        "color": "#797D62",
                                                        "margin": "md",
                                                        "weight": "bold"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "size": "sm",
                                                        "wrap": True,
                                                        "margin": "md",
                                                        "text": comment
                                                    }
                                                    ],
                                                    "paddingBottom": "18px"
                                                }
                                                ],
                                                "spacing": "md",
                                                "paddingAll": "12px"
                                            },
                                            "footer": {
                                                "type": "box",
                                                "layout": "horizontal",
                                                "contents": [
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+cond[0:-1]
                                                    },
                                                    "color": "#D08C60"
                                                }
                                                ]
                                            },
                                            "styles": {
                                                "footer": {
                                                "separator": False
                                                }
                                            }
                                            }
                                        ]
                                        }

            )

                line_bot_api.reply_message(event.reply_token,flex_message5)

#----------------最愛清單訊息觸發設定-----------------   
    #if event.message.text == "最愛清單":
    #    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "尚未有最愛清單，快去加入你喜歡的拉麵吧！\uDBC0\uDC5e"))


if __name__ == 'main':
    app.run(debug=True) 
        

 

