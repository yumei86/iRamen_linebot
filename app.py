from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json
import os
from linebot.exceptions import LineBotApiError

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import secrets
import random
import csv
import re
import requests

from vincenty import vincenty
from itertools import islice

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

  def __init__(self, store_id, stores, create_on, ramen_name, fb_review):
    self.store_id = store_id
    self.stores = stores
    self.create_on = create_on
    self.ramen_name = ramen_name
    self.fb_review = fb_review

class Favorite(db.Model):
  __tablename__ = 'favorite'
  id = db.Column (db.Integer, primary_key = True)
  line_id = db.Column (db.String(34), nullable = False)
  detail_store_id = db.Column (db.String(10), db.ForeignKey('store.detail_store_id'), nullable = False, onupdate ='CASCADE')
  
  def __init__(self, line_id, detail_store_id):
    self.line_id = line_id
    self.detail_store_id = detail_store_id

def get_data_str(lst):
    output_before_random = ''
    for r in lst:
        if r[2] is None:
            output_before_random += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                            MAP_REVIEW:{r[1].map_review},\
                            LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},OPEN_TIME:{r[1].open_time},\
                            CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
        else:
            try:
                output_before_random += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                    FB_R_CREATE:{r[2].create_on},FB_R_RAMEN:{r[2].ramen_name},FB_R_CONTENT:{r[2].fb_review},\
                    LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},OPEN_TIME:{r[1].open_time},\
                    CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'

            except AttributeError as error:
                output_before_random += f'STORE:{r[1].store},ADDRESS:{r[1].address},DISCRIPTION:{r[1].discription},TRANSPORT:{r[1].transport},\
                    MAP_REVIEW:{r[1].map_review},\
                    LONGITUDE:{r[1].longtitute},LATITUDE:{r[1].latitude},OPEN_TIME:{r[1].open_time},\
                    CHECK_TAG:{r[1].soup},CHECK_CITY:{r[1].province}%'
    return output_before_random
        

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

#----------------主要用在直接打字query店家的部分-----------------
def query_store(store_k1,store_k2):
    store_direct = db.session.query(Main_store, Store, Post)\
                        .outerjoin(Post, Post.store_id == Main_store.store_id)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.store.contains(store_k1))\
                        .filter(Store.store.contains(store_k2))\
                        .filter(Store.still_there == True)
    return store_direct
#----------------主要用在定位系統GIS的部分-----------------
def query_region_by_store_table(r):
    province_soup_q = db.session.query(Main_store, Store)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.region == r)\
                        .filter(Store.still_there == True)
    return province_soup_q
def take(n, iterable):
    #"Return first n items of the iterable as a list"
    return list(islice(iterable, n))
def caculate_distance(user_loc,lst):
    store_distance_name = []
    store_detail_list = []
    for r in lst:
        stores_loation_before_choice = (float(r[1].latitude),float(r[1].longtitute))
        distance = vincenty(user_loc, stores_loation_before_choice) #caculate distance
        store_distance_name.append(r[1].store)
        store_detail_list.append((distance,str(r[1].soup)))
    city_dis_dic = dict(zip(store_distance_name, store_detail_list))
    sorted_city_dis_dic = {k: v for k, v in sorted(city_dis_dic.items(), key=lambda item: item[1][0])}
    return sorted_city_dis_dic
