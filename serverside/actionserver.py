from kafka import KafkaConsumer
from json import loads
from time import sleep
from json import dumps
from kafka import KafkaProducer
from _thread import *
import json 
# import schedule 
import sys
import datetime

import time
import collections

from time import sleep
from json import dumps
from kafka import KafkaProducer
from kafka import KafkaConsumer
from json import loads
import threading

import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb1 = myclient["GlobalDB1"]
mydb2 = myclient["GlobalDB2"]
mydb3 = myclient["GlobalDB3"]

topic_num = 0
chance = 0
msgid = 1
servercount = 1

def select_server(msgid):
    global servercount
    return msgid%servercount

def check_typeof_receiver(message):
    recv = message.split("_/_")[1].split("_")
    if(len(recv)>1):
        return "group"
    return "singleuser"

def update_database(templist,flg):
    table_name=""
    if flg==1:
        table_name = str(templist[1])+"_"+str(templist[2])
    else:
        table_name=str(templist[2])
    mycol1 = mydb1[table_name]
    mycol2 = mydb2[table_name]
    mycol3 = mydb3[table_name]

    mydict = { "Msg ID": templist[0], "Sender ID": templist[1], "Text": templist[2],"Timestamp":datetime.datetime.now()}

    x1 = mycol1.insert_one(mydict)
    x2 = mycol2.insert_one(mydict)
    x3 = mycol3.insert_one(mydict) 

def consumer_t(topic):
    
    global chance, producer, msgid
    consumer = KafkaConsumer(topic,
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    for message in consumer:
        message = message.value
        print("loop ",message)
        receiver_type = check_typeof_receiver(message)
        print(" receiver_type ",receiver_type)
        if(receiver_type=="group"):
            print("its grp")
            recv = message.split("_/_")[1].split("_")
            print("if grp ",recv)
            update_database(message.split("_/_")[0].split("_"),0)
            format_of_msg_server = " ".join(message.split("_/_")[0].split("_"))
            for recvr in recv:
                    # pass
                    producer.send(recvr.split('\n')[0], value=format_of_msg_server)

        else:
            print("nothing")
            recv = message.split("_/_")[1].split("_")
            print("if not ",recv)
            update_database(message.split("_/_")[0].split("_"),1)
            format_of_msg_server = " ".join(message.split("_/_")[0].split("_"))
            for recvr in recv:
                # pass
                    # format_of_msg_server = " ".join(message.split("_/_")[0].split("_"))
                producer.send(recvr, value=format_of_msg_server)
            
    
            
user_id=""
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda x: dumps(x).encode('utf-8'))


while(1):
    
    if(topic_num==0):
        print(" Action Server running ..")
        topic= "server0"
        user_id=topic
        t1 = threading.Thread(target=consumer_t,args=(topic,))
        t1.start()
        topic_num+=1
    
    else:    
        recv = input("Receiver?  ")
        data = "Hi Yash"
        
        data=user_id+" sent you-   "+data
        producer.send(recv, value=data)
        sleep(1)