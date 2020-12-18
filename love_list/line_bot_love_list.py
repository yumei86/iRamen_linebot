elif "加到最愛清單" in event.message.text:
    
    text_list=event.message.text.split(":")
    add_ramen=text_list[1]
    
    if ramen.objects.filter(chinese_name=add_ramen).exists():
        
        user=UserFavorite.objects.get(user_id=user_id)
        ramen_str=user.ramen
        
        if ramen_str is None or ramen_str == "":
            user.ramen=add_ramen
            user.save()
        else:
            ramen_list=ramen_str.split(",")
            
            if len(ramen_list) > 25:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="最愛清單數量超過上限，請刪除部分資料～")
                )
            elif add_ramen in ramen_list:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=add_ramen + "已經在最愛清單！")
                )
            else:
                ramen_str=ramen_str + "," + add_ramen
                user.ramen=ramen_str
                user.save()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已經把" + add_ramen + "加進最愛清單！")
        )
elif "從最愛清單刪除" in event.message.text:
    
    text_list=event.message.text.split(":")
    delete_ramen=text_list[1]
    
    if Ramen.objects.filter(chinese_name=add_name).exists():
        if delete_ramen in ramen_str:
            ramen_str=ramen_str.remove(delete_ramen)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已經把" + delete_ramen + "從最愛清單刪除！")
            )
