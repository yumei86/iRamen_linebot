from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import json

app = Flask(__name__)

line_bot_api = LineBotApi('Zt18oeL1jEzB9bbOw3BjRbMC9u8q4FwJkV2J7wlRd9G+GY5D8HHrShTSGZRK7uIKTAbqmImphpl3/U2G2B3wFLshfMnvqVCsZW+lWZrxUT3XOMma0KcbeLxwc9v7DdTbtRyi/UedtsR7jJE3NSquLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('18a7d98e70f62d369081d4d82c88a1e3')

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
    f = open('json_for_app.json') 
    data = json.load(f) 

    if event.message.text == "拉麵推薦":

        flex_message = FlexSendMessage(
                        alt_text='拉麵推薦',
                        contents= data[0]
        )

        line_bot_api.reply_message(event.reply_token,flex_message)


#----------------不同區域的介面設定-----------------
        
    elif event.message.text == "北部":
        flex_message1 = FlexSendMessage(
                        alt_text='北部的縣市',
                        contents=  data[1]
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message1) 
       
    elif event.message.text == "中部":
            
        flex_message2 = FlexSendMessage(
                        alt_text='中部的縣市',
                        contents= data[2]
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message2) 
    
    elif event.message.text == "南部":
        flex_message3 = FlexSendMessage(
                        alt_text='南部的縣市',
                        contents= data[3]
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message3) 

    elif event.message.text == "東部":
        flex_message4 = FlexSendMessage(
                        alt_text='東部的縣市',
                        contents= data[4]
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message4) 

#----------------湯頭/直接推薦介面-----------------

    cityname = ["台北市","新北市","基隆市","桃園市","苗栗縣","新竹縣","新竹市","台中市","彰化市","南投縣","雲林縣","嘉義市","台南市","高雄市","屏東縣","宜蘭縣","花蓮縣","台東縣"]

    elif event.message.text == "台北市":
        flex_message5 = FlexSendMessage(
                        alt_text='依據你的喜好選擇吧！',
                        contents= data[5]
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message5) 

