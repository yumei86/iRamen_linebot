import random

def keyword_warning_text():
    store_example = ['「鷹流 公館」','「公 子」','「山下公 園」','「隱家 赤峰」','「七 面鳥」','「麵屋 壹」','「真 劍」','「秋 鳴」','「Mr 拉麵雲」','「辰 拉」','「京都 柚子」','「麵屋 ichi」','「麵屋 壹之穴」','「KIDO 拉麵」','「Ramen 初」','「暴 走」','「Hiro 新店」']
    random.shuffle(store_example)
    store_example_choice_lst = store_example[:5]
    store_example_choice = ''.join(store_example_choice_lst)
    # store_example_choice = reduce(lambda a,x: a+str(x), store_example_choice_lst, "")
    warning_text = f"\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n\n例:{store_example_choice}\n\n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我隨意留一個半形空,但不可在前後加入空白)\n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！"
    return warning_text

def error_warning_text(err_code):
    err_msg = f"\udbc0\udcb2出錯啦靠邀，麻煩您把「錯誤代碼{err_code}」和「您的店家搜尋指令（含空格）」填在填錯誤回報上，感激到五體投地\udbc0\udcb2"
    return err_msg

def user_report():
    report_text =f"\udbc0\udcb2常見問題\n\n• 選擇湯頭和評論品項不同:\n別擔心，該推薦店家是有賣你選的湯頭類型！\
                    \n\
                    \n• 希望有較小範圍的地區搜尋功能:\n已經上線了。\
                    \n\
                    \n\udbc0\udcb25月新增\n\n• 機器人後台提升（特別感謝「拉麵機器人加油」網友協助）\n\n• 一同抵抗corona，請各位麵友待在家「阻斷傳播鍊」\
                    \n\
                    \n\udbc0\udc84更多心得請至臉書社團「台灣拉麵愛好會」觀看\
                    \n\
                    \n歡迎請填寫使用者回饋表單，非常感謝你！\udbc0\udc7a\
                    \nhttps://reurl.cc/14RmVW"
    return report_text 

def warm_msg():
    warm_msg_lst = ['拉麵不分貴賤','No Ramen no life，Wear mask to improve your life','拉麵是恆久忍耐又有恩慈，口罩也是','防疫期間請待在家煮拉麵','用拉麵和口罩抵擋水逆！','人與麵的連結','趁年輕多在家吃拉麵','防疫為重，拉麵濃淡皆宜自煮為佳','總是需要一碗拉麵，哪怕是一點點自以為是的紀念','總有一碗麵一直住在心底，卻消失在生活里','拉麵可以隨遇而安，防疫不行','希望所有的防疫都不會被辜負，所有的拉麵都不會冷掉','拉麵是留給堅持防疫的人','比一個人吃拉麵更寂寞的是一個人沒有錢吃拉麵','眼淚不是答案，拉麵才是選擇','一個人之所以強大，是因為他一同防疫，並且搞清楚自己想要吃的拉麵','有些事讓你一夜長大，有些麵讓你一夜感謝']
    warm_msg_content = f"{random.choice(warm_msg_lst)}"
    return warm_msg_content