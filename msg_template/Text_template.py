import random

def keyword_warning_text():
    store_example = ['「鷹流 公館」','「公 子」','「山下公 園」','「隱家 赤峰」','「七 面鳥」','「麵屋 壹」','「真 劍」','「秋 鳴」','「Mr 拉麵雲」','「辰 拉」','「京都 柚子」','「麵屋 ichi」','「麵屋 壹之穴」','「KIDO 拉麵」','「Ramen 初」','「暴 走」','「Hiro 新店」']
    random.shuffle(store_example)
    store_example_choice_lst = store_example[:5]
    store_example_choice = ''.join(store_example_choice_lst)
    # store_example_choice = reduce(lambda a,x: a+str(x), store_example_choice_lst, "")
    warning_text = f"\udbc0\udcb2打字搜尋功能請輸入:\n關鍵字 關鍵字,\n\n例:{store_example_choice}\n\n\udbc0\udcb2請輸入有效店名關鍵字(中間幫我隨意留一個半形空,但不可在前後加入空白)\n\udbc0\udcb2或請幫我直接點選拉麵推薦選單做選擇喔！"
    return warning_text