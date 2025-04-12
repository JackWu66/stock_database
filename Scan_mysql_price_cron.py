import urllib.request as req
import bs4
import ssl

import requests as re1
import time
import json
import mysql.connector


snum=[]
big_date=[]  #存大盤日期 主要是要基準開盤日 不要去更新到沒有開盤的個股 導致外資 投信 自營商 買賣張數被歸零

def stock_id():
    cursor.execute("SELECT * FROM `stock_id_list`;")
    analy=cursor.fetchall()
    i=0
    while(i>-1):
        try:
            id=analy[i][0]
            snum.insert(i,id)
            i=i+1
        except:
            i=-1
            print("snum update finish")


def create_table(id):
    cursor.execute("CREATE TABLE `%s`(`date` date UNIQUE,`stock_ID` VARCHAR(4),`open` DECIMAL(6,2),\
    `high` DECIMAL(6,2),`low` DECIMAL(6,2),`close`DECIMAL(6,2),`volume` INT,PRIMARY KEY (`date`,`stock_ID`));"%id)

def drop_table(id):
    cursor.execute("DROP TABLE `%s`;" %id)

def insert_data(id,date,open,high,low,close,volume):
    cursor.execute("INSERT INTO `%s`(`date`,`stock_ID`,`open`,`high`,`low`,`close`,`volume`,`外資`,`投信`,`自營商`) \
    VALUE('%s',%s,%f,%f,%f,%f,%d,%d,%d,%d);"%(id,date,id,open,high,low,close,volume,0,0,0))

def update_data(id,open,high,low,close,volume,date):
    cursor.execute("UPDATE `%s` SET `open`=%f,`high`=%f,`low`=%f,`close`=%f,`volume`=%d,`外資`=%d,`投信`=%d,`自營商`=%d \
    WHERE `date`=%s;"%(id,open,high,low,close,volume,0,0,0,date))



def query_data(id):
    cursor.execute("SELECT * FROM `%s`;" %id)
    stock = cursor.fetchall()
    print(stock)

def delete(id,item,primary):
    cursor.execute("DELETE FROM `%s` where `%s`='%s';"%(id,item,primary))

def update_capital_amount(cap,vol,date,id):
    cursor.execute("UPDATE `stock_id_list` SET `資本額(萬張)`='%f',`最新成交量`='%f' ,`更新時間`='%s' WHERE `stock_ID`='%s';"%(cap,vol,date,id))


#######################爬蟲###############################################

def urldatabig(loop):  #擷取五日股價 算均線
    url = "https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=d&mkt=10&sym=%"+str(loop)+"&v"
    headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    res = re1.get(url,headers = headers) 
    res.encoding ="utf-8"
    data3 = res.text[5:-2] #濾掉json不合法的字元
    data3 = data3.replace("\"143\":0","\"143\":") #濾掉10點前json不合法字元
    return data3


##############################data2###########################################

def urldata2(loop):  #爬網頁基本資料
    context=ssl._create_unverified_context() #新增忽略未經核實的ssl驗證
    try:
        url = "https://stock.pchome.com.tw/stock/sid"+str(loop)+".html"
        headers = {
        "Referer":"https://stock.pchome.com.tw/set_cookie.php?is_need_login=0&key=WVRveU9udHpPakk2SW1sMklqdHpPakUyT2lKL0RWOGZhQXVYT2V2cEloX0lwOXZESWp0ek9qVTZJbU55ZVhCMElqdHpPakl3T0RvaUtGQUloT1dEQWJ2SjA2ZlJXWVk1SUJJa19zTElodlQ4ZmtOUTNGYlc3WEt2U0dTOV95ZlJ4VldFNmFaTHdTaHJyNDZsSWcvV1V2R1gyakE4RGZUWGpZcXRyU25kSFFZUl8veThqNk1jN1E0VmRoYTFTMmkyWTVPYUpkREd1TkVLdHJvZmcydjdyOTc0NEFtcW1UWkgzOTVoajFsZkdEdFczUlJtdUhFYlZNVDdSWXo3RWJ6WWRJYVhzd29RQ2dhMzBlZHpZS0lTL3RLc2hDR2luOUZMRTQ2WnV3TDNYeFZkL0NLR2ltWThhX3BEdi91SlZDNzVXb0lWa0ZxNjk1V01oMGNmbUZ4d0JWWF82UEN0LzhqYXhDSTdmUT09"
                }
        request =req.Request(url,headers = headers)
    except:
        snum.insert(0,loop)
        return str(loop)+":網頁連線重試"
    with req.urlopen(request,context=context) as response:
        data = response.read()
        urldata2 = bs4.BeautifulSoup(data,"html.parser")
        return urldata2   



def Volume(data2): #資本額
    Volume = data2.find_all("tr")[5]("td")[2].text #資本額
    Volume = Volume.replace(",","")
    return Volume  #文字格式的資本額單位億



##############################################data3############################################


