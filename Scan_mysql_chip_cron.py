import urllib.request as req
import requests as re1
import bs4
import datetime #時間操作函數
import time
import ssl
import json
import mysql.connector



snum=[]
datebox=[]


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

def insert_stockid(id,date):
    try:
        cursor.execute("INSERT INTO `stock_id_list`(`stock_ID`,`date`) VALUE('%s',%s);"%(id,date))
        print(str(id)+" insert to stock_id_list finish")
    except:
        print("stock id:"+str(id)+" already exist")

def create_table(id):
    cursor.execute("CREATE TABLE `%s`(`date` date UNIQUE,`stock_ID` VARCHAR(4),`open` DECIMAL(6,2),\
    `high` DECIMAL(6,2),`low` DECIMAL(6,2),`close` DECIMAL(6,2),`volume` INT,`外資` DECIMAL(8,0),`投信` DECIMAL(8,0),`自營商` DECIMAL(8,0),\
    `量資比％` DECIMAL(8,2),`量資排名` DECIMAL(5,0),PRIMARY KEY (`date`,`stock_ID`));"%id)

def alter_id (id):
    cursor.execute("ALTER TABLE `%s` ADD `外資` DECIMAL(8,0),ADD `投信` DECIMAL(8,0),ADD `自營商` DECIMAL(8,0),\
                   ADD `量資比％` DECIMAL(8,2),ADD `量資排名` DECIMAL(5,0);"%id)

def drop_table(id):
    cursor.execute("DROP TABLE `%s`;" %id)

def insert_data(id,date,open,high,low,close,volume):
    cursor.execute("INSERT INTO `%s`(`date`,`stock_ID`,`open`,`high`,`low`,`close`,`volume`) \
    VALUE('%s',%s,%f,%f,%f,%f,%d);"%(id,date,id,open,high,low,close,volume))

def update_data(id,foreign,credit,dealer,date):
    cursor.execute("UPDATE `%s` SET `外資`=%d,`投信`=%d,`自營商`=%d WHERE `date`=%d AND `stock_ID`=%s;"\
    %(id,foreign,credit,dealer,date,id))


def update_data_B(id,foreign,credit,dealer,date):
    cursor.execute("UPDATE `%s` SET `外資`=%f,`投信`=%f,`自營商`=%f WHERE `date`=%d AND `stock_ID`=%s;"\
    %(id,foreign,credit,dealer,date,id))



def query_data(id):
    cursor.execute("SELECT * FROM `%s`;" %id)
    stock = cursor.fetchall()
    print(stock)

def delete(id,item,primary):
    cursor.execute("DELETE FROM `%s` where `%s`='%s';"%(id,item,primary))


def Catch_date(loop,start):                         #爬取大盤的日期 要更新近期兩天使用
    cursor.execute("SELECT * FROM `%s`;"%loop)
    analy=cursor.fetchall()
    for i in range(-1,-(start+2),-1):
        date=str(analy[i][0]).replace("-","")
        datebox.insert(i,date)
    return date





#######################爬蟲###############################################


def urldata1(date):  #上市三大法人進出
    context=ssl._create_unverified_context() #新增忽略未經核實的ssl驗證
    R_times=0
    for R_times in range(8):
        try:
            url = "https://www.twse.com.tw/rwd/zh/fund/T86?date="+date+"&selectType=ALLBUT0999&response=html"
            headers = {
            "Referer":"https://stock.pchome.com.tw/set_cookie.php?is_need_login=0&key=WVRveU9udHpPakk2SW1sMklqdHpPakUyT2lKL0RWOGZhQXVYT2V2cEloX0lwOXZESWp0ek9qVTZJbU55ZVhCMElqdHpPakl3T0RvaUtGQUloT1dEQWJ2SjA2ZlJXWVk1SUJJa19zTElodlQ4ZmtOUTNGYlc3WEt2U0dTOV95ZlJ4VldFNmFaTHdTaHJyNDZsSWcvV1V2R1gyakE4RGZUWGpZcXRyU25kSFFZUl8veThqNk1jN1E0VmRoYTFTMmkyWTVPYUpkREd1TkVLdHJvZmcydjdyOTc0NEFtcW1UWkgzOTVoajFsZkdEdFczUlJtdUhFYlZNVDdSWXo3RWJ6WWRJYVhzd29RQ2dhMzBlZHpZS0lTL3RLc2hDR2luOUZMRTQ2WnV3TDNYeFZkL0NLR2ltWThhX3BEdi91SlZDNzVXb0lWa0ZxNjk1V01oMGNmbUZ4d0JWWF82UEN0LzhqYXhDSTdmUT09"
                    }
            request =req.Request(url,headers = headers)
            with req.urlopen(request,context=context) as response:
                data = response.read()
                urldata1 = bs4.BeautifulSoup(data,"html.parser")
                return urldata1 
        except:
            R_times=R_times+1
            print("catch urldata1 fail,Retry:"+str(R_times)+"/8")
            continue


