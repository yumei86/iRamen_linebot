def favorite_list_generator(favorite_list):
    
    button_list = [BoxComponent(
                    layout="vertical",
                    margin="sm",
                    spacing="sm",
                    content=[
                        TextComponent(text="最愛清單", weight="bold", size="md", margin="sm", wrap=True,),
                        SeparatorComponent(margin = "xl")
                    ])]
    for i in favorite_list:
        favorite_button=ButtonComponent(style="primary", color="#997B66", size="sm", margin="sm",
                                        action=MessageAction(label=i, text=i), )
        delete_button=ButtonComponent(style="secondary", color="#F1DCA7", size="sm", margin="sm", flex=0,
                                      action=MessageAction(label="-", text="刪除最愛清單："+i), )
        button_row=BoxComponent(layout="horizontal", margin="md", spacing="sm",
                                contents=[favorite_button, delete_button])
        button_list.append(button_row)
    
    bubble=BubbleContainer(
        director='ltr',
    
        body=BoxComponent(
            layout="vertical",
            contents=button_list
        )
    )
