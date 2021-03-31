from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json
import os
from linebot.exceptions import LineBotApiError

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import random
import csv
import re
import requests
from msg_template import Gps,Weather,Flex_template,Text_template

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
#----------------取得userid-----------------
    user_id = event.source.user_id
    if user_id == '':
        user_id = event.source.user_id
    TWregion = ["北部","中部","南部","東部"]
    city_name = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]
    city_name_dic = {**n_dict, **c_dict, **s_dict, **e_dict}
    city_region_dict = dict(zip(["north","center","south","east"], [north,center,south,east]))

#----------------拉麵推薦介面-----------------
    if event.message.text == "拉麵推薦":
        flex_message0 = Flex_template.main_panel_flex()
        line_bot_api.reply_message(event.reply_token,flex_message0)
#----------------不同區域的介面設定-----------------

    elif event.message.text in TWregion:
            #讀需要的json資料
        f_region = open('json_files_for_robot/json_for_app.json', encoding="utf8") 
        data_region = json.load(f_region) 

        for i,v in enumerate(TWregion):
            if event.message.text == v:
                flex_message1 = FlexSendMessage(
                               alt_text= v + '的縣市',
                               contents= data_region[i]
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
        flex_message5 = Flex_template.soup_direct_flex(event.message.text)
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
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.error_warning_text('O1')) )
            
                flex_message9 = Flex_template.double_flex("快回來看看我幫你找到的店家！", store_n, address, lon, lat, descrip, trans, op, "看同類推薦", user_choice, f_city, comment, "+到最愛", "加到最愛清單")
                line_bot_api.reply_message(event.reply_token,flex_message9)

            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = f"資料庫有誤"))
            
    elif ' ' in event.message.text and ' ' not in event.message.text[-1] and ' ' not in event.message.text[0]:
        user_select = event.message.text
        if "有人評論→" in user_select:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.warm_msg()))
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
            weather_result = Weather.query_local_weather(lonti,lati,WEATHER_API_KEY,store_name)
            if weather_result != '':
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = weather_result))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.error_warning_text('W1'))
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
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.keyword_warning_text()))
            else:
                output_before_random_clear = get_data_str(keyword_result)
                if output_before_random_clear == None:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.keyword_warning_text()))
                else:
                    output_before_random_clear = output_before_random_clear.replace(u'\xa0', u' ').replace('\n','')
                    #---------------------------------change data to a list of datas--------------------------
                    output_whole_lst = convert_string_to_lst(output_before_random_clear,'%')
                    output_whole_lst = [i for i in output_whole_lst if i]
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
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.error_warning_text('S1')) )
                        flex_message3 = Flex_template.double_flex("快來看你搜索到的店！", store_n, address, lon, lat, descrip, trans, op, "再搜索一次", user_select, f_city, comment, "+到最愛", "加到最愛清單")
                        line_bot_api.reply_message(event.reply_token,flex_message3)
                    else:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.error_warning_text('S3'))
        )       

    elif ' ' in event.message.text and (' ' in event.message.text[-1] or ' '  in event.message.text[0]):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.keyword_warning_text()))
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
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.error_warning_text('L2'))
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

            flex_message7 = Flex_template.single_flex('快來看看你的清單~', r_store, ad, lont, lati, dis, trans, opent, city_r, com_format,'刪除最愛','刪除最愛清單')
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

            flex_message8 = Flex_template.single_flex('快來看看店家細節~', r_store, ad, lont, lati, dis, trans, opent, city_r, com_format,"+到最愛","加到最愛清單")
            line_bot_api.reply_message(event.reply_token,flex_message8)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.error_warning_text('D1'))
        )       
        
#----------------問題回報（未來可加donate資訊）----------------
    elif event.message.text == "問題回報":
        line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= Text_template.user_report()))

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = Text_template.keyword_warning_text()))

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
      else:
        #search all
        all_store_province = province_soup_q = db.session.query(Main_store, Store)\
                          .outerjoin(Store, Store.store_id == Main_store.store_id)\
                          .filter(Store.still_there == True)
        break
    
    # '''
    # 算距離
    # '''
    if all_store_province == '':
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=Text_template.error_warning_text('P1'))) 
    else:
        sorted_city_distance_dic = Gps.caculate_distance(user_location,all_store_province)
        if  len(sorted_city_distance_dic) >= 10:
            choice_nearby_city = Gps.take(10, sorted_city_distance_dic.items())
            if choice_nearby_city[0][1][0] > 395:
                text_message_foreign_location = TextSendMessage(text="\udbc0\udc7B目前不支援離島與國外拉麵店，請到台灣本島吃拉麵Yeah We only support ramen shops in Taiwan~",
                                                  quick_reply=QuickReply(items=[
                                                      QuickReplyButton(action=LocationAction(label="再定位一次My LOC"))
                                                  ]))
                line_bot_api.reply_message(event.reply_token,text_message_foreign_location) 
            else:
                choice_nearby_city_tup = choice_nearby_city
        
        else:
          line_bot_api.reply_message(event.reply_token,TextSendMessage(text=  Text_template.error_warning_text('G2') ))

    
    flex_message_location = FlexSendMessage(
                                        alt_text='快回來看看我幫你找到的店家！',
                                        contents= Gps.distance_template_generator(choice_nearby_city_tup),
                                        quick_reply= QuickReply(items=[QuickReplyButton(action=LocationAction(label="再定位一次My LOC")),
                                                                       QuickReplyButton(action=URIAction(label="拉麵地圖自己找",uri=f'https://www.google.com/maps/d/u/0/viewer?fbclid=IwAR3O8PKxMuqtqb2wMKoHKe4cCETwnT2RSCZSpsyPPkFsJ6NpstcrDcjhO2k&mid=1I8nWhKMX1j8I2bUkN4qN3-FSyFCCsCh7&ll={u_lat}%2C{u_long}'))
                                                                       ]))
    line_bot_api.reply_message(event.reply_token,flex_message_location)
        
if __name__ == 'main':
    app.run(debug=True) 
        

 