def id(data1,N):
    data=data1.find_all("div")[0]("tr")[N]("td")
    id = data[0].text
    return id #文字格式

def name(data1,N):
    data=data1.find_all("div")[0]("tr")[N]("td")
    name = data[1].text
    return name #文字格式


def foreign(data1,N):
    data=data1.find_all("div")[0]("tr")[N]("td")
    foreign = int(round((float(data[4].text.replace(",",""))/1000),0))
    return foreign

def credit(data1,N):
    data=data1.find_all("div")[0]("tr")[N]("td")
    credit = int(round((float(data[10].text.replace(",",""))/1000),0))
    return credit

def dealer(data1,N):
    data=data1.find_all("div")[0]("tr")[N]("td")
    dealer = int(round((float(data[11].text.replace(",",""))/1000),0))
    return dealer




def urldata2(date):  #上櫃三大法人
    context = ssl._create_unverified_context() #新增忽略未經核實的ssl驗證
    R_times=0
    for R_times in range(8):
        try:
            url="http://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&o=htm&se=EW&t=D&d="+date+"&s=0,asc" #上櫃三大法人
            headers = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Referer":"https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&o=htm&se=EW&t=D&d",
                    }
            request =req.Request(url,headers = headers)
            with req.urlopen(request,context=context,timeout=5) as response:
                data = response.read()
                urldata2 = bs4.BeautifulSoup(data,"html.parser")
                print("Catch Success")
                return urldata2 
        except:
            R_times=R_times+1
            print("Catch fail Retry:"+str(R_times)+"/8")
            continue




def id2(data2,N):
    id2=data2.find_all("tr")[N]("td")[0].text       #N=80~740 
    return id2 #文字格式

def name2(data2,N):
    name2=data2.find_all("tr")[N]("td")[1].text 
    return name2 #文字格式


def foreign2(data2,N):
    data=data2.find_all("tr")[N]("td")
    foreign2 = int(round((float(data[10].text.replace(",",""))/1000),0))
    return foreign2

def credit2(data2,N):
    data=data2.find_all("tr")[N]("td")
    credit2 = int(round((float(data[13].text.replace(",",""))/1000),0))
    return credit2

def dealer2(data2,N):
    data=data2.find_all("tr")[N]("td")
    dealer2 = int(round((float(data[22].text.replace(",",""))/1000),0))
    return dealer2


def urldata3(date):  #上市三大法人大盤進出金額
    context=ssl._create_unverified_context() #新增忽略未經核實的ssl驗證
    try:
        url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U?type=day&dayDate="+date+"&response=html"

        headers = {
        "Referer":"https://stock.pchome.com.tw/set_cookie.php?is_need_login=0&key=WVRveU9udHpPakk2SW1sMklqdHpPakUyT2lKL0RWOGZhQXVYT2V2cEloX0lwOXZESWp0ek9qVTZJbU55ZVhCMElqdHpPakl3T0RvaUtGQUloT1dEQWJ2SjA2ZlJXWVk1SUJJa19zTElodlQ4ZmtOUTNGYlc3WEt2U0dTOV95ZlJ4VldFNmFaTHdTaHJyNDZsSWcvV1V2R1gyakE4RGZUWGpZcXRyU25kSFFZUl8veThqNk1jN1E0VmRoYTFTMmkyWTVPYUpkREd1TkVLdHJvZmcydjdyOTc0NEFtcW1UWkgzOTVoajFsZkdEdFczUlJtdUhFYlZNVDdSWXo3RWJ6WWRJYVhzd29RQ2dhMzBlZHpZS0lTL3RLc2hDR2luOUZMRTQ2WnV3TDNYeFZkL0NLR2ltWThhX3BEdi91SlZDNzVXb0lWa0ZxNjk1V01oMGNmbUZ4d0JWWF82UEN0LzhqYXhDSTdmUT09"
                }
        request =req.Request(url,headers = headers)
    except:
        None
    with req.urlopen(request,context=context) as response:
        data = response.read()
        urldata3 = bs4.BeautifulSoup(data,"html.parser")
        return urldata3   

def foreign3(data3):
    data=data3.find_all("div")[0]("tr")[5]("td")
    foreign3 = round((float(data[3].text.replace(",",""))/100000000),2)
    return foreign3

