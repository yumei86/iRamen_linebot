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
    report_text =f"\udbc0\udcb2常見問題\n\n• 選擇湯頭和評論品項不同:\n\n別擔心，該推薦店家是有賣你選的湯頭類型！\
                    \n\
                    \n• 希望有較小範圍的地區搜尋功能:\n\n已經上線了試營運中。\
                    \n\
                    \n\udbc0\udcb23月新增\n• 評論超連結\n• 店家附近天氣\n• 拉麵語錄\n• 分流看更多推薦\n• 看相似店鋪\n• 大幅提升回應速度\n\
                    \n\
                    \n\udbc0\udc84更多心得請至臉書社團「台灣拉麵愛好會」、「台灣拉麵評論會」觀看\
                    \n\
                    \n歡迎請填寫使用者回饋表單，非常感謝你！\udbc0\udc7a\
                    \nhttps://reurl.cc/14RmVW"
    return report_text 