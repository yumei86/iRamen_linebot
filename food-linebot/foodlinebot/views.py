from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent,
    PostbackEvent,
    TextSendMessage
)

from .scraper import IFoodie
from .messages import AreaMessage, CategoryMessage, PriceMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):

    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件

                if event.message.text == "哈囉":

                    line_bot_api.reply_message(  # 回復「選擇地區」按鈕樣板訊息
                        event.reply_token,
                        AreaMessage().content()
                    )

            elif isinstance(event, PostbackEvent):  # 如果有回傳值事件

                if event.postback.data[0:1] == "A":  # 如果回傳值為「選擇地區」

                    line_bot_api.reply_message(   # 回復「選擇美食類別」按鈕樣板訊息
                        event.reply_token,
                        CategoryMessage(event.postback.data[2:]).content()
                    )

                elif event.postback.data[0:1] == "B":  # 如果回傳值為「選擇美食類別」

                    line_bot_api.reply_message(   # 回復「選擇美食類別」按鈕樣板訊息
                        event.reply_token,
                        PriceMessage(event.postback.data[2:]).content()
                    )

                elif event.postback.data[0:1] == "C":  # 如果回傳值為「選擇消費金額」

                    result = event.postback.data[2:].split('&')  # 回傳值的字串切割

                    food = IFoodie(
                        result[0],  # 地區
                        result[1],  # 美食類別
                        result[2]  # 消費價格
                    )

                    line_bot_api.reply_message(  # 回復訊息文字
                        event.reply_token,
                        # 爬取該地區正在營業，且符合所選擇的美食類別及消費價格的前五大最高人氣餐廳
                        TextSendMessage(text=food.scrape())
                    )

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
