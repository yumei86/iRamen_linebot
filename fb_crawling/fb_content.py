import pandas as pd
import re
f = open('./data/1_fb_crawling.txt', 'r', encoding='utf8')
shop_count = 0
ramen_list = []
ramen_shop_raw = []
ramen_shop_list = []
ramen_name_list = []
ramen_name_raw = []
ramen_review_raw = []
ramen_review_list = []
unorganized_shops = []
unorganized_unorganized_shops = []
temp_s = ''
ramen_list_group = []
for line in f:
    line = line.strip()
    #### add endpoint and startpoint to items for striping later
    #### catch 店家:(first item of each sublist) to % for 店名
    #### catch G to Z, if not Z catch to the first 0
    start_point = line.replace('… 更多','').replace(' ','').replace('$','').replace('%','')\
                    .replace(u'\u3000',u'')\
                    .replace('／','').replace('區域','').replace('：',':').replace(':',':')\
                    .replace('店家:','$店家:')\
                    .replace('▎店家:','$店家:').replace('▎店　　名:','$店家:')\
                    .replace('店名:','$店家:').replace('▎店　　家:','$店家:')\
                    .replace('【店家】','$店家:').replace('店家名稱:','$店家:')\
                    .replace('■店家資訊:','$店家:')\
                    .replace('鄰近地點','%鄰近地點').replace('臨近地點:','%鄰近地點:')\
                    .replace('鄰近地區','%鄰近地點').replace('鄰近:','%鄰近地點:')\
                    .replace('拉麵名稱','%.G拉麵名稱').replace('餐點名稱:','%.G拉麵名稱:')\
                    .replace('餐點:','%.G拉麵名稱:').replace('拉麵品項:','%.G拉麵名稱')\
                    .replace('品項:','%.G拉麵名稱:').replace('品名:','%.G拉麵名稱:')\
                    .replace('名稱:','%.G拉麵名稱:').replace('品項價格:','%.G拉麵名稱:')\
                    .replace('配置:','Z配置').replace('配　　置','Z配置').replace('配置(','Z配置')\
                    .replace('\'','').replace('Description','')\
                    .replace('_','').replace('分隔線','')\
                    .replace('▎','').replace('🁢',' ').replace('-','').replace('◎','')\
                    .replace('【',' ').replace('】',':')
    # print(start_point)
    #### replace \u3000 doesnt work
    #### devide all the stores and store them in a list
    for w in start_point:
        temp_s += w
        if w == '$':
            ramen_list.append(temp_s)
            temp_s = ''
# print(ramen_list)

#### first filtering:put items with all the startpoint and endpoint to lists
#### if not sufficient then put into unorganized_shops list
for shops in ramen_list:
    if ('%'not in shops or 'G' not in shops or 'Z' not in shops\
        or shops.index('Z')>shops.index('G')+80) :
        unorganized_shops.append(shops)
    else:
        ramen_shop_raw.append(shops[:shops.index('%')])
        ramen_name_raw.append(shops[shops.index('G')+1:shops.index('Z')])
        ramen_review_raw.append(shops[shops.index('Z')+1:shops.index('Z')+265]+'...')
# print(len(ramen_shop_list))
# print(ramen_name_list)
# print(ramen_review_list)
# print(ramen_list)

#### second filtering
for shops in unorganized_shops:
    if ('G' in shops and '0' in shops):
        ramen_shop_raw.append(shops[:shops.index('%')])
        ramen_name_raw.append(shops[shops.index('G')+1:shops.index('G')+30])
        ramen_review_raw.append(shops[shops.index('G')+19:shops.index('G')+285]+'...')

    else:
        unorganized_unorganized_shops.append(shops)

# print(ramen_shop_raw)

for shops in ramen_shop_raw:
    new_shops = shops.replace('■','').replace('2.','')
    if '地址' in new_shops and '用餐' in new_shops:
        # print(shops)
        if new_shops.index('地') < new_shops.index('用'):
            ramen_shop_list.append(new_shops[:new_shops.index('地')])
        else:
            ramen_shop_list.append(new_shops[:new_shops.index('用')])
    elif '地址' in new_shops:
        ramen_shop_list.append(new_shops[:new_shops.index('地')])
    elif '用餐' in new_shops:
        ramen_shop_list.append(new_shops[:new_shops.index('用')])
    else:
        ramen_shop_list.append(new_shops)


# print(ramen_shop_list)
for names in ramen_name_raw:
    # print(f'original name{names}')
    new_name = names.replace('拉麵%.G','').replace('%.G','')
    last_ch = new_name[-1]
    first_ch = new_name[0]
    # ramen_name_list = []
    if '0' in new_name and '00' not in new_name and '2020' not in new_name\
        and last_ch != '）' and last_ch != ')':
        ramen_name_list.append(new_name[:new_name.index('0')+1])
    elif '00' in new_name and last_ch != '）' and last_ch != ')'\
        and '2020' not in new_name:
        ramen_name_list.append(new_name[:new_name.index('00')+2])
    elif first_ch != '拉':
        ramen_name_list.append(new_name[new_name.index('拉'):])
    elif '0' not in new_name and '00' not in new_name and '/' not in new_name\
        and last_ch.isdigit() == False and last_ch != '麵' and last_ch != '麺'\
        and last_ch != '）' and last_ch != ')'and '+' not in new_name:
        new_point =  new_name.replace('麵','麵H').replace('麺','麵H').replace('拉麵H名稱','拉麵名稱')
        if 'H' in new_point:
            ramen_name_list.append(new_point[:new_point.index('H')])
        else:
            ramen_name_list.append(new_point)
    else:
        ramen_name_list.append(new_name)

# print(len(ramen_name_list))

#https://www.cnblogs.com/qmfsun/p/11811990.html
for reviews in ramen_review_raw:
    new_reviews = reviews.replace('拉麵%.G','').replace('%.G','').replace('%','').replace('$','')
    first_few_words = new_reviews[0:6]
    if '配置'not in first_few_words:
        pattern="[\u4e00-\u9fa5]+" 
        regex = re.compile(pattern)
        results =  regex.findall(new_reviews)
        # print(results_to_str)
        results_to_str =' '.join([str(elem) for elem in results]) 
        ramen_review_list.append(results_to_str)
        # print(results_to_str)

    else:
        ramen_review_list.append(new_reviews)
        

#coding=utf-8

    
#### debug
# print(len(unorganized_unorganized_shops))
# print(unorganized_unorganized_shops)
# print(len(ramen_shop_list))
# print(len(ramen_name_list))
# print(len(ramen_review_list))
# print(ramen_shop_list)
# print(ramen_name_list)
# print(ramen_review_list)

# print(ramen_name_list.index("拉麵名稱價格:濃厚雞白湯拉麵雞腿捲230"))
# print(ramen_shop_list.index('店家:樂趣Lovecheers'))

# print(ramen_shop_list.index('店家:不二家拉麵居酒屋'))
# print(ramen_name_list.index("拉麵名稱:醬油叉燒拉麵180"))



####csv
# https://stackoverflow.com/questions/17704244/writing-python-lists-to-columns-in-csv
df = pd.DataFrame(list(zip(*[ramen_shop_list, ramen_name_list, ramen_review_list])))
col_names = ['stores', 'ramens', 'reviews']
df.columns = col_names
df.to_csv('fb_crawling.csv', index=True)
