from linebot.models import FlexSendMessage
def main_panel_flex():
    flex_message = FlexSendMessage(
                    alt_text='拉麵推薦',
                    contents= {
                                "type": "bubble",
                                "hero": {
                                  "type": "image",
                                  "url": "https://github.com/yumei86/iRamen_linebot/blob/master/image/TWmap.png?raw=true",
                                  "size": "full",
                                  "aspectRatio": "20:13",
                                  "aspectMode": "cover",
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
                                      "contents": [],
                                      "color": "#876C5A"
                                    },
                                    {
                                      "type": "text",
                                      "text": "請幫助我選擇你在台灣的哪個位置：）",
                                      "size": "xs",
                                      "margin": "sm"
                                    },
                                    {
                                      "type": "separator",
                                      "margin": "lg"
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
                                          "style": "primary",
                                          "height": "sm",
                                          "color": "#797D62"
                                        },
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "中部",
                                            "text": "中部"
                                          },
                                          "style": "primary",
                                          "margin": "xxl",
                                          "height": "sm",
                                          "color": "#797D62"
                                        }
                                      ],
                                      "margin": "lg"
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
                                          "style": "primary",
                                          "height": "sm",
                                          "color": "#797D62"
                                        },
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "東部",
                                            "text": "東部"
                                          },
                                          "style": "primary",
                                          "margin": "xxl",
                                          "height": "sm",
                                          "color": "#797D62"
                                        }
                                      ],
                                      "margin": "md"
                                    },
                                    {
                                      "type": "separator",
                                      "margin": "lg"
                                    },
                                    {
                                      "type": "box",
                                      "layout": "vertical",
                                      "contents": [
                                        {
                                          "type": "button",
                                          "action": {
                                            "type": "message",
                                            "label": "開定位探店GPS",
                                            "text": "定位"
                                          },
                                          "style": "primary",
                                          "margin": "xxl",
                                          "height": "sm",
                                          "color": "#797D62"
                                        }
                                      ]
                                    }
                                  ]
                                }
                    }
    )
    return flex_message

def soup_direct_flex(whole_input):
    flex_message = FlexSendMessage(
                    alt_text='依據你的喜好選擇吧！',
                    contents= {
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
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                        "type": "button",
                                        "style": "primary",
                                        "height": "sm",
                                        "action": {
                                            "type": "message",
                                            "label": "湯頭推薦",
                                            "text": "湯頭推薦:"+whole_input
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
                                            "text": "直接推薦:"+whole_input
                                        },
                                        "color": "#797D62",
                                        "margin": "md"
                                        },
                                        {
                                        "type": "separator",
                                        "margin": "lg"
                                        },
                                        {
                                          "type": "box",
                                          "layout": "horizontal",
                                          "contents": [
                                            {
                                              "type": "button",
                                              "action": {
                                                "type": "message",
                                                "label": "突然想開定位GPS",
                                                "text": "定位"
                                              },
                                              "style": "primary",
                                              "margin": "xxl",
                                              "height": "sm",
                                              "color": "#797D62"
                                            }
                                          ]
                                        }
                                    ]
                                }
                    }
        )
    return flex_message

def single_flex(whole_alt,whole_store,whole_address,whole_longtitude,whole_latitude,whole_description,whole_transport,whole_open_time,whole_city,whole_comment,add_or_delete,add_or_delete_label):
    flex_message = FlexSendMessage(
                            alt_text= whole_alt,
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
                                                "text": whole_store,
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
                                                    "text": add_or_delete,
                                                    "size": "sm",
                                                    "align": "center",
                                                    "offsetTop": "3px",
                                                    "action": {
                                                        "type": "message",
                                                        "label": add_or_delete_label,
                                                        "text": add_or_delete_label+'♡'+whole_store
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
                                                    "text": whole_address,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": f"正在幫你找到→ \n{whole_longtitude}→{whole_latitude}"
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
                                                    "text": whole_description,
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
                                                    "text": whole_transport,
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
                                                    "text": whole_open_time,
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
                                                    "text": f"\udbc0\udc54有人評論→ {whole_store}\n\n{whole_comment}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看當地天氣",
                                                    "text": f"{whole_store} 附近天氣搜索中→ \n{whole_longtitude}→{whole_latitude}"
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
                                                    "text": f"類別搜索中→{whole_store}→{whole_city}"
                                                },
                                                "color": "#D08C60"
                                                },
                                                {
                                                "type": "button",
                                                "action": {
                                                    "type": "message",
                                                    "label": "看更多推薦",
                                                    "text": "看更多推薦:"+whole_city
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
    return flex_message


def double_flex(whole_alt, whole_store, whole_address, whole_longtitude, whole_latitude, whole_description, whole_transport, whole_open_time, whole_input_label, whole_input, whole_city, whole_comment, add_or_delete, add_or_delete_label):#pass 14 values
    flex_message =  FlexSendMessage(
                        alt_text= whole_alt,
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
                                                    "text": whole_store,
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
                                                        "text": add_or_delete,
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": add_or_delete_label,
                                                        "text": add_or_delete_label+'♡'+whole_store
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
                                                    "text": whole_address,
                                                    "action": {
                                                        "type": "message",
                                                        "label": "action",
                                                        "text": f"正在幫你找到→ \n{whole_longtitude}→{whole_latitude}"
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
                                                        "text": whole_description,
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
                                                        "text": whole_transport,
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
                                                    "text": whole_open_time,
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
                                                    "label": whole_input_label,
                                                    "text": whole_input
                                                    },
                                                    "color": "#D08C60"
                                                },
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看相似店鋪",
                                                    "text": f"類別搜索中→{whole_store}→{whole_city}"
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
                                                    "text": whole_store,
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
                                                        "text": add_or_delete,
                                                        "size": "sm",
                                                        "align": "center",
                                                        "offsetTop": "3px",
                                                        "action": {
                                                        "type": "message",
                                                        "label": add_or_delete_label,
                                                        "text": add_or_delete_label+'♡'+whole_store
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
                                                        "text": whole_comment
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
                                                    "text": f"輸出評論超連結→{whole_store}"
                                                    },
                                                    "color": "#D08C60"
                                                },
                                                {
                                                    "type": "button",
                                                    "action": {
                                                    "type": "message",
                                                    "label": "看當地天氣",
                                                    "text": f"{whole_store} 附近天氣搜索中→ \n{whole_longtitude}→{whole_latitude}"
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
    return flex_message

