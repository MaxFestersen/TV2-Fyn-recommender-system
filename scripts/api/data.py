#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mysql.connector import MySQLConnection
from dotenv import load_dotenv
import os
import requests

class UserHistory:

    def __init__(self):
        '''
            __init__:
                description: Connects to cookie database using environment variables defined in .env
                returns:
                    - self.db : MYSQLConnection
        '''
        load_dotenv()
        self.db = MySQLConnection(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASS'),
        database=os.environ.get('MYSQL_DB'))

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
                    - self.sessionIDs: method for getting sessionIDs of a user
                    - deviceID: str
                returns:
                    - articleIDs: list of strings
        '''
        sessionIDs = self.sessionIDs(deviceID)
        cur = self.db.cursor()
        cur.execute('SELECT articleID FROM sessionInfo WHERE sessionID IN {};'.format('(' + ', '.join(f'"{s}"' for s in sessionIDs) + ')'))
        articleIDs = cur.fetchall()
        cur.close()
        return list(sum(articleIDs, ()))

class Bazo:
    
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


