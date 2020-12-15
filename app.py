from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json
import os

#----------------互叫我們的line bot(這邊直接取用herohu的環境變數)-----------------

app = Flask(__name__)

USER = os.environ.get('CHANNEL_ACCESS_TOKEN')
PASS = os.environ.get('CHANNEL_SECRET')

line_bot_api = LineBotApi(USER)
handler = WebhookHandler(PASS)


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

    elif event.message.text == "最愛清單":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "尚未有最愛清單，快去加入你喜歡的拉麵吧！\uDBC0\uDC5e"))


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

    cityname = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化縣","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]

    for city in cityname:
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
    address = "query出來的地址"
    
    for city in cityname:
        cond = "直接推薦:"+city
        if event.message.text == cond :

            flex_message3 = FlexSendMessage(
                            alt_text='快回來看看我幫你找到的店家！',
                            contents={
                                        "type": "carousel",
                                        "contents": [
                                        {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                "type": "text",
                                                "text": "query出來的店家名",
                                                "align": "start",
                                                "size": "md",
                                                "gravity": "center",
                                                "color": "#ffffff"
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
                                                        "text": "加到最愛清單"
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
                                                    "text": "query出來的特色",
                                                    "size": "sm",
                                                    "wrap": True
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
                                                    "text": "query出來的交通資訊"
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
                                                    "label": "看更多類似推薦",
                                                    "text": "看更多類似推薦:"+city
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
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                "type": "text",
                                                "text": "query出來的店家名",
                                                "align": "start",
                                                "size": "md",
                                                "gravity": "center",
                                                "color": "#ffffff"
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
                                                        "text": "加到最愛清單"
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
                                                    "text": "網友評論1：",
                                                    "color": "#797D62",
                                                    "size": "md",
                                                    "wrap": True,
                                                    "weight": "bold"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": "query出來的網友評論"
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
                                                    "label": "看更多類似推薦",
                                                    "text": "看更多類似推薦:"+city
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
            
            #----------------位置經緯度資訊-----------------

            if event.message.text == address:

                location_message = LocationSendMessage(
                        title= 'location',
                        address= address,
                        latitude=35.65910807942215,
                        longitude=139.70372892916203
                        )
                line_bot_api.reply_message(event.reply_token,location_message)



#----------------選完湯頭介面/湯頭看更多類似推薦-----------------

    #各縣市湯頭清單
    #北部
    taipei = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "雞豚", "淡麗系", "其他"]
    new_taipei = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "淡麗系", "煮干", "素食"]
    keelung = ["豚骨", "素食"]
    taoyuan = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "柑橘", "淡麗系", "煮干", "大骨"]
    miaoli = ["豚骨", "咖哩"]
    hsinchu_county = ["豚骨"]
    hsinchu_city = ["豚骨", "醬油", "魚介", "雞清", "素食", "背脂", "淡麗系"]

    #中部
    taichung = ["豚骨", "醬油", "雞白", "魚介", "沾麵", "雞清", "家系", "雞豚", "味噌", "其他"]
    chuanghua = ["豚骨", "雞白", "家系"]
    nantou = ["豚骨"]
    yunlin = ["豚骨", "雞白", "魚介"]

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
        cond = str(cityname[i])+":"
        soup = city_soup[i]
        for item in soup:
            n = cond+item
            if event.message.text == n:

                flex_message4 = FlexSendMessage(
                            alt_text='快回來看看我幫你找到的店家！',
                            contents={
                                        "type": "carousel",
                                        "contents": [
                                        {
                                            "type": "bubble",
                                            "size": "mega",
                                            "header": {
                                            "type": "box",
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                "type": "text",
                                                "text": "query出來的店家名",
                                                "align": "start",
                                                "size": "md",
                                                "gravity": "center",
                                                "color": "#ffffff"
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
                                                        "text": "加到最愛清單"
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
                                                    "text": "query出來的地址",
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": "的傳送門"
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
                                                    "text": "query出來的特色",
                                                    "size": "sm",
                                                    "wrap": True
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
                                                    "text": "query出來的交通資訊"
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
                                                    "label": "看更多類似推薦",
                                                    "text": "看更多類似推薦:"+cityname[i]
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
                                            "layout": "vertical",
                                            "contents": [
                                                {
                                                "type": "text",
                                                "text": "query出來的店家名",
                                                "align": "start",
                                                "size": "md",
                                                "gravity": "center",
                                                "color": "#ffffff"
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
                                                        "text": "加到最愛清單"
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
                                                    "color": "#797D62",
                                                    "size": "md",
                                                    "wrap": True,
                                                    "weight": "bold"
                                                    },
                                                    {
                                                    "type": "text",
                                                    "size": "sm",
                                                    "wrap": True,
                                                    "text": "query出來的網友評論"
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
                                                    "label": "看更多類似推薦",
                                                    "text": "看更多類似推薦:"+cityname[i]
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


