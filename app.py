from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)


line_bot_api = LineBotApi('Zt18oeL1jEzB9bbOw3BjRbMC9u8q4FwJkV2J7wlRd9G+GY5D8HHrShTSGZRK7uIKTAbqmImphpl3/U2G2B3wFLshfMnvqVCsZW+lWZrxUT3XOMma0KcbeLxwc9v7DdTbtRyi/UedtsR7jJE3NSquLQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('18a7d98e70f62d369081d4d82c88a1e3')

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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    #print(type(msg))
    msg = msg.encode('utf-8')  

    if event.message.text == "拉麵推薦":
        flex_message = FlexSendMessage(
        alt_text='hello',
        contents={
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://media.timeout.com/images/105665255/630/472/image.jpg",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "uri": "http://linecorp.com/"
    },
    "position": "relative"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "你在哪裡？",
        "weight": "bold",
        "size": "xl",
        "contents": []
      },
      {
        "type": "text",
        "text": "請選擇你在台灣的哪裡 ",
        "size": "xs",
        "color": "#888888"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "北部",
              "text": "北部"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "中部",
              "text": "中部"
            },
            "style": "secondary",
            "margin": "xxl",
            "height": "sm"
          }
        ],
        "margin": "md"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "南部",
              "text": "南部"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "東部",
              "text": "東部"
            },
            "style": "secondary",
            "margin": "xxl",
            "height": "sm"
          }
        ],
        "margin": "md"
      }
    ]
  },
}
        )

        line_bot_api.reply_message(event.reply_token,flex_message)



    elif event.message.text == "錯誤回報":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請點選以下連結：https://reurl.cc/14RmVW"))

        
        
    elif event.message.text == "北部":
        flex_message1 = FlexSendMessage(
        alt_text='北部的縣市',
        contents= {
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://github.com/yumei86/iRamen_linebot/blob/master/image/northtw.png?raw=true",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "uri": "http://linecorp.com/"
    }
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "你在哪個縣市？",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "text",
        "text": "請幫助我選擇縣市讓你更快得到推薦喔！",
        "size": "xs",
        "margin": "lg",
        "color": "#888888"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "台北市",
              "label": "台北市"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "新北市",
              "text": "新北市"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "基隆市",
              "label": "基隆市"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "桃園市",
              "text": "桃園市"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "新竹市",
              "label": "新竹市"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "新竹縣",
              "text": "新竹縣"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "苗栗縣",
              "label": "苗栗縣"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "text",
            "text": " ",
            "margin": "xxl"
          }
        ],
        "margin": "md"
      }
    ]
  }
}
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message1) 
       
    elif event.message.text == "中部":
            
        flex_message2 = FlexSendMessage(
        alt_text='中部的縣市',
        contents={
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://github.com/yumei86/iRamen_linebot/blob/master/image/centraltw.png?raw=true",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "uri": "http://linecorp.com/"
    }
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "你在哪個縣市？",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "text",
        "text": "請幫助我選擇縣市讓你更快得到推薦喔！",
        "size": "xs",
        "margin": "lg",
        "color": "#888888"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "台中市",
              "label": "台中市"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "彰化縣",
              "text": "彰化縣"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "南投縣",
              "text": "南投縣"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "雲林縣",
              "text": "雲林縣"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      }
    ]
  }
} 

        )
        
        line_bot_api.reply_message(event.reply_token,flex_message2) 
    
    elif event.message.text == "南部":
        flex_message3 = FlexSendMessage(
        alt_text='南部的縣市',
        contents={
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://github.com/yumei86/iRamen_linebot/blob/master/image/southtw.png?raw=true",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "uri": "http://linecorp.com/"
    }
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "你在哪個縣市？",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "text",
        "text": "請幫助我選擇縣市讓你更快得到推薦喔！",
        "size": "xs",
        "margin": "lg",
        "color": "#888888"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "嘉義市",
              "label": "嘉義市"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "嘉義縣",
              "text": "嘉義縣"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "台南市",
              "label": "台南市"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "高雄市",
              "text": "高雄市"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "屏東縣",
              "label": "屏東縣"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "text",
            "text": " ",
            "margin": "xxl"
          }
        ],
        "margin": "md"
      }
    ]
  }
}
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message3) 

    elif event.message.text == "東部":
        flex_message4 = FlexSendMessage(
        alt_text='東部的縣市',
        contents={
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://github.com/yumei86/iRamen_linebot/blob/master/image/easttw.png?raw=true",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "uri": "http://linecorp.com/"
    }
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "你在哪個縣市？",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "text",
        "text": "請幫助我選擇縣市讓你更快得到推薦喔！",
        "size": "xs",
        "margin": "lg",
        "color": "#888888"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "宜蘭縣",
              "label": "宜蘭縣"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "花蓮縣",
              "text": "花蓮縣"
            },
            "style": "secondary",
            "height": "sm",
            "margin": "xxl"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "text": "台東縣",
              "label": "台東縣"
            },
            "style": "secondary",
            "height": "sm"
          },
          {
            "type": "text",
            "text": " ",
            "margin": "xxl"
          }
        ],
        "margin": "md"
      }
    ]
  }
}
        )
        
        line_bot_api.reply_message(event.reply_token,flex_message4) 
