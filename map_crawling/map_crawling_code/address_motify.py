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
            final.append(n_line)
        except:
            final.append(add)
    return final


    



    