def urldata3(loop):  #擷取五日股價 算均線
    url = "https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=d&mkt=10&sym="+str(loop)+"&v"
    headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    res = re1.get(url,headers = headers) 
    res.encoding ="utf-8"
    data3 = res.text[5:-2] #濾掉json不合法的字元
    data3 = data3.replace("\"143\":0","\"143\":") #濾掉10點前json不合法字元
    return data3


def close (data3,day):  #得到哪一天的收盤股價 day=0=最新 1=1天前
    try:
        close = json.loads(data3)["ta"][-day-1]["c"]
        return close
    except:
        return "NA"

def open (data3,day):  #得到哪一天的開價 day=0=最新 1=1天前
    try:
        open = json.loads(data3)["ta"][-day-1]["o"]
        return open
    except:
        return "NA"

def high (data3,day):  #得到哪一天的最高價 day=0=最新 1=1天前
    try:
        high = json.loads(data3)["ta"][-day-1]["h"]
        return high
    except:
        return "NA"

def low (data3,day):  #得到哪一天的最低股價 day=0=最新 1=1天前
    try:
        low = json.loads(data3)["ta"][-day-1]["l"]
        return low
    except:
        return "NA"



def date (data3,day):  #得到哪一天的日期 day=0=最新 1=1天前
    try:
        date = json.loads(data3)["ta"][-day-1]["t"]
        return date
    except:
        return "NA"

def vol (data3,day):            #列出哪一天的成交量
    try:
        vol = json.loads(data3)["ta"][-day-1]["v"]
        return vol
    except:
        None



def rampup(data3,day):
    try:
        dvalue =json.loads(data3)["ta"][-day-1]["c"]
        dvalue_1=json.loads(data3)["ta"][-day-2]["c"]
        rampup = round(float(((dvalue-dvalue_1)/dvalue_1)*100),2)
        return rampup
    except:
        None






##################main##########################






start_time = time.time()

mysql_connection=mysql.connector.connect(       #建立連線
    host = 'localhost',
    user = 'root',
    password = '079508FS'

)

cursor=mysql_connection.cursor()
cursor.execute("USE `stockdatabase`")



#print(mysql_connection) #檢查連線


day = 1 #int(input("請輸入N天要輸入幾天前的data到SQL database(0代表今日):")) set0 抓一天 set1抓兩天 預防前一天沒抓到
stock_id()
#=======================大盤指數資料寫入==========================
data3= urldatabig(23001)
No_use_box=[]
try:
    for i in range(day,-1,-1):   
        date_d =date(data3,i)
        print(date_d)
        big_date.append(date_d)
        open_d=open(data3,i)
        high_d=high(data3,i)
        low_d=low(data3,i)
        close_d=close(data3,i)
        volume_d=vol(data3,i)
        try:
            insert_data('23001',date_d,open_d,high_d,low_d,close_d,volume_d)
        except:
            print(str('23001')+" updating")
            update_data('23001',open_d,high_d,low_d,close_d,volume_d,date_d)
        mysql_connection.commit() #最後要有commit 才能把資料存起來
except:
    None

#=======================大盤資料寫入==========================

print(big_date)

Total_count=0
Current =0
for loop in snum:
    Total_count=Total_count+1

retry_counter=0

for loop in snum:
    data3=urldata3(loop)
    Current=Current+1
    print(Current)
    retry_counter=0
    try:
        for i in range((day),-1,-1):
            date_d =date(data3,i)
            while(date_d!=big_date[-i-1] and retry_counter <6):
                data3=urldata3(loop)
                date_d =date(data3,i)
                retry_counter=retry_counter+1
                print(str(loop)+"insert snum retry:"+str(retry_counter)+"time") 
            if (date_d==big_date[-i-1]):
                date_d =date(data3,i)
                open_d=open(data3,i)
                high_d=high(data3,i)
                low_d=low(data3,i)
                close_d=close(data3,i)
                volume_d=vol(data3,i)
                try:
                    insert_data(loop,date_d,open_d,high_d,low_d,close_d,volume_d)
                    print(str(loop)+" New add success")  #原本沒有 create
                    retry_counter=0
                except:
                    update_data(loop,open_d,high_d,low_d,close_d,volume_d,date_d)
                    print(str(loop)+" updating") #原本有 覆蓋成功
                    retry_counter=0
                mysql_connection.commit() #最後要有commit 才能把資料存起來
            else:
                print(str(loop)+"finial date is:"+str(date_d)+",update fail skip")
                break
    except:
        None
    try:
        data2=urldata2(loop)
        capital=round(float(Volume(data2)),2)
        update_capital_amount(capital,volume_d,date_d,loop)
        mysql_connection.commit() #最後要有commit 才能把資料存起來
    except:
        No_use_box.append(loop)


# try:                          #清空table (不用使用 不然database會不見)
#     for loop in snum:
#         drop_table(loop)
# except:
#     None


# for loop in snum:             #建立table
#     create_table(loop)


# for loop in snum:
#     query_data(loop)

#insert_data(1101,20211203,10,10.5,9.3,10.2,123550)
#delete(1101,'date','2021-12-03')
# query_data(loop)


mysql_connection.close() 

end_time = time.time()
print("Time:%f" %(end_time-start_time))