def distance_template_generator(lst):
    distance_message = {
                        "type": "carousel",
                        "contents": []
                       }
    lst_to_append_stores = distance_message["contents"]

    for t in lst:
        #km to m
        distance_message_content = {
                                "type": "bubble",
                                "size": "mega",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": t[0],
                                        "align": "center",
                                        "size": "md",
                                        "gravity": "center",
                                        "color": "#ffffff",
                                        "wrap": True
                                    }
                                    ],
                                    "paddingTop": "15px",
                                    "paddingAll": "15px",
                                    "paddingBottom": "16px",
                                    "backgroundColor": "#797D62"
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
                                            "text": f"距離你：{t[1][0]}公里",
                                            "size": "md",
                                            "wrap": True,
                                            "color": "#876C5A",
                                            "margin": "md",
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "separator",
                                            "margin": "lg"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"風格：{t[1][1]}",
                                            "size": "md",
                                            "wrap": True,
                                            "color": "#876C5A",
                                            "margin": "md",
                                            "weight": "bold"
                                        }
                                        ],
                                        "paddingBottom": "10px"
                                    }
                                    ],
                                    "spacing": "sm",
                                    "paddingAll": "12px"
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "adjustMode": "shrink-to-fit",
                                    "margin": "none",
                                    "align" : "start",
                                    "contents": [
                                    {
                                        "type": "button",
                                        "action": {
                                        "type": "message",
                                        "label": "看店家細節",
                                        "text": f"搜尋店家細節♡{t[0]}"#後面要加看前五項/看後五項按鈕
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
        lst_to_append_stores.append(distance_message_content)
    return distance_message
#--------------------天氣weather api--------------------------------
def query_local_weather(lon,lat,APIkey):
    weather_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&lang=zh_tw&appid={APIkey}&units=metric'
    get_weather_data = requests.get(weather_url)
    weather_result = get_weather_data.json()
    return weather_result
#---------------------formation-------------------------------
def convert_string_to_lst(string,c): 
    li = list(string.split(c)) 
    return li 
def divide_map_review(comment_s):
    comment_clean = comment_s.replace(" - ", "-").replace("- ", "-").replace(" -", "-")
    comment_clean_split = re.split('[   ]',comment_clean)
    comment_lst = [i for i in comment_clean_split if i]
    if len(comment_lst) > 1:
        comment_final_list = []
        for i, val in enumerate(comment_lst):
            if i != (len(comment_lst)-1) and val[-1].islower() == True and val[0].isupper() == True and comment_lst[i+1][0].isupper() == True:
                val = val + comment_lst[i+1]
                comment_lst.remove(comment_lst[i+1])
            comment_final_list.append(val)

        return comment_final_list
    else:
        return comment_lst
##----------------我的最愛取得userid資料庫設定-----------------
def get_love_list_from_user_id(user_id):  
    love_list_q = db.session.query(Store,Favorite)\
      .outerjoin(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
      .filter(Favorite.line_id == user_id)
    love_list = ''
    for l in love_list_q :
      love_list += f'{l[0].store}%'
    love_list_clear = love_list.replace(u'\xa0', u' ').replace(' ','')
    output_whole_love_list = convert_string_to_lst(love_list_clear,'%')
    output_whole_love_list = [i for i in output_whole_love_list if i]
    return output_whole_love_list

def count_store_in_table(store_name):
    store_id_q = db.session.query(Store)\
        .filter(Store.store == store_name)\
        .count()
    return store_id_q
def get_store_id(store_name):
    get_id = ''
    store_id_q = db.session.query(Store)\
        .filter(Store.store == store_name)
    for data in store_id_q:
        get_id += data.detail_store_id
    return get_id
def store_exist(get_user_line_id, store_name):
    store_exist = db.session.query(Store, Favorite)\
        .join(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
        .filter(Favorite.line_id == get_user_line_id)\
        .filter(Store.store == store_name).count()
    return store_exist
def count_love_list(user_id):
    count_love_list = db.session.query(Favorite)\
        .filter(Favorite.line_id == user_id).count()
    return count_love_list

##----------------Query love-list by userID----------------
def get_list_from_user_id(user_id):  
    love_list_q = db.session.query(Store,Favorite)\
        .outerjoin(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
        .filter(Favorite.line_id == user_id)
    return love_list_q

def query_map_review_by_full_name(s):
    review = db.session.query(Store).filter(Store.store == s).filter(Store.still_there == True)
    love_list = ''
    for l in review:
      love_list += f'STORE:{l.store},ADDRESS:{l.address},DISCRIPTION:{l.discription},TRANSPORT:{l.transport},MAP_REVIEW:{l.map_review},CITY:{l.province},LONGITUDE:{l.longtitute},LATITUDE:{l.latitude},\
                        OPEN_TIME:{l.open_time},CHECK_TAG:{l.soup}%'
    love_list = love_list.replace(u'\xa0', u' ').replace('\n','')
    return love_list

#----------------最愛清單動態的模板設定-----------------

def favorite_list_generator(favorite_list):    
    button_list = [BoxComponent(
                    layout="vertical",
                    margin="sm",
                    spacing="sm",
                    contents=[
                        TextComponent(text="最愛清單",weight="bold",size="xl",margin="sm",wrap=True,),
                        SeparatorComponent(margin = "xxl")
                    ])]
    for i in favorite_list:

        favorite_button = ButtonComponent(style="primary", color="#997B66", size="sm", margin="sm",
                                        action=MessageAction(label=i, text=f'搜尋你的清單♡{i}'),)
        delete_button = ButtonComponent(style="secondary", color="#F1DCA7", size="sm", margin="sm", flex=0,
                                      action=MessageAction(label="-", text="刪除最愛清單♡"+i),)
        button_row = BoxComponent(layout="horizontal", margin="md", spacing="sm",
                                contents=[favorite_button, delete_button])
        button_list.append(button_row)
    
    bubble = BubbleContainer(
        director='ltr',
    
        body=BoxComponent(
            layout="vertical",
            contents=button_list
        )
    )

    return bubble

#----------------tag functions-----------
def tags_button_generator(tag_lst,append_obj,city):
    lst_to_append_tags = append_obj["body"]["contents"]
    tag_btn_lst = []

    for item in tag_lst:
        tag_btn = {
              "type": "button",
              "action": {
              "type": "message",
              "label": item,
              "text": f"{city}:{item}" 
              },
              "color": "#D08C60"
        }

        tag_btn_lst.append(tag_btn)
    tag_btn_group = [tag_btn_lst[2*i:(2*i)+2] for i in range(int((len(tag_btn_lst)/2)) +1)]
    tag_btn_group = [sub for sub in tag_btn_group if len(sub) != 0]

    for sub in tag_btn_group:
        tag_btn_layout = {
            "type": "box",
            "layout": "vertical",
            "margin": "sm",
            "contents": []
        }
        tag_btn_layout["contents"] = sub
        lst_to_append_tags.append(tag_btn_layout)

    return append_obj

def store_query_tags(s):
    store_query_tags = db.session.query(Store).filter(Store.store == s)
    result = ''
    for r in store_query_tags:
        result += f"{r.soup}"
    return result

#----------------用來做縣市對應region字典-----------------
north = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","臺北市"]
center = ["台中市","彰化縣","南投縣","雲林縣","臺中市"]
south = ["嘉義市","台南市","高雄市","屏東縣","臺南市"]
east = ["宜蘭縣","花蓮縣","台東縣","臺東縣"]
n_dict = dict.fromkeys(north, ("北","north"))
c_dict = dict.fromkeys(center, ("中","center"))
s_dict = dict.fromkeys(south, ("南","south"))
e_dict = dict.fromkeys(east, ("東","east"))

#----------------官方設定-----------------

@app.route("/", methods=['GET'])
def hello():
    return "Hello RAMEN World!"

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

    return 'OK RAMEN'

#----------------設定回覆訊息介面-----------------

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # msg = event.message.text
    # msg = msg.encode('utf-8') 

#----------------取得userid-----------------
    user_id = event.source.user_id

    if user_id == '':
        user_id = event.source.user_id
    TWregion = ["北部","中部","南部","東部"]
    city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]
    city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
    city_region_dict = dict(zip(["north","center","south","east"], [north,center,south,east]))
#----------------雞湯文-----------------
    store_example = ['「鷹流 公館」','「公 子」','「山下公 園」','「隱家 赤峰」','「七 面鳥」','「麵屋 壹」','「真 劍」','「秋 鳴」','「Mr 拉麵雲」','「辰 拉」','「京都 柚子」','「麵屋 ichi」','「麵屋 壹之穴」','「KIDO 拉麵」','「Ramen 初」','「暴 走」','「Hiro 新店」']
    random.shuffle(store_example)
    store_example_choice_lst = store_example[:5]
    store_example_choice = ''.join(store_example_choice_lst)
    # store_example_choice = reduce(lambda a,x: a+str(x), store_example_choice_lst, "")
    #----------------拉麵推薦介面-----------------
    if event.message.text == "拉麵推薦":
    #讀需要的json資料
        f = open('json_files_for_robot/json_for_app.json', encoding="utf8") 
        data = json.load(f) 

        flex_message = FlexSendMessage(
                        alt_text='拉麵推薦',
                        contents= data[0]
        )

        line_bot_api.reply_message(event.reply_token,flex_message)
        f.close()
#----------------不同區域的介面設定-----------------

    elif event.message.text in TWregion:
        f_region = open('json_files_for_robot/json_for_app.json', encoding="utf8") 
        data_region = json.load(f_region) 

        for i,v in enumerate(TWregion):
            if event.message.text == v:
                flex_message1 = FlexSendMessage(
                               alt_text= v + '的縣市',
                               contents= data_region[i+1]
                )

                line_bot_api.reply_message(event.reply_token,flex_message1) 

        f_region.close()
#----------------選擇湯頭介面-----------------
    elif "湯頭推薦:" in event.message.text:
        user_choice = event.message.text
        city_choice = user_choice[user_choice.index(':')+1:]
        #用迴圈去讀湯頭選單
        #讀需要的推薦介面json資料
        f_city_soup = open('json_files_for_robot/soup_'+city_name_dic[city_choice][1]+'_city.json', encoding="utf8") 
        data_city_soup = json.load(f_city_soup) 
        #---------------------get province list----------------#
        for i, v in enumerate(city_region_dict[city_name_dic[city_choice][1]]):
            if v == city_choice:
                flex_message2 = FlexSendMessage(
                           alt_text='快回來看看我幫你找到的湯頭！',
                           contents= data_city_soup[i]
                )

                line_bot_api.reply_message(event.reply_token,flex_message2) 

        f_city_soup.close()

    elif event.message.text in city_name:
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
                                            "text": "湯頭推薦:"+event.message.text
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
                                            "text": "直接推薦:"+event.message.text
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
    
    elif event.message.text == "嘉義縣":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "抱歉！\uDBC0\uDC7c 這邊尚未有拉麵店，請至附近其他縣市看看!"))
    elif ('湯頭推薦:'not in event.message.text and '評論' not in event.message.text and ':' in event.message.text) and ':' not in event.message.text[0] and ':' not in event.message.text[-1] and '最愛清單' not in event.message.text:
        user_choice = event.message.text
        select_first_param = user_choice[:user_choice.index(':')]
        select_second_param = user_choice[user_choice.index(':')+1:]
        result = ''
        if ((select_first_param == '直接推薦') or (select_first_param == '看更多推薦')) and select_second_param in city_name:                
            result = query_province_direct(select_second_param)
        elif select_first_param in city_name:
            result = query_province_soup(select_first_param, select_second_param)
        else:
            result = ''
        # #---------------------------------put all data to a string--------------------------  
        if result == '':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\uDBC0\uDC7c輸入的字串不合法，查詢不到你想要的東西"))         
        output_before_random_clear = get_data_str(result)
        if output_before_random_clear == None or output_before_random_clear == '':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\uDBC0\uDC7c輸入的字串不合法，查詢不到你想要的東西"))
        else:
            output_before_random_clear = output_before_random_clear.replace(u'\xa0', u' ').replace('\n','')
            #---------------------------------change data to a list of datas--------------------------
            output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
            output_whole_lst = [i for i in output_whole_lst if i]
            #---------------------------------random(everytime renew can auto random)--------------------------
            output_s = random.choice(output_whole_lst)
            output_lst = convert_string_to_lst(output_s, ',')
            if len(output_lst) == 12 or len(output_lst) == 10:
                store_n = output_lst[0][output_lst[0].index(':')+1:]
                address = output_lst[1][output_lst[1].index(':')+1:]
                descrip = output_lst[2][output_lst[2].index(':')+1:]
                trans = output_lst[3][output_lst[3].index(':')+1:]
                f_city = output_lst[-1][output_lst[-1].index(':')+1:]
                if len(output_lst) == 12:
                    #FB評論
                    c1 = output_lst[4][output_lst[4].index(':')+1:]
                    c2 = output_lst[5][output_lst[5].index(':')+1:]
                    c3 = output_lst[6][output_lst[6].index(':')+1:]
                    comment = f'貼文時間：\n{c1}\n\n品項：\n{c2}\n\n評論：\n{c3}'
                    lon = output_lst[7][output_lst[7].index(':')+1:]
                    lat = output_lst[8][output_lst[8].index(':')+1:]
                    op  = output_lst[9][output_lst[9].index(':')+1:]

                elif len(output_lst) == 10:
                    #googleMap
                    comment = output_lst[4][output_lst[4].index(':')+1:]
                    lon = output_lst[5][output_lst[5].index(':')+1:]
                    lat = output_lst[6][output_lst[6].index(':')+1:] 
                    op  = output_lst[7][output_lst[7].index(':')+1:]  
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼O1」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2") )
            
                flex_message9 = FlexSendMessage(
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
                                                                            "text": "加到最愛清單♡"+store_n
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
                                                                            "text": "↓↓點擊下方地址可以直接幫你傳送地圖！",
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
                                                                            "text": f"正在幫你找到→ \n{lon}→{lat}"
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
                                                                        },
                                                                        {
                                                                        "type": "separator",
                                                                        "margin": "lg"
                                                                        },
                                                                        {
                                                                        "type": "text",
                                                                        "text": "營業時間：",
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
                                                                        "text": op,
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
                                                                        "label": "看同類推薦",
                                                                        "text": user_choice
                                                                        },
                                                                        "color": "#D08C60"
                                                                    },
                                                                    {
                                                                        "type": "button",
                                                                        "action": {
                                                                        "type": "message",
                                                                        "label": "看相似店鋪",
                                                                        "text": f"類別搜索中→{store_n}→{f_city}"
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
                                                                            "text": "加到最愛清單♡"+store_n
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
                                                                        "label": "評論超連結",
                                                                        "text": f"輸出評論超連結→{store_n}"
                                                                        },
                                                                        "color": "#D08C60"
                                                                    },
                                                                    {
                                                                        "type": "button",
                                                                        "action": {
                                                                        "type": "message",
                                                                        "label": "看當地天氣",
                                                                        "text": f"{store_n} 附近天氣搜索中→ \n{lon}→{lat}"
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
                line_bot_api.reply_message(event.reply_token,flex_message9)

            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"資料庫有誤"))
            
    elif ' ' in event.message.text and ' ' not in event.message.text[-1] and ' ' not in event.message.text[0]:
        user_select = event.message.text
        if "有人評論→" in user_select:
            warm_msg = ['拉麵不分貴賤','No Ramen no life','拉麵是恆久忍耐又有恩慈','好拉麵不分先來後到但排隊不可解壓縮','用拉麵抵擋水逆！','拉麵拯救宇宙','趁年輕多吃拉麵','拉麵濃淡皆宜多吃為佳','做好事，說好話，吃好麵','總是需要一碗拉麵，哪怕是一點點自以為是的紀念','總有一碗麵一直住在心底，卻消失在生活里','用心甘情願的態度吃隨遇而安的拉麵','希望所有的努力都不會被辜負，所有的拉麵都不會冷掉','拉麵是留給堅持的人','拉麵使人偉大','比一個人吃拉麵更寂寞的是一個人沒有錢吃拉麵','眼淚不是答案，拉麵才是選擇','一個人之所以強大，是因為他搞清楚自己想要吃的拉麵','有些事讓你一夜長大，有些麵讓你一夜感謝']
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"{random.choice(warm_msg)}"))
        elif "正在幫你找到→" in user_select:
            text_list = user_select.split("→")
            lonti = float(text_list[1])
            lati  = float(text_list[2])
            line_bot_api.reply_message(event.reply_token,LocationSendMessage(title='點擊帶你前往！',address='iRamen',latitude= lati,longitude= lonti))
        #----------------weather api logic----------------- 
        elif "附近天氣搜索中→" in user_select:
            text_list = user_select.split("→")
            lonti = float(text_list[1])
            lati  = float(text_list[2])
            store_name = str(text_list[0]).replace('搜索中','').replace(' ','')
            WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
            weather_data = query_local_weather(lonti, lati, WEATHER_API_KEY)
            weather_description = weather_data['current']['weather'][0]['description']
            main_temp = weather_data['current']['temp']
            temp_feels_like = weather_data['current']['feels_like']
            humidity_procent = weather_data['current']['humidity']
            uvi_index = weather_data['current']['uvi']
            uvi_index_description = ''
            if 0 <= uvi_index <= 2:
              uvi_index_description = '對於一般人無危險'
            elif 3 <= uvi_index <= 5:
              uvi_index_description = '無保護暴露於陽光中有較輕傷害的風險'
            elif 6 <= uvi_index <= 7:
              uvi_index_description = '無保護暴露於陽光中有很大傷害的風險'
            elif 8 <= uvi_index <= 10:
              uvi_index_description = '暴露於陽光中有極高風險'
            elif 11 <= uvi_index:
              uvi_index_description = '暴露於陽光中極其危險'
            else:
              uvi_index_description = '目前無相關資訊'
            if weather_data:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f'目前{store_name}\n\n【{weather_description}】\n\n氣溫:{main_temp}℃\n體感溫度:{temp_feels_like}℃\n濕度:{humidity_procent}%\n紫外線指數:{uvi_index}，{uvi_index_description}'))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼W1」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2")
            )
        else:    #----------------輸入關鍵字找尋店家-----------------
            input_lst = user_select.split()
            keyword_result=''
            if len(input_lst) == 2 :
              count_store = query_store(str(input_lst[0]),str(input_lst[1])).count()
              # print(count_store)
              if count_store != 0:
                keyword_result = query_store(str(input_lst[0]),str(input_lst[1]))
            #       else:
            #         keyword_result = ''
            #     else:
            #         keyword_result = ''
            # else:
            #   keyword_result = ''
       #       ---------------------------------put all data to a string--------------------------
            if keyword_result == '':
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n\n例:{store_example_choice}\
                                                                                          \n\n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我隨意留一個半形空,但不可在前後加入空白)\
                                                                                          \n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！"))
            else:
                output_before_random_clear = get_data_str(keyword_result)
                if output_before_random_clear == None:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n\n例:{store_example_choice}\
                                                                                              \n\n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我隨意留一個半形空,但不可在前後加入空白)\
                                                                                              \n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！"))
                else:
                    output_before_random_clear = output_before_random_clear.replace(u'\xa0', u' ').replace('\n','')
                    #---------------------------------change data to a list of datas--------------------------
                    output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
                    output_whole_lst = [i for i in output_whole_lst if i]
                    output_s = secrets.choice(output_whole_lst)
                    output_lst = convert_string_to_lst(output_s, ',')
                    if len(output_lst) == 12 or len(output_lst) == 10:
                    
                        store_n = output_lst[0][output_lst[0].index(':')+1:]
                        address = output_lst[1][output_lst[1].index(':')+1:]
                        descrip = output_lst[2][output_lst[2].index(':')+1:]
                        trans = output_lst[3][output_lst[3].index(':')+1:]
                        f_city = output_lst[-1][output_lst[-1].index(':')+1:]
                        if len(output_lst) == 12:
                            #FB評論
                            c1 = output_lst[4][output_lst[4].index(':')+1:]
                            c2 = output_lst[5][output_lst[5].index(':')+1:]
                            c3 = output_lst[6][output_lst[6].index(':')+1:]
                            comment = f'貼文時間：\n{c1}\n\n品項：\n{c2}\n\n評論：\n{c3}'
                            lon = output_lst[7][output_lst[7].index(':')+1:]
                            lat = output_lst[8][output_lst[8].index(':')+1:]
                            op  = output_lst[9][output_lst[9].index(':')+1:]
                            
                        elif len(output_lst) == 10:
                            #googleMap
                            comment = output_lst[4][output_lst[4].index(':')+1:]
                            lon = output_lst[5][output_lst[5].index(':')+1:]
                            lat = output_lst[6][output_lst[6].index(':')+1:]
                            op  = output_lst[7][output_lst[7].index(':')+1:]  
                        else:
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼S1」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2") )
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
                                                                            "text": "加到最愛清單♡"+store_n
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
                                                                            "text": "↓↓點擊下方地址可以直接幫你傳送地圖！",
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
                                                                            "text": f"正在幫你找到→ \n{lon}→{lat}"
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
                                                                        },
                                                                        {
                                                                        "type": "separator",
                                                                        "margin": "lg"
                                                                        },
                                                                        {
                                                                        "type": "text",
                                                                        "text": "營業時間：",
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
                                                                        "text": op,
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
                                                                    "adjustMode": "shrink-to-fit",
                                                                    "margin": "none",
                                                                    "align" : "start",
                                                                    "contents": [
                                                                    {
                                                                        "type": "button",
                                                                        "action": {
                                                                        "type": "message",
                                                                        "label": "再搜索一次",
                                                                        "text": user_select
                                                                        },
                                                                        "color": "#D08C60"
                                                                    },
                                                                    {
                                                                        "type": "button",
                                                                        "action": {
                                                                        "type": "message",
                                                                        "label": "看相似店鋪",
                                                                        "text": f"類別搜索中→{store_n}→{f_city}"
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
                                                                            "text": "加到最愛清單♡"+store_n
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
                                                                        "label": "評論超連結",
                                                                        "text": f"輸出評論超連結→{store_n}"
                                                                        },
                                                                        "color": "#D08C60"
                                                                    },
                                                                    {
                                                                        "type": "button",
                                                                        "action": {
                                                                        "type": "message",
                                                                        "label": "看當地天氣",
                                                                        "text": f"{store_n} 附近天氣搜索中→ \n{lon}→{lat}"
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
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼S3」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2")
        )       

    elif ' ' in event.message.text and (' ' in event.message.text[-1] or ' '  in event.message.text[0]):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n\n例:{store_example_choice}\
                                                                              \n\n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我隨意留一個半形空,但不可在前後加入空白)\
                                                                              \n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！")
    )
    elif "輸出評論超連結→" in event.message.text:
        text_list = event.message.text.split("→")
        store_name = str(text_list[1])
        map_review_data = db.session.query(Store.map_review).filter(Store.store == text_list[1]).filter(Store.still_there == True)
        map_format = ''
        for r in map_review_data:
          #抓出來是tuple
          r_str = ''.join(list(map(str,r)))
          r_str = r_str.replace(u'\xa0', u' ').replace(u'\n', u' ')
          map_lst = divide_map_review(r_str)
          map_lst = [v+'\n\n' if i%2 != 0 and i != len(map_lst)-1 else v+'\n' for i,v in enumerate(map_lst)]
          map_format += ''.join(map(str, map_lst))
          map_format = map_format[:-1]
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"{store_name}\n\n{map_format}")
        )
    elif "類別搜索中→" in event.message.text:
        group_list = event.message.text.split("→")
        store_n = str(group_list[1])
        city_n = str(group_list[2])
        tags = store_query_tags(store_n)
        tag_list = convert_string_to_lst(tags,'#')
        tag_list = [i for i in tag_list if i]
        contents_tags = {
                          "type": "bubble",
                          "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                              {
                                "type": "text",
                                "text": f"{store_n}相關風格",
                                "weight": "bold",
                                "align": "start",
                                "gravity": "center",
                                "size": "lg",
                                "color": "#876C5A",
                                "wrap":True
                              },
                              {
                                "type": "text",
                                "text": "點擊看類似店家...",
                                "size": "xs",
                                "margin": "sm"
                              },
                              {
                                "type": "separator",
                                "margin": "lg"
                              }
                            ]
                        }
                        }

        flex_message_tags = FlexSendMessage(
                                        alt_text='快回來看看我幫你找到的店家！',
                                        contents= tags_button_generator(tag_list, contents_tags, city_n))
        line_bot_api.reply_message(event.reply_token,flex_message_tags)
        # line_bot_api.reply_message(event.reply_token,TextSendMessage(text = f"{store_n}{city_n}{tag_list}"))
    #----------------最愛清單訊息觸發設定-----------------  
    elif event.message.text == "最愛清單":
        user_list_count = count_love_list(user_id)
        if user_list_count == 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "尚未有最愛清單，快去加入你喜歡的拉麵吧！\uDBC0\uDC5e"))
        elif user_list_count != 0:
            ramen_test = get_love_list_from_user_id(user_id)
            flex_message6 = FlexSendMessage(
                                        alt_text= '快回來看看我的最愛！',
                                        contents= favorite_list_generator(ramen_test)
            )
            line_bot_api.reply_message(event.reply_token,flex_message6) 
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼L2」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2")
        )       
     #----------------最愛清單加入資料庫設定與訊息回覆設定-----------------
    elif "搜尋你的清單♡" in event.message.text:
        text_l  = event.message.text.split("♡")
        store_name_full = text_l[1] 
        if store_exist(user_id, store_name_full) != 0:
            store_detail = query_map_review_by_full_name(store_name_full)
            #---------------------------------change data to a list of datas--------------------------
            output_whole_lst = convert_string_to_lst(store_detail,',')
            output_whole_lst = [i for i in output_whole_lst if i]

            r_store = output_whole_lst[0][output_whole_lst[0].index(':')+1:]
            ad = output_whole_lst[1][output_whole_lst[1].index(':')+1:]
            dis = output_whole_lst[2][output_whole_lst[2].index(':')+1:]
            trans = output_whole_lst[3][output_whole_lst[3].index(':')+1:]
            com = output_whole_lst[4][output_whole_lst[4].index(':')+1:]
            com_lst = divide_map_review(com)
            com_lst = [v+'\n\n' if i%2 != 0 and i != len(com_lst)-1 else v+'\n' for i,v in enumerate(com_lst)]
            com_format = ''.join(map(str, com_lst))
            city_r = output_whole_lst[5][output_whole_lst[5].index(':')+1:]
            lont = output_whole_lst[6][output_whole_lst[6].index(':')+1:]
            lati = output_whole_lst[7][output_whole_lst[7].index(':')+1:]
            opent = output_whole_lst[8][output_whole_lst[8].index(':')+1:]
            flex_message7 = FlexSendMessage(
                            alt_text='快回來看看你的最愛<3',
                            contents={
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
                                                "text": r_store,
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
                                                    "text": "刪除最愛",
                                                    "size": "sm",
                                                    "align": "center",
                                                    "offsetTop": "3px",
                                                    "action": {
                                                        "type": "message",
                                                        "label": "刪除最愛清單",
                                                        "text": "刪除最愛清單♡"+r_store
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
                                                    "text": "↓↓點擊下方地址可以直接幫你傳送地圖！",
                                                    "color": "#CA8E68",
                                                    "size": "xs",
                                                    "wrap": True,
                                                    "weight": "regular"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": ad,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": f"正在幫你找到→ \n{lont}→{lati}"
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
                                                    "text": dis,
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
                                                    },
                                                    {
                                                    "type": "separator",
                                                    "margin": "lg"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": "營業時間：",
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
                                                    "text": opent,
                                                    "margin": "md"
                                                    }
                                                ],
                                                "paddingBottom": "15px"
                                                }
                                            ],
                                            "spacing": "md",
                                            "paddingAll": "12px"
                                            },
                                            "footer": {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                            {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents":[
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看網友評論",
                                                    "text": f"\udbc0\udc54有人評論→ {r_store}\n\n{com_format}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看當地天氣",
                                                    "text": f"{r_store} 附近天氣搜索中→ \n{lont}→{lati}"
                                                },
                                                "color": "#D08C60"
                                                }
                                            ]
                                            },
                                            {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents":[
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看相似店鋪",
                                                    "text": f"類別搜索中→{r_store}→{city_r}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city_r
                                                },
                                                "color": "#D08C60"
                                                }
                                            ]
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

            line_bot_api.reply_message(event.reply_token,flex_message7)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "你已將此店家從最愛清單中刪除")
        )       

      
    elif "加到最愛清單♡" in event.message.text or "刪除最愛清單♡" in event.message.text:

        user_line_id = user_id

        text_l = event.message.text.split("♡")
        
        first_love_param = text_l[0]
        second_love_param = text_l[1] 

        if first_love_param == '加到最愛清單':
            store_in_table = count_store_in_table(second_love_param) #check if the store name legal
            favorite_list_count = count_love_list(user_line_id) #how many items a user save
            already_add_store_count = store_exist(user_line_id, second_love_param) #check if the store user want to add already exist in the list
            
            if store_in_table != 0:
                if favorite_list_count == 0 or\
                    favorite_list_count != 0 and already_add_store_count == 0 and favorite_list_count <= 25 :
                    get_foreign_id = get_store_id(second_love_param)#check the map_id(foreign key) of the store
                    data = Favorite(user_line_id,get_foreign_id)
                    while(data.id == None):
                        try:
                            db.session.add(data)
                            db.session.commit()
                        except IntegrityError:
                            db.session.rollback()
                            continue

                    line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="你剛剛成功把 " + second_love_param + " 加進最愛清單！")
                        )
                elif favorite_list_count > 25:

                    line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="最愛清單數量超過上限，請刪除部分資料\udbc0\udc7c")
                        )
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text= second_love_param + "已經在最愛清單！"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你輸入的店名資料庫裡沒有啦\udbc0\udc7c"))

        elif first_love_param == '刪除最愛清單':
            detail_id = get_store_id(second_love_param)
            if detail_id != '' and store_exist(user_line_id, second_love_param) != 0:
                data = db.session.query(Favorite)\
                        .filter(Favorite.detail_store_id == detail_id)\
                        .filter(Favorite.line_id == user_line_id)\
                        .first()
                db.session.delete(data)
                db.session.commit()
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="成功刪除"+ second_love_param ))

            elif store_exist(user_line_id, second_love_param) == 0: #check if the store user want to rermove already not exist in the list
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text= second_love_param + "已不在你的最愛清單囉!" ))

            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "發生錯誤請再試一次" ))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "不要亂打字!!!" ))

    #----------------定位叫使用者給位置-----------------
    elif event.message.text == "定位" :
        text_message_location = TextSendMessage(text='偷偷分享位置給我，我才能推薦附近店家給你哦！\uDBC0\uDCB9',
                                                quick_reply=QuickReply(items=[
                                                    QuickReplyButton(action=LocationAction(label="我在哪My LOC"))
                                                ]))
        line_bot_api.reply_message(event.reply_token,text_message_location) 
    elif "搜尋店家細節♡" in event.message.text:
        text_s = event.message.text.split("♡")
        store_full_name = text_s[1] 
        store_detail_for_distance = query_map_review_by_full_name(store_full_name)
        output_whole_lst = convert_string_to_lst(store_detail_for_distance,',')
        output_whole_lst = [i for i in output_whole_lst if i]
        if len(output_whole_lst) == 10:
            r_store = output_whole_lst[0][output_whole_lst[0].index(':')+1:]
            ad = output_whole_lst[1][output_whole_lst[1].index(':')+1:]
            dis = output_whole_lst[2][output_whole_lst[2].index(':')+1:]
            trans = output_whole_lst[3][output_whole_lst[3].index(':')+1:]
            com = output_whole_lst[4][output_whole_lst[4].index(':')+1:]
            com_lst = divide_map_review(com)
            com_lst = [v+'\n\n' if i%2 != 0 and i != len(com_lst)-1 else v+'\n' for i,v in enumerate(com_lst)]
            com_format = ''.join(map(str, com_lst))
            city_r = output_whole_lst[5][output_whole_lst[5].index(':')+1:]
            lont = output_whole_lst[6][output_whole_lst[6].index(':')+1:]
            lati = output_whole_lst[7][output_whole_lst[7].index(':')+1:]
            opent = output_whole_lst[8][output_whole_lst[8].index(':')+1:]
            flex_message8 = FlexSendMessage(
                            alt_text='快回來看看店家細節~',
                            contents={
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
                                                "text": r_store,
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
                                                    "text": "加到最愛",
                                                    "size": "sm",
                                                    "align": "center",
                                                    "offsetTop": "3px",
                                                    "action": {
                                                        "type": "message",
                                                        "label": "加到最愛清單",
                                                        "text": "加到最愛清單♡"+r_store
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
                                                    "text": "↓↓點擊下方地址可以直接幫你傳送地圖！",
                                                    "color": "#CA8E68",
                                                    "size": "xs",
                                                    "wrap": True,
                                                    "weight": "regular"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": ad,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": f"正在幫你找到→ \n{lont}→{lati}"
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
                                                    "text": dis,
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
                                                    },
                                                    {
                                                    "type": "separator",
                                                    "margin": "lg"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "text": "營業時間：",
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
                                                    "text": opent,
                                                    "margin": "md"
                                                    }
                                                ],
                                                "paddingBottom": "15px"
                                                }
                                            ],
                                            "spacing": "md",
                                            "paddingAll": "12px"
                                            },
                                            "footer": {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                            {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents":[
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看網友評論",
                                                    "text": f"\udbc0\udc54有人評論→ {r_store}\n\n{com_format}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看當地天氣",
                                                    "text": f"{r_store} 附近天氣搜索中→ \n{lont}→{lati}"
                                                },
                                                "color": "#D08C60"
                                                }
                                            ]
                                            },
                                            {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents":[
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看相似店鋪",
                                                    "text": f"類別搜索中→{r_store}→{city_r}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+city_r
                                                },
                                                "color": "#D08C60"
                                                }
                                            ]
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

            line_bot_api.reply_message(event.reply_token,flex_message8)
        
