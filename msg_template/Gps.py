from vincenty import vincenty
from itertools import islice
from linebot.models import *

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