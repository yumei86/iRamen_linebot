import csv
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

#---------------find_longtitude and latitude for stores-------------------

options = webdriver.ChromeOptions()
options.add_argument("headless")

def get_coordinate(addr):
    browser = webdriver.Chrome(executable_path='chromedriver',options=options)
    browser.get("http://www.map.com.tw/")
    search = browser.find_element_by_id("searchWord")
    search.clear()
    search.send_keys(addr)
    browser.find_element_by_xpath("/html/body/form/div[10]/div[2]/img[2]").click() 
    time.sleep(2)
    iframe = browser.find_elements_by_tag_name("iframe")[1]
    browser.switch_to.frame(iframe)
    coor_btn = browser.find_element_by_xpath("/html/body/form/div[4]/table/tbody/tr[3]/td/table/tbody/tr/td[2]")
    coor_btn.click()
    coor = browser.find_element_by_xpath("/html/body/form/div[5]/table/tbody/tr[2]/td")
    coor = coor.text.strip().split(" ")
    lat = coor[-1].split("：")[-1]
    log = coor[0].split("：")[-1]
    browser.quit()
    return (lat, log)

#---------------motify origional csv file------------------


def mo(csv_file):
    
    f = open(csv_file, "r")
    f.readline() #把檔頭讀掉   
    rows = csv.reader(f)

    # 以迴圈輸出每一列
    final = []
    for row in rows:
        add = row[2]
    
        if "," in add:
            add = "無提供地址資訊"

        a = re.findall(r'[0-9]+|[a-z]+',add)
        try:
            n_line = add.replace(str(a[0]), "")
            final.append(n_line)
        except:
            final.append(add)
    return final


inp = mo("Ramen_infor_version.csv")
  
#---------------create new csv file------------------

with open('Ramenstore_lonlat.csv', 'w', newline='') as csvfile:
    
    writer = csv.writer(csvfile, delimiter=',') #以空白分隔欄位，建立 CSV 檔寫入器
    writer.writerow(['latitude','longtitute'])
    for item in inp: #計算剩下的資料有幾行
        if "無提供地址資訊" == item:
            a = ["",""]
        else:
            a = get_coordinate(item)

        print(a[0],a[1])
        writer.writerow([a[0],a[1]])

