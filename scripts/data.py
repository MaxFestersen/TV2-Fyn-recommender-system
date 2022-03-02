#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 14:50:19 2022

@author: adernild
"""

import http.client
import json
import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd

#%%
load_dotenv()
db_user = os.environ.get('db-user')
db_pass = os.environ.get('db-pass')
#%%
mydb = mysql.connector.connect(
    host="localhost",
    user=db_user,
    password=db_pass,
    database='tv2fyn')

mycursor = mydb.cursor()

#%%
mycursor.execute('SELECT * FROM device;')
device = mycursor.fetchall()
device = pd.DataFrame(device, columns=['deviceID', 'firstVisit', 'screenWidth', 'screenHeight', 'deviceOS', 'deviceVendor'])

#%%
def get_sessions(deviceID):
    mycursor.execute(f'SELECT sessionID FROM session WHERE deviceID="{deviceID}";')
    session = mycursor.fetchall()
    session = pd.DataFrame(session, columns=['sessionID'])
    return session

def get_sessionInfo(sessionID):
    mycursor.execute(f'SELECT * FROM sessionInfo WHERE sessionID="{sessionID}";')
    sessionInfo = mycursor.fetchall()
    sessionInfo = pd.DataFrame(sessionInfo, columns=['sessionID', 'date', 'elapsed', 'articleID', 'scrollY', 'lat', 'lon'])
    return sessionInfo

#%%
sessionID = get_sessions(device['deviceID'][1])
#%%
sessionInfo = get_sessionInfo(sessionID['sessionID'][0])

#%%

mycursor.execute('SELECT * FROM session')
session = mycursor.fetchall()
session = pd.DataFrame(session, columns=['deviceID', 'sessionID'])

mycursor.execute('SELECT * FROM sessionInfo')
sessionInfo = mycursor.fetchall()
sessionInfo = pd.DataFrame(sessionInfo, columns=['sessionID', 'date', 'elapsed', 'articleID', 'scrollY', 'lon', 'lat'])



#%%
def get_article(articleID):
    conn = http.client.HTTPSConnection('public.fyn.bazo.dk')
    payload = ''
    headers = {
        'Accept': 'application/json'
        }
    conn.request('GET', f'/v1/articles/{articleID}', payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    return data['data']

#%%
res = get_article("45ca241d-3447-418d-8207-5724528f93f4")

