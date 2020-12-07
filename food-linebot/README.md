# food-linebot #

## 專案介紹 ##

本專案使用Python物件導向的多型(Polymorphism)概念，來開發美食餐廳LINE Bot，透過按鈕樣板訊息(Buttons template message)對談的方式瞭解使用者所要尋找的餐廳條件(地區、美食分類、平均消費價格)後，利用Python網頁爬蟲取得目前正在營業的五間最高人氣餐廳資料，回覆給使用者作為參考，可以搭配[[LINE Bot教學]提升使用者體驗的按鈕樣板訊息(Buttons template message)實用技巧](https://www.learncodewithmike.com/2020/07/line-bot-buttons-template-message.html)部落格文章來進行學習。

## 前置作業 ##

將專案複製(Clone)下來後，假設沒有pipenv套件管理工具，可以透過以下指令來進行安裝：

`$ pip install pipenv`

有了pipenv套件管理工具後，就可以執行以下指令，來安裝專案所需的套件：

`$ pipenv install --ignore-pipfile`

接著，登入虛擬環境，執行Django Migration(資料遷移)：

`$ pipenv shell`

`$ python manage.py migrate`

## 執行畫面 ##

<img src="https://1.bp.blogspot.com/-xtdV8qWOQgI/XwsK2R_FLRI/AAAAAAAADho/mwYWqibN1wIv1Xy-RZF9LBN2rPwmMsbNQCPcBGAsYHg/s2048/line_bot_buttons_template_message_1.jpg" width="350" height="700" />

<img src="https://1.bp.blogspot.com/-WRi2qROqKis/XwsK2fDaTZI/AAAAAAAADho/VZ-Ac8ewhjccJwDMtyQAsJftU2t78OH3gCPcBGAsYHg/s2048/line_bot_buttons_template_message_2.jpg" width="350" height="700" />