#----------------問題回報（未來可加donate資訊）----------------
    elif event.message.text == "問題回報":
        line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="\udbc0\udcb2常見問題\
                                        \n\
                                        \n• 選擇湯頭和評論品項不同:\n\n別擔心，該推薦店家是有賣你選的湯頭類型！\
                                        \n\
                                        \n• 希望有較小範圍的地區搜尋功能:\n\n在做了別急。\
                                        \n\
                                        \n\udbc0\udcb22月新增\n• 評論超連結\n• 店家附近天氣\n• 拉麵語錄\n• 分流看更多推薦\n• 看相似店鋪\n• 大幅提升回應速度\n\
                                        \n\
                                        \n\udbc0\udc84若你很喜歡我們的作品，也不吝嗇贊助，讓我們的iRamen變得更好，請匯款至以下戶頭:\n玉山銀行(808)0864979119334\
                                        \n\
                                        \n歡迎請填寫使用者回饋表單，非常感謝你！\udbc0\udc7a\
                                        \nhttps://reurl.cc/14RmVW"))

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n\n例:{store_example_choice}\
                                                                                  \n\n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我隨意留一個半形空,但不可在前後加入空白)\
                                                                                  \n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！"))
@handler.add(MessageEvent, message=LocationMessage)#定位細節
def handle_location(event):
    city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
    #---------------user info-----------------
    u_lat = event.message.latitude
    u_long = event.message.longitude   
    user_address = event.message.address
    u_address = user_address.replace(' ', '')
    user_location = (u_lat, u_long)
    all_store_province = ''
    choice_nearby_city_tup = ''
    for k, v in city_name_dic.items():
      if k in u_address:
        region_value = v[0]
        all_store_province = query_region_by_store_table(region_value)
        break
      elif k not in u_address and ("臺灣" in u_address or '台灣' in u_address or '台湾' in u_address or 'Taiwan' in u_address):
        #search all
        all_store_province = province_soup_q = db.session.query(Main_store, Store)\
                          .outerjoin(Store, Store.store_id == Main_store.store_id)\
                          .filter(Store.still_there == True)
        break
      elif k not in u_address and "臺灣" not in u_address or '台灣' not in u_address or '台湾' not in u_address or 'Taiwan' not in u_address:
        all_store_province = ''
      else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "出錯惹靠腰，麻煩幫忙在使用者回報填寫出錯代碼「G1」和您的狀況" ))
    
    # '''
    # 算距離
    # '''
    if all_store_province == '':
        text_message_foreign_location = TextSendMessage(text="\udbc0\udc7B目前不支援離島與國外拉麵店，請到台灣本島吃拉麵~",
                                                quick_reply=QuickReply(items=[
                                                    QuickReplyButton(action=LocationAction(label="再定位一次My LOC"))
                                                ]))
        line_bot_api.reply_message(event.reply_token,text_message_foreign_location) 
    else:
        sorted_city_distance_dic = caculate_distance(user_location,all_store_province)
        if  len(sorted_city_distance_dic) >= 10:
          choice_nearby_city_tup = take(10, sorted_city_distance_dic.items())
        else:
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text= "出錯惹靠腰，麻煩幫忙在使用者回報填寫出錯代碼「G2」和您的狀況" ))

    
    flex_message_location = FlexSendMessage(
                                        alt_text='快回來看看我幫你找到的店家！',
                                        contents= distance_template_generator(choice_nearby_city_tup),
                                        quick_reply= QuickReply(items=[QuickReplyButton(action=LocationAction(label="再定位一次My LOC")),
                                                                       QuickReplyButton(action=URIAction(label="拉麵地圖自己找",uri=f'https://www.google.com/maps/d/u/0/viewer?fbclid=IwAR3O8PKxMuqtqb2wMKoHKe4cCETwnT2RSCZSpsyPPkFsJ6NpstcrDcjhO2k&mid=1I8nWhKMX1j8I2bUkN4qN3-FSyFCCsCh7&ll={u_lat}%2C{u_long}'))
                                                                       ]))
    line_bot_api.reply_message(event.reply_token,flex_message_location)
        
if __name__ == 'main':
    app.run(debug=True) 
        

 