def credit3(data3):
    data=data3.find_all("div")[0]("tr")[4]("td")
    credit3 = round((float(data[3].text.replace(",",""))/100000000),2)
    return credit3

def dealer3(data3):
    data=data3.find_all("div")[0]("tr")[2]("td")
    dealer3 = round((float(data[3].text.replace(",",""))/100000000),2)
    return dealer3





#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvmainvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


start_time = time.time()

mysql_connection=mysql.connector.connect(       #建立連線
    host = 'localhost',
    user = 'root',
    password = '079508FS'

)

cursor=mysql_connection.cursor()
cursor.execute("USE `stockdatabase`")

Catch_date(23001,1)      #抓大盤table 23001 日期的0 =-1 , 1=-2 (0是最新＝只更新1天 1是前一天＝更新2天)
print(datebox)



for i in datebox:         #日期for迴圈
    date=int(i)           #資料庫的日期格是整數格式
    print(date)
    data3=urldata3(str(date))         #寫入大盤23001的三大法人買賣超金額  日期for迴圈
    try: 
        foreignB=foreign3(data3)
        creditB=credit3(data3)
        dealerB=dealer3(data3)
        update_data_B('23001',foreignB,creditB,dealerB,date)
        mysql_connection.commit()
        print("update:"+str(date))
    except:
        print("update fail:"+str(date))

    data1= urldata1(str(date))
    for j in range(-1,-1600,-1):            #table result迴圈   20240407 -1250-->-1600
        try:
            id1=id(data1,j)
            foreign1=foreign(data1,j)
            credit1=credit(data1,j)
            dealer1=dealer(data1,j)
            try:
                update_data(id1,foreign1,credit1,dealer1,date)
                mysql_connection.commit()
                print(str(date)+" "+id1+" Finish")
            except:
                if (len(id1)==4 and str.isdigit(id1) and id1[0]!='0'):        #SQL沒有stock id 插入新的stock id到SQL stock_id_list
                    print("import new stockid:"+str(id1))
                    insert_stockid(id1,date)
                    mysql_connection.commit()
                    create_table(id1)
                    mysql_connection.commit()
                    print("create "+str(id1)+" table ok")

        except:
            None
    
    date_str=str(date)
    date2=str(int(date_str[0:4])-1911)+"/"+date_str[4:6]+"/"+date_str[6:8]
    data2= urldata2(date2)
    for k in range(50,1200,1):      #20240407 800-->1200
        try:
            id_2=id2(data2,k)
            foreign_2=foreign2(data2,k)
            credit_2=credit2(data2,k)
            dealer_2=dealer2(data2,k)
            try:
                update_data(id_2,foreign_2,credit_2,dealer_2,date)
                mysql_connection.commit()
                print(str(date)+" "+id_2+" Finish")
            except:
                if (len(id_2)==4 and str.isdigit(id_2) and id_2[0]!='0'):        #SQL沒有stock id 插入新的stock id到SQL stock_id_list
                    print("import new stockid:"+str(id_2))
                    insert_stockid(id_2,date)
                    mysql_connection.commit()
                    create_table(id_2)
                    mysql_connection.commit()
                    print("create "+str(id_2)+" table ok")


        except:
            None
            

mysql_connection.close() 

end_time = time.time()
print("Time:%f" %(end_time-start_time))


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^main^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




#print(mysql_connection) #檢查連線





# Total_count=0
# Current =0
# for loop in snum:
#     Total_count=Total_count+1




# for loop in snum:
#     data3=urldata3(loop)
#     Current=Current+1
#     print("目前進度:"+str(Current)+"/"+str(Total_count)+"\n")
#     try:
#         for i in range(0,(day+1),1):
#             date_d =date(data3,i)
#             open_d=open(data3,i)
#             high_d=high(data3,i)
#             low_d=low(data3,i)
#             close_d=close(data3,i)
#             volume_d=vol(data3,i)
#             insert_data(loop,date_d,open_d,high_d,low_d,close_d,volume_d)

#     except:
#         None 



# try:                          #清空table (不用使用 不然database會不見)
#     for loop in snum:
#         drop_table(loop)
# except:
#     None


# for loop in snum:             #建立table
#     create_table(loop)

# for loop in snum:
#     alter_id(loop)
#     mysql_connection.commit() #最後要有commit 才能把資料存起來

# for loop in snum:
#     query_data(loop)

#insert_data(1101,20211203,10,10.5,9.3,10.2,123550)
#delete(1101,'date','2021-12-03')
# query_data(loop)



