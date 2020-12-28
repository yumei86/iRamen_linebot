from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json
import os
from linebot.exceptions import LineBotApiError

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

#----------------直接打字query店家的部分-----------------
def query_store(stores,store2):
    store_direct = db.session.query(Main_store, Store, Post)\
                        .outerjoin(Post, Post.store_id == Main_store.store_id)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.store.contains(stores))\
                        .filter(Store.store.contains(store2))
                        
    return store_direct
def query_store_direct(stores):
    store_direct = db.session.query(Main_store, Store, Post)\
                        .outerjoin(Post, Post.store_id == Main_store.store_id)\
                        .outerjoin(Store, Store.store_id == Main_store.store_id)\
                        .filter(Store.store.contains(stores))
    return store_direct
#----------------------------------------------------


def convert_string_to_lst(string,c): 
    li = list(string.split(c)) 
    return li 

##----------------我的最愛取得userid資料庫設定-----------------
def get_store_id(store_name):
    store_id_q = db.session.query(Store)\
        .filter(Store.store == store_name)
    for data in store_id_q:
        get_id = data.detail_store_id
    return get_id
def store_exist(store_name):
    store_exist = db.session.query(Store, Favorite)\
            .join(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
            .filter(Store.store == store_name).count()
    return store_exist
def count_love_list(user_id):
    count_love_list = db.session.query(Favorite)\
            .filter(Favorite.line_id == user_id).count()
    return count_love_list
def count_total_row(database_name):
    count_total_row = db.session.query(database_name).count()
    return count_total_row


##----------------Query love-list by userID----------------
def get_list_from_user_id(user_id):  
    love_list_q = db.session.query(Store,Favorite)\
        .outerjoin(Favorite, Favorite.detail_store_id == Store.detail_store_id)\
        .filter(Favorite.line_id == user_id)
    return love_list_q


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
                                        action=MessageAction(label=i, text=i),)
        delete_button = ButtonComponent(style="secondary", color="#F1DCA7", size="sm", margin="sm", flex=0,
                                      action=MessageAction(label="-", text="刪除最愛清單:"+i),)
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

#----------------取得userid-----------------
    user_id = event.source.user_id

    if user_id == '':
        user_id = event.source.user_id
        

#----------------該id的最愛清單database-----------------
    love_lst_q = get_list_from_user_id(user_id)
    love_list = ''
    for l in love_lst_q:
        love_list += f'STORE:{l[0].store},ADDRESS:{l[0].address},DISCRIPTION:{l[0].discription},TRANSPORT:{l[0].transport},\
                      MAP_REVIEW:{l[0].map_review},CITY:{l[0].province},\
                      LONGITUDE:{l[0].longtitute},LATITUDE:{l[0].latitude},\
                      OPEN_TIME:{l[0].open_time},CHECK_TAG:{l[0].soup}%'
    love_list_clear = love_list.replace(u'\xa0', u' ').replace(' ','')
    output_whole_love_list = convert_string_to_lst(love_list_clear,'%')
    for data in output_whole_love_list:
        if data == '':
            output_whole_love_list.remove(data)

    ramen_test = []
    
    for j in range(len(output_whole_love_list)):
        temp_lst = output_whole_love_list[j].split(",")
        ramen_test.append(temp_lst[0][temp_lst[0].index(':')+1:])
        
        ad = temp_lst[1][temp_lst[1].index(':')+1:]
        dis = temp_lst[2][temp_lst[2].index(':')+1:]
        trans = temp_lst[3][temp_lst[3].index(':')+1:]
        com = temp_lst[4][temp_lst[4].index(':')+1:]
        city_r = temp_lst[5][temp_lst[5].index(':')+1:]
        lont = temp_lst[6][temp_lst[6].index(':')+1:]
        lati = temp_lst[7][temp_lst[7].index(':')+1:]
        opent = temp_lst[10][temp_lst[10].index(':')+1:]
        r_store = ramen_test[j]
        

