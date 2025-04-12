import urllib.request as req
import bs4
import ssl
import datetime #時間操作函數

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


def stock_id_condition_select(date):
    cursor.execute("SELECT * FROM `stock_id_list` WHERE `date`=%s;" %date)
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


#################################以下是資料庫建立##################################
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

def update_stock_id_list_rank(ratio,rank,id):
    cursor.execute("UPDATE `stock_id_list` SET `量資比`='%f',`量資排名`='%d' WHERE `stock_ID`='%s';"%(ratio,rank,id))



def create_vol_cap_ratio(id):
    cursor.execute("ALTER TABLE `%s` ADD `量資比％` DECIMAL(8,2),ADD `量資排名` DECIMAL(5,0);"%(id))

def change_type(id,s1,s2):
    cursor.execute("ALTER TABLE `%s` CHANGE `%s` `%s` DECIMAL(5,0);"%(id,s1,s2))

def update_rank_ratio(id,ratio,rank,date):
    cursor.execute("UPDATE `%s` SET `量資比％`='%f',`量資排名`='%d' where `date`='%s';"%(id,ratio,rank,date)) #更新每天的排名
############################以下是資料庫操作#############################


def date_catch(M):
    cursor.execute("SELECT * FROM `23001`;") #利用大盤database抓日期
    analy=cursor.fetchall()
    date_time=analy[-M-1][0]
    return date_time

def date_vol(id,date):
    cursor.execute("SELECT * FROM `%s` where `date`='%s';"%(id,date)) #利用大盤database抓日期
    analy=cursor.fetchall()
    vol=analy[0][6]
    cursor.execute("SELECT * FROM `stock_id_list` where `stock_ID`='%s';"%(id)) #利用大盤database抓日期
    analy=cursor.fetchall()
    capi=analy[0][2]
    return vol,capi

def dvalue (loop,day):  #得到哪一天的股價 day=0=最新 1=1天前
    try:
        cursor.execute("SELECT * FROM `%s`;"%loop)
        analy=cursor.fetchall()
        dvalue=analy[-day-1][5]
        return dvalue
    except:
        return "抓不到close股價"

def open (loop,day):
    try:
        cursor.execute("SELECT * FROM `%s`;"%loop)
        analy=cursor.fetchall()
        dvalue=analy[-day-1][2]
        return dvalue
    except:
        return "抓不到open股價"



def MA(loop,start,end):
    try:
        cursor.execute("SELECT * FROM `%s`;"%loop)
        analy=cursor.fetchall()
        sum = 0
        average =0
        for i in range(-(start+1),-(end+1),-1):
            pr=(analy[i][5])          #5 收盤價 6 volume
            sum=sum+pr
        average =round(float(sum/(end-start)),2)
        return average
    except:
        return "抓不到"+str(end)+"日均線"


def MA_all(loop,start,end):
    try:
        cursor.execute("SELECT * FROM `%s`;"%loop)
        analy=cursor.fetchall()
        sum = 0
        counter=0
        for i in range(-(start+1),-(end+1),-1):
            pr=(analy[i][5])          #5 收盤價 6 volume
            sum=sum+pr
            counter=counter+1
            if(counter==5):
                a5 =round(float(sum/(counter)),2)
            elif(counter==10):
                a10=round(float(sum/(counter)),2)
            elif(counter==20):
                a20=round(float(sum/(counter)),2)
            elif(counter==60):
                a60=round(float(sum/(counter)),2)
            elif(counter==120):
                a120=round(float(sum/(counter)),2)
        return [a5,a10,a20,a60,a120]
    except:
        return "抓不到"+str(end)+"日均線"



def MA_continue_trend(loop,start,MAday,days):     #輸入多少MA 是否連續N days trend up
    try:
        counter=0
        tempdays=days
        while(tempdays>0):
            MA_day_ProcessY=MA(loop,start+tempdays,start+tempdays+MAday)
            MA_day_Process=MA(loop,start+tempdays-1,start+tempdays-1+MAday)
            if(MA_day_Process>=MA_day_ProcessY):
                counter=counter+1
            tempdays=tempdays-1
        if(days==counter):
            return True
        else:
            return False
    except:
        return "No getting"




def Vol (loop,day):            #列出哪一天的成交量
    try:
        cursor.execute("SELECT * FROM `%s`;"%loop)
        analy=cursor.fetchall()
        vol = analy[-day-1][6]
        return vol
    except:
        return "抓不到成交量"


def VA(loop,start,end):         #成交量平均
    try:
        cursor.execute("SELECT * FROM `%s`;"%loop)
        analy=cursor.fetchall()
        sum = 0
        average =0
        for i in range(-(start+1),-(end+1),-1):
            pr=(analy[i][6])          #5 收盤價 6 volume
            sum=sum+pr
        average =round(float(sum/(end-start)),2)
        return average
    except:
        return "抓不到"+str(start)+"天前到"+str(end)+"天前日均線"




##################main##########################

start_time = time.time()

start = 1      # M天前
baseday = 0   # N天交易日前 0代表最新data


mysql_connection=mysql.connector.connect(       #建立連線
    host = 'localhost',
    user = 'root',
    password = '079508FS'

)

cursor=mysql_connection.cursor()
cursor.execute("USE `stockdatabase`")



date_box=[]

stock_id()
Total_count=0
Current =0
for loop in snum:
    Total_count=Total_count+1

for i in range(start,baseday-1,-1):
    sub_date=date_catch(i)      #取23001最新日期
    date_box.append(sub_date)

for date_i in date_box:
    Sort_box={}
    sub_box={}
    Counter=0
    for loop in snum:
        try:
            vol_1=date_vol(loop,date_i)[0]
            capital=date_vol(loop,date_i)[1]
            vol_capi_ratio=round(float((vol_1/(capital*100))),2)
            sub_box={loop:vol_capi_ratio}
            Sort_box.update(sub_box)
        except:
            None
    Sort_box=sorted(Sort_box.items(),key=lambda x:x[1],reverse=True)
    Sort_box=dict(Sort_box)
    
    for i,j in zip(Sort_box.keys(),Sort_box.values()):
        Counter=Counter+1
        update_rank_ratio(i,j,Counter,date_i)
        mysql_connection.commit()
        update_stock_id_list_rank(j,Counter,i)
        mysql_connection.commit()

    print(str(date_i)+"Finish")
    

mysql_connection.close() 

end_time = time.time()
print("Time:%f" %(end_time-start_time))
