import os
import time
import random
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


### change as needed
load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
chromedriver_path = '/PATH/TO/CHROMEDRIVER'   
url = 'https://m.facebook.com/groups/RamenTW'


def FB_login(chromedriver_path,url):
    driver = webdriver.Chrome(executable_path = chromedriver_path)
    driver.get("https://www.facebook.com")
    print('open')
    # driver.close()

    ### facebook login
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#email')))
    elem = driver.find_element_by_id("email")
    elem.send_keys(USERNAME)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(PASSWORD)
    elem.send_keys(Keys.RETURN)
    time.sleep(5)
    driver.get(url) # Switch to the group page
    return driver


def FB_crawling(driver, n):
    ### Scrolling the website
    for x in range(1,n):
        #print(x) # testing
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        t = random.choice([2,3,4,5]) # avoid being banned 
        time.sleep(t)
        
    ### POST Crawling
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    raw_data = soup.findAll('div', {'class':'story_body_container'})

    posts = []
    for item in raw_data:
        description = item.select('p')
        see_more = item.findAll('span', {'class': 'text_exposed_show'}) # Expand the 'See more' button
        if len(see_more) > 0:
            if len(description) > 0:
                description = '\n'.join([d.text for d in description])
                see_more_txt = '\n'.join([s.text for s in see_more])
                description = description + ' ' + see_more_txt 
            else:
                description = '\n'.join([s.text for s in see_more])
        else:
            if len(description) > 0:
                description = '\n'.join([d.text for d in description])
            else:
                description = ''

        ### Post created time Crawling       
        published = item.select('abbr')  # Get the formatted datetime of published time
        if published is not None:
            published = '\n'.join([pb.text for pb in published])
        else:
            published = ''
        post = {'Description': description, 'published': published}
        posts.append(post)
    return posts
        

def output_to_csv(posts, filename):
    df = pd.DataFrame(posts)
    if filename[:-4] != '.csv':
        filename = f'{filename}.csv'
    df.to_csv(str(filename))


def output_to_txt(posts, filename):
    df = pd.DataFrame(posts)
    if filename[:-3] != '.txt':
        filename = f'{filename}.txt'
    df.to_csv(str(filename), sep='\t', index=False)


'''def main():
    driver = FB_login(chromedriver_path, url)
    posts = FB_crawling(driver, 520)
    output_to_csv(posts, 'fb_crawling_output')


if __name__ == '__main__':
    main()'''
