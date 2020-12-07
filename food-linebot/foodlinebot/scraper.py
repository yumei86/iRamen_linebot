from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests


# 美食抽象類別
class Food(ABC):

    def __init__(self, area, category, price):
        self.area = area  # 地區
        self.category = category  # 美食類別
        self.price = price  # 消費價格

    @abstractmethod
    def scrape(self):
        pass


# 愛食記爬蟲
class IFoodie(Food):

    def scrape(self):
        response = requests.get(
            "https://ifoodie.tw/explore/" + self.area +
            "/list/" + self.category +
            "?priceLevel=" + self.price +
            "&sortby=popular&opening=true")

        soup = BeautifulSoup(response.content, "html.parser")

        # 爬取前五筆餐廳卡片資料
        cards = soup.find_all(
            'div', {'class': 'jsx-2133253768 restaurant-item track-impression-ga'}, limit=5)

        content = ""
        for card in cards:

            title = card.find(  # 餐廳名稱
                "a", {"class": "jsx-2133253768 title-text"}).getText()

            stars = card.find(  # 餐廳評價
                "div", {"class": "jsx-1207467136 text"}).getText()

            address = card.find(  # 餐廳地址
                "div", {"class": "jsx-2133253768 address-row"}).getText()

            content += f"{title} \n{stars}顆星 \n{address} \n\n"

        return content