#----------------最愛清單店家資訊msg-----------------
        if event.message.text == r_store:

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
                                                        "text": "刪除最愛清單:"+r_store
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
                                                        "text": "正在幫你找到:\n"+lont+":"+lati
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
                                                    "text": "看更多推薦:"+city_r
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
                                                        "text": "刪除最愛清單:"+r_store
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
                                                    "text": com
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
                                                    "text": "看更多推薦:"+city_r
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

            line_bot_api.reply_message(event.reply_token,flex_message7)



#----------------最愛清單加入資料庫設定與訊息回覆設定-----------------
      
    if "加到最愛清單" in event.message.text:

        user_line_id = user_id

        text_l = event.message.text.split(":")
        
        first_love_param = text_l[0]
        second_love_param = text_l[1] 

        if first_love_param == '加到最愛清單':
            favorite_list_count = count_love_list(user_line_id) #how many items a user save
            already_add_store_count = store_exist(second_love_param) #check if the store user want to add already exist in the list
            get_foreign_id = get_store_id(second_love_param)#check the map_id(foreign key) of the store

        if favorite_list_count == 0 or\
            favorite_list_count != 0 and already_add_store_count == 0 and favorite_list_count <= 25 :
            data = Favorite(user_line_id,get_foreign_id)
            db.session.add(data)
            db.session.commit()

            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="已經把" + second_love_param + "加進最愛清單！")
                )
        elif favorite_list_count > 25:

            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="最愛清單數量超過上限，請刪除部分資料\udbc0\udc7c")
                )
        else:
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= second_love_param + "已經在最愛清單！")
                )

    if "刪除最愛清單" in event.message.text:
 
        text_d = event.message.text.split(":")

        #first_del_param = text_d[0]
        second_del_param = text_d[1]

        detail_id = get_store_id(second_del_param)

        if detail_id != '' and store_exist(second_del_param) == 1:
            data = db.session.query(Favorite)\
                    .filter(Favorite.detail_store_id == detail_id).first()
            db.session.delete(data)
            db.session.commit()
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="成功刪除"+ second_del_param )
                )

        elif store_exist(second_del_param) == 0: #check if the store user want to rermove already not exist in the list
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= second_del_param + "已不在你的最愛清單囉!" )
                )
        
        else:
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text= "發生錯誤請再試一次" )
                )


#----------------最愛清單訊息觸發設定-----------------  
    if event.message.text == "最愛清單":

        if ramen_test == []:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "尚未有最愛清單，快去加入你喜歡的拉麵吧！\uDBC0\uDC5e"))
        else:
            flex_message6 = FlexSendMessage(
                                        alt_text= '快回來看看我的最愛！',
                                        contents= favorite_list_generator(ramen_test)
            )
            line_bot_api.reply_message(event.reply_token,flex_message6) 

#----------------問題回報（未來可加donate資訊）----------------
    if event.message.text == "問題回報":
        line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="常見問題:\n\udbc0\udcb2我的反應太慢:\n因為目前我的雲端伺服器有時會睡眠，請等待個幾秒鐘。\
                                        \n\udbc0\udcb2選擇湯頭和評論品項不同:\n別擔心，該推薦店家是有賣你選的湯頭類型！\
                                        \n\udbc0\udcb2更多資訊請到「台灣拉麵愛好會」觀看，我們的資料皆由此社團取得。\
                                        \n\udbc0\udc84若你很喜歡我們的作品，也不吝嗇贊助，讓我們的iRamen變得更好，請匯款至以下戶頭:\n玉山銀行(808)0864979119334\
                                        \n\
                                        \n若以上的問題清單都不是你情況，請填寫表單，非常感謝你！\udbc0\udc7a\
                                        \nhttps://reurl.cc/14RmVW")

        )
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
                                                        "text": "正在幫你找到:\n"+lon+":"+lat
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
                                                        "text": "正在幫你找到:\n"+lon+":"+lat
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

        text_list = event.message.text.split(":")
        lonti = float(text_list[1])
        lati  = float(text_list[2])
        line_bot_api.reply_message(event.reply_token,LocationSendMessage(title='點擊帶你前往！',address='iRamen',latitude= lati,longitude= lonti))
    
