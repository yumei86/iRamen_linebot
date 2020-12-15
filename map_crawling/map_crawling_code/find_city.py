import re 
import csv
 
def mo(csv_file):
    #f = open(str(csv_file), "r")
    f = open(csv_file, "r")
    first_line = f.readline() #把檔頭讀掉   
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
            final.append(n_line) #將縣市找出來
        except:
            final.append(add)
    return final

inp = mo("/Users/linyumei/Ramen_May_git/map_crawling/csv_file/Map_Ramen_data_with_city_new_version.csv")

for item in inp:
    print(item)
   

#---------------create new csv file------------------

with open('/Users/linyumei/Ramen_May_git/map_crawling/csv_file/city.csv', 'w', newline='') as csvfile:
    
    writer = csv.writer(csvfile, delimiter=',') #以空白分隔欄位，建立 CSV 檔寫入器
    writer.writerow(['city_name'])
    for item in inp: #計算剩下的資料有幾行
        if "無提供地址資訊" == item:
            a = ""
        else:
            a = item[:3]

        print(a)
        writer.writerow([a])
    



    
