#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mysql.connector import MySQLConnection
from dotenv import load_dotenv
import os
import requests
import json
import pandas as pd
from zmq import device

class Bazo():
    
    def __init__(self):
        '''
            __init__:
                description: establishes a connection to public bazo api
                returns:
                    - self.url: url for public bazo api
        '''
        self.url = 'https://public.fyn.bazo.dk'

    def listArticles(self, sectionID=None):
        '''
            listArticles:
                description: lists articles with optional filtering of specific sections
                inputs: 
                    - self.url: url for public bazo api
                    - sectionID: str defaults to None
                returns: 
                    - json data of published articles
        '''
        if sectionID:
            r = requests.get(f'{self.url}/v1/articles?q=section:{sectionID}')
        else:
            r = requests.get(f'{self.url}/v1/articles')
        return r.json()['data']
    
    def getArticle(self, articleID):
        '''
            getArticle:
                description: gets a specific article by articleID
                inputs:
                    - self.url: url for public bazo api
                    - articleID: str (uuid)
                returns:
                    - json data of specific article
        '''
        r = requests.get(f'{self.url}/v1/articles/{articleID}')
        return r.json()['data']
    
    def listSections(self):
        '''
            listSections:
                description: lists sections of tv2fyn and corresponding id's
                inputs: 
                    - self.url: url for public bazo api
                returns:
                    - dict with section names and uuid
        '''
        r = requests.get(f'{self.url}/v1/taxonomies/sections')
        data = json.loads(r.content)['data']
        name = [_['name'] for _ in data]
        uuid = [_['uuid'] for _ in data]
        return dict(zip(name, uuid))
    
    def listLocations(self):
        '''
            listLocations:
                description: lists locations of tv2fyn an corresponding id's
                inputs:
                    - self.url: url for public bazo api
                returns:
                    - dict with section names and uuid
        '''
        r = requests.get(f'{self.url}/v1/taxonomies/locations')
        data = json.loads(r.content)['data']
        name = [_['name'] for _ in data]
        uuid = [_['uuid'] for _ in data]
        return dict(zip(name, uuid))

    def notArticleIDs(self):
        '''
        '''
        r = requests.get(f'{self.url}/v1/website')
        data = json.loads(r.content)['data']
        def helper(x):
            '''
                helper:
                    description: /v1/website is structured differently than locations and sections, with some levels not containing uuid's
                                 this let's us pass these levels without code stopping.
            '''
            try:
                uuid = x['uuid']
                return uuid
            except:
                pass
        uuid = [_ for _ in [helper(x) for _, x in data.items()] if _]
        uuid.extend(self.listLocations().values())
        uuid.extend(self.listSections().values())
        return tuple(uuid)

class UserHistory(Bazo):

    def __init__(self):
        '''
            __init__:
                description: Connects to cookie database using environment variables defined in .env, and initializes Bazo class
                returns:
                    - self.db : MYSQLConnection
                    - selff.notArticles: list of uuids that aren't articles
        '''
        load_dotenv()
        self.db = MySQLConnection(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASS'),
        database=os.environ.get('MYSQL_DB'))

        super(UserHistory, self).__init__()
        self.notArticles = self.notArticleIDs()

    def sessionIDs(self, deviceID: str):
        '''
            sessionIDs:
                description: gets sessionID's of a given user from cookie database
                inputs:
                    - self.db: MYSQLConnection
                    - deviceID: str
                returns:
                    - sessionIDs: list of strings
        '''
        cur = self.db.cursor()
        cur.execute(f'SELECT sessionID FROM session WHERE deviceID="{deviceID}";')
        sessionIDs = cur.fetchall()
        cur.close()
        return list(sum(sessionIDs, ()))
    
    def articleIDs(self, deviceID: str):
        '''
            articleIDs:
                description: gets articleID's across all of a users sessions from cookie database
                inputs: 
                    - self.db: MYSQLConnection
                    - deviceID: str
                returns:
                    - articleIDs: list of strings
        '''
        cur = self.db.cursor()
        stmt = f"""SELECT articleID FROM sessionInfo 
        WHERE sessionID IN 
        (SELECT sessionID FROM session WHERE deviceID="{deviceID}")
        AND articleID NOT IN {self.notArticles};"""
        cur.execute(stmt)
        articleIDs = cur.fetchall()
        cur.close()
        return list(sum(articleIDs, ()))
    
    def interactions(self):
        '''
            interactions:
                description: gets interactions between article (date, elapsed, articleID, scrollY) and deviceID
                inputs: 
                    - self.db: MYSQLConnection
                returns:
                    - interactions: pandas DataFrame
                        - date
                        - elapsed
                        - articleID
                        - scrollY
                        - deviceID
        '''
        cur = self.db.cursor()
        stmt = f"""SELECT sessionInfo.date, sessionInfo.elapsed, sessionInfo.articleID, sessionInfo.scrollY, session.deviceID
                    FROM sessionInfo
                    INNER JOIN session
                    ON session.sessionID=sessionInfo.sessionID
                    WHERE sessionInfo.articleID NOT IN {self.notArticles};"""
        cur.execute(stmt)
        interactions = cur.fetchall()
        return pd.DataFrame(interactions, columns=['date', 'elapsed', 'articleID', 'scrollY', 'deviceID'])
    