#----------------選完湯頭介面/湯頭看更多類似推薦-----------------

    #各縣市湯頭清單
    #北部
    taipei = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "味噌", "淡麗系", "其他"]
    new_taipei = ["豚骨", "醬油", "雞白湯", "雞骨魚介", "沾麵", "雞清", "淡麗系", "煮干", "素食", "其他"]
    keelung = ["豚骨", "素食", "限定"]
    taoyuan = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "柑橘", "淡麗", "煮干", "其他"]
    miaoli = ["豚骨", "咖哩","雞骨"]
    hsinchu_county = ["豚骨"]
    hsinchu_city = ["豚骨", "醬油", "二郎", "沾麵" , "雞清", "家系" , "素食", "背脂", "淡麗系" , "其他"]

    #中部
    taichung = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "辣味噌", "泡系", "其他"]
    chuanghua = ["豚骨", "雞白湯", "家系", "鴨清", "鴨白", "限定", "雞湯"]
    nantou = ["豚骨", "其他"]
    yunlin = ["雞白", "魚介雞湯", "限定"]

    #南部
    chiayi = ["豚骨", "沾麵", "家系", "二郎風", "限定", "變化"]
    tainan = ["豚骨", "雞白湯", "豚骨魚介", "沾麵", "二郎", "素食", "咖哩", "淡麗系", "煮干", "其他"]
    kaohsiung = ["豚骨", "醬油", "雞白湯", "豚骨魚介", "沾麵", "雞清", "家系", "雞豚", "淡麗", "其他"]
    pintung = ["豚骨", "醬油", "雞白", "雞清", "家系", "雞濃", "限定", "其他"]

    #東部
    yilan = ["豚骨", "三星蔥", "其他"]
    hualien = ["豚骨", "魚白", "鬼頭刀", "其他"]
    taitung = ["豚骨", "其他"]

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
                                                        "text": "↓↓點擊下方地址可以直接幫你傳送地址！",
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
                                                        "text": "正在幫你找到:\n"+lon+":"+lat
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

#----------------輸入關鍵字找尋店家-----------------
    
    if " " in event.message.text:

        user_select = event.message.text

        if ' ' in user_select and ' ' not in user_select[-1] and ' ' not in user_select[0]:
            input_store = ''
            input_location = ''
            input_lst = user_select.split()
            if len(input_lst) == 2:
                    input_store += input_lst[0]
                    input_location += input_lst[1]
            result = query_store(input_store,input_location)
        elif ' ' in user_select[-1] or ' ' in user_select[0]:
            result = ''
        else:
            result = query_store_direct(user_select)

        #---------------------------------put all data in a string--------------------------
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
        try:
            output_s = secrets.choice(output_whole_lst)
            output_lst = convert_string_to_lst(output_s, ',')

        except IndexError:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n例如\n\"鷹流 中山\",\"一風堂 桃園\"\
                                                                                  \n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我留空,但不可在前後加入空白)\
                                                                                  \n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！")
            )
        
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
            f_city = output_lst[10][output_lst[10].index(':')+1:]


        elif len(output_lst) == 9:
            #googleMap
            comment = output_lst[4][output_lst[4].index(':')+1:]
            lon = output_lst[5][output_lst[5].index(':')+1:]
            lat = output_lst[6][output_lst[6].index(':')+1:]  
            f_city = output_lst[8][output_lst[8].index(':')+1:]

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
                                                            "text": "↓↓點擊下方地址可以直接幫你傳送地址！",
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
                                                            "text": "正在幫你找到:\n"+lon+":"+lat
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
                                                        "text": "看更多推薦:"+ f_city
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
                                                        "text": "看更多推薦:"+ f_city
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

    elif ":" not in event.message.text:

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n例如\n\"鷹流 中山\",\"一風堂 桃園\"\
                                                                                  \n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我留空,但不可在前後加入空白)\
                                                                                  \n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！")
        )
        
if __name__ == 'main':
    app.run(debug=True) 
        

 

