from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import time
import csv
import pyautogui



#-------將網頁開啟的動作換為背景執行----------

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_experimental_option('excludeSwitches', ['enable-automation'])  #把新版google的自動控制提醒關掉
#options.add_argument("window-size=1920,1080")
#options.add_argument("--start")
driver = webdriver.Chrome(executable_path='chromedriver',options=options)
link = 'https://www.google.com/maps/d/u/0/viewer?fbclid=IwAR3O8PKxMuqtqb2wMKoHKe4cCETwnT2RSCZSpsyPPkFsJ6NpstcrDcjhO2k&mid=1I8nWhKMX1j8I2bUkN4qN3-FSyFCCsCh7&ll=24.807740000000006%2C120.96740199999999&z=8'
driver.get(link)

time.sleep(3)


#-------關掉即將開幕的選單-------
first_cl = driver.find_element_by_xpath("//div[2]/div/div/div[2]/div/div/div[2]/div/div/div/div[3]")
first_cl.click()

#-------下滑網頁(較南邊的縣市需要)-------
#pyautogui.scroll(-10)

store_name = []
store_loca = []
store_char = []
store_time = []
store_tran = []
store_refs = []
store_tags = []
store_number = [167,47,59,68,37,50,12]
#-------把剩下項目打開--------
item = 2
#for item in range():
num_1 = str(item + 2)
start_search_btn = driver.find_element_by_xpath("//div["+ num_1 +"]/div/div[3]/div[2]/div/div")
start_search_btn.click()

n = store_number[item]


#-------打開評論爬資訊(要記得關掉)-------
for items in range(59):
    num = str(items + 3)
    driver.find_element_by_xpath("//div["+ num_1 +"]/div/div[3]/div["+ num +"]/div[2]/div").click()
    time.sleep(1)

    s1 = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="qqvbed-p83tee-lTBxed"]')))
        
    store_name.append(s1[0].text)
    print(store_name)
    time.sleep(1)

    temp = s1[1].text.split("\n")
    temp_new = []
        
    for i in range(len(temp)):
        if "▎特色：" == temp[i]:
            one = i
        if "▎營業時間：" == temp[i]:
            two = i
        if "▎鄰近地標或大眾運輸：" == temp[i]:
            three = i
        if "▎社團內參考食記：" == temp[i]:
            four = i
        if "▎標籤：" == temp[i]:
            five = i
    
    try:
        l = int( two - one )-1
        
        for k in range(l):
            temp_new.append(temp[one+k+1])
        ans = "".join(temp_new)
        store_char.append(ans)
        
    except:
        store_time.append("無提供特色資訊")

    temp_new = []
        
    try:
        l = int( three - two )-1
            
        for k in range(l):
            temp_new.append(temp[two+k+1])
        ans = "".join(temp_new)
        store_time.append(ans)
            
    except:
        store_time.append("無提供時間資訊")
        
    temp_new = []
        
    try:
        l = int( four - three  )-1

        for k in range(l):
            temp_new.append(temp[three+k+1])
        ans = "".join(temp_new)
        store_tran.append(ans)   
    except:
        store_tran.append("無提供交通資訊")     
        
    temp_new = []

    try:
        l = int( five - four )-1

        for k in range(l):
            temp_new.append(temp[four+k+1])
        ans = "   ".join(temp_new)
        store_refs.append(ans)
            
    except:
        store_refs.append("無提供評論資訊")

    temp_new = []

    try:
        l = int( five )
        temp_new.append(temp[five+1])
        ans = "".join(temp_new)
        store_tags.append(ans)
            
    except:
        store_tags.append("無提供標籤資訊")
        
    temp_new = []
        
    
    try:
        location = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="fO2voc-jRmmHf-MZArnb-Q7Zjwb"]')))
        #print(location[0].text)
        
        store_loca.append(location[0].text) 
    except:
        store_loca.append("無提供地址資訊")
    time.sleep(1)

        
    driver.find_element_by_xpath("//div[3]/div/div/span/span/span").click()
    time.sleep(1)




ans = ['','','','','','','']
with open('Ramen_map_TY.csv', 'w', newline='') as csvfile:
    
    writer = csv.writer(csvfile, delimiter=',') #以空白分隔欄位，建立 CSV 檔寫入器
    writer.writerow(['name','address','characteristics','time','transport','tags','reference'])
    for i in range(len(store_name)):
        ans[0] = store_name[i]
        ans[1] = store_loca[i]
        ans[2] = store_char[i]
        ans[3] = store_time[i]
        ans[4] = store_tran[i]
        ans[5] = store_tags[i]
        ans[6] = store_refs[i]

        writer.writerow([ans[0],ans[1],ans[2],ans[3],ans[4],ans[5],ans[6]])

driver.close() #關掉瀏覽器
