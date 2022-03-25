#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Libraries
from mysql.connector import MySQLConnection
from dotenv import load_dotenv
import os
from numpy import float16, float32
import requests
import asyncio
import json
import aiohttp
import re
import pandas as pd

class Bazo():
    def __init__(self):
        '''
            __init__:
                description: establishes a connection to public bazo api
                returns:
                    - self.url: url for public bazo api
        '''
        self.url = 'https://public.fyn.bazo.dk/v1'

    def getParallel(self, endpoint, ids: list):
        '''
            getParallel:
                description: method for making parallel get requests inspired by https://blog.jonlu.ca/posts/async-python-http?ref=rpr
                inputs:
                    - self.url: url for public bazo api
                    - endpoint: str (endpoint to request from)
                    - ids: list (list of id's for instance articleID)
                returns:
                    - results: dict (id,json)
        '''
        conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        results = {}
        PARALLEL_REQUESTS = 100
        async def gather_with_concurrency(n):
            semaphore = asyncio.Semaphore(n)
            session = aiohttp.ClientSession(connector=conn)
            async def get(url, id):
                url = url + id
                async with semaphore:
                    try:
                        async with session.get(url, ssl=False) as response:
                            if response.status == 200:
                                obj = json.loads(await response.read())
                                results[id] = obj
                            else:
                                print(response.status, "status on", response.url)
                    except aiohttp.ClientConnectionError as e:
                        print('Error', str(e))
            await asyncio.gather(*(get(f'{self.url}{endpoint}', id) for id in ids))
            await session.close()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(gather_with_concurrency(PARALLEL_REQUESTS))
        conn.close()
        return results
    
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
            r = requests.get(f'{self.url}/articles?q=section:{sectionID}')
        else:
            r = requests.get(f'{self.url}/articles')
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
        r = requests.get(f'{self.url}/taxonomies/sections')
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
        r = requests.get(f'{self.url}/taxonomies/locations')
        data = json.loads(r.content)['data']
        name = [_['name'] for _ in data]
        uuid = [_['uuid'] for _ in data]
        return dict(zip(name, uuid))
    
    def listLiveblogs(self):
        r = requests.get(f'{self.url}/liveblogs')
        data = json.loads(r.content)['data']
        name = [_['title'] for _ in data]
        uuid = [_['uuid'] for _ in data]
        return dict(zip(name, uuid))

    def notArticleIDs(self):
        '''
            notArticleIDs:
                description: gets uuid's of pages that aren't articles i.e., sections, locations, front page etc.
                input:
                    - self.url: url for public bazo api
                returns:
                    - tuple of uuid's that aren't articles
        '''
        r = requests.get(f'{self.url}/website')
        data = json.loads(r.content)['data']
        def helper(x):
            '''
                helper:
                    description: /website is structured differently than locations and sections, with some levels not containing uuid's
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
        uuid.extend(self.listLiveblogs().values())
        return tuple(uuid)

    def getArticles(self, articleIDs: list):
        '''
            getArticle:
                description: gets a list of articles by articleID
                inputs:
                    - self.url: url for public bazo api
                    - articleID: str (uuid)
                returns:
                    - list of json data for specific articles
        '''
        return self.getParallel('/articles/', articleIDs)

    def articleTitles(self, articleIDs: list):
        '''
            articleTitle:
                description: gets titles comprised of 'trumpet' and 'title' fields in getArticle
                input:
                    - self.getArticle: function for getting article json data
                returns:
                    - title: str containing trumpet and title
        '''
        articleData = self.getArticles(articleIDs)
        return dict(zip(articleData.keys(), [_['trumpet'] + _['title'] for _ in [_['data'] for _ in articleData.values()]]))

    def articleTexts(self, articleID: list):
        '''
            articleText:
                description: gets body text of articles from getArticle and removes html tags
                input:
                    - self.getArticle: function for getting article json data
                returns:
                    - text: str containing article body text
        '''
        articleData = self.getArticles(articleID)

        def extractCleanText(json):
            # checks for content in json, loops through it to find content of type text and removes html tags
            if json:
                raw_html = [_['content']['html'] for _ in json['content'] if _['type']=="Text"]
                return re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', ' ', ''.join(raw_html))
            return None
        if articleData:
            articleText = dict(zip(articleData.keys(), list(map(extractCleanText, [_['data'] for _ in articleData.values()]))))
            return articleText
        return None
    
     
class CookieDatabase():
    def __init__(self):
            '''
                __init__:
                    description: Connects to cookie database using environment variables defined in .env, and initializes Bazo class
                    returns:
                        - self.db : MYSQLConnection
            '''
            load_dotenv()
            self.db = MySQLConnection(
            host=os.environ.get('MYSQL_HOST'),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASS'),
            database=os.environ.get('MYSQL_DB'))
            self.Bazo = Bazo()
            self.notArticles = self.Bazo.notArticleIDs()
    
    def getTable(self, stmt: str, columns: list):
        '''
            getTable:
                description: executes sql statement and returns values in pandas DataFrame
                input:
                    - self.db: MySQLConnection
                    - stmt: str
                    - columns: list (names of columns)
                returns:
                    - df: pandas DataFrame
        '''
        cur = self.db.cursor()
        cur.execute(stmt)
        df = pd.DataFrame(cur.fetchall(), columns=columns)
        cur.close()
        return df
    
    def getList(self, stmt: str):
        '''
            getList:
                description: executes sql statement and returns values in a list
                input:
                    - self.db: MySQLConnection
                    - stmt: str
                returns:
                    - list
        '''
        cur = self.db.cursor()
        cur.execute(stmt)
        values = cur.fetchall()
        cur.close()
        return list(sum(values, ()))
    
    def updateArticleLength(self):
        '''
            updateArticleLength:
                description: checks if there are articleID's in sessionInfo not present in articleLength and requests text of missing articleID's.
                            Then computes the length in characters and inserts length and articleID in articleLength.
                inputs:
                    - self.getList: method for getting list from sql statement
                    - self.Bazo.articleTexts: method for requesting text from list of articleID's
                    - self.db: MySQLConnection
                returns:
                    - prints whether articleLength was updated or not  
        '''

        stmt = f"""SELECT DISTINCT(articleID) FROM sessionInfo
                    WHERE articleID NOT IN (SELECT articleID FROM articleLength)
                    AND articleID NOT IN {self.notArticles};"""
        MISSING_IDS = self.getList(stmt)
        if MISSING_IDS:
            articleTexts = self.Bazo.articleTexts(MISSING_IDS)
            if articleTexts:
                lengths = {k:len(v) for (k,v) in articleTexts.items()}
                cur = self.db.cursor()
                stmt = "INSERT INTO articleLength(articleID, length) VALUES {};".format(",".join("(%s, %s)" for _ in lengths.items()))
                rows = [row for rows in lengths.items() for row in rows]
                cur.execute(stmt, rows)
                self.db.commit()
                cur.close()
                return print("Updated")
        return print("Nothing to update")
        
class allUsers():
    def __init__(self):
        '''
            __init__:
                description: Initializes CookieDatabase class, assigns self.notArticles and calls self.db.updateArticleLength()
                returns:
                    - self.db: CookieDatabase class
                    - self.notArticles: list of uuids that aren't articles
        '''
        self.db = CookieDatabase()
        self.notArticles = Bazo().notArticleIDs()
        self.db.updateArticleLength()

    def avgElapsed(self, _from: str, _to: str):
        '''
            avgElapsed: 
                description: computes the average time articles have been read by a user between two dates
                inputs: 
                    - self.db.getTable: method for getting DataFrame from sql statement
                    - self.notArticles: tuple of uuid's that aren't articles
                    - _from: str (date from which query range should start)
                    - _to: str (date from which query range should end)
                returns:
                    - avgElapsed: pandas DataFrame
                        - articleID: str
                        - avg_elapsed: str time
        '''
        stmt = f"""SELECT articleID, AVG(TIME_TO_SEC(elapsed)), STD(TIME_TO_SEC(elapsed)) FROM sessionInfo
                    WHERE date BETWEEN "{_from}" AND "{_to}" AND
                    articleID NOT IN {self.notArticles}
                    GROUP BY articleID;"""
        return self.db.getTable(stmt, columns=['articleID', 'avg_elapsed', 'std_elapsed'])

    def avgScroll(self, _from: str, _to: str):
        '''
            avgScroll: 
                description: computes the average percent scrolled on articles between two dates
                inputs:
                    - self.db.getTable: method for getting DataFrame from sql statement
                    - self.notArticles: tuple of uuid's that aren't articles
                    - _from: str (date from which query range should start)
                    - _to: str (date from which query range should end)
                returns:
                    - avgScrolled: pandas DataFrame
                        - articleID: str
                        - avg_scrolled: float
        '''
        stmt = f"""SELECT articleID, AVG(scrollY), STD(scrollY) FROM sessionInfo
                    WHERE date BETWEEN "{_from}" AND "{_to}" AND
                    articleID NOT IN {self.notArticles}
                    GROUP BY articleID;"""
        return self.db.getTable(stmt, columns=['articleID', 'avg_scrolled', 'std_scrolled'])

    def interactions(self):
        '''
            interactions:
                description: gets interactions between article (date, elapsed, articleID, scrollY) and deviceID
                inputs: 
                    - self.db.getTable: method for getting DataFrame from sql statement
                    - self.notArticles: tuple of uuid's that aren't articles
                returns:
                    - df: pandas DataFrame
                        - date
                        - articleID
                        - deviceID
                        - affinity
        '''
        stmt = f"""SELECT UNIX_TIMESTAMP(sessionInfo.date), sessionInfo.articleID, session.deviceID, 
                    (TIME_TO_SEC(sessionInfo.elapsed)/(articleLength.length/2))*(sessionInfo.scrollY+1) AS affinity
                    FROM sessionInfo
                    INNER JOIN session
                        ON session.sessionID=sessionInfo.sessionID
                    INNER JOIN articleLength
                        ON sessionInfo.articleID=articleLength.articleID
                    WHERE sessionInfo.articleID NOT IN {self.notArticles};"""
        df = self.db.getTable(stmt, columns=['date', 'articleID', 'deviceID', 'affinity'])
        df = df.dropna().reset_index(drop=True)
        df.affinity = df.affinity.astype(float32)
        return df

class User():
    def __init__(self):
        '''
            __init__:
                description: initializes Bazo and CookieDatabase classes and calls notArticleIDs() from Bazo
                returns:
                    - self.notArticles: list of uuids that aren't articles
        '''
        self.db = CookieDatabase()
        self.notArticles = Bazo().notArticleIDs()

    def sessionIDs(self, deviceID: str):
        '''
            sessionIDs:
                description: gets sessionID's of a given user from cookie database
                inputs:
                    - self.db.getList: method for getting list from sql statement
                    - deviceID: str
                returns:
                    - sessionIDs: list of strings
        '''
        stmt = f'SELECT sessionID FROM session WHERE deviceID="{deviceID}";'
        return self.db.getList(stmt)

    def articleIDs(self, deviceID: str):
        '''
            articleIDs:
                description: gets articleID's across all of a users sessions from cookie database
                inputs: 
                    - self.db.getList: method for getting list from sql statement
                    - self.notArticles: tuple of uuid's that aren't articles
                    - deviceID: str
                returns:
                    - articleIDs: list of strings
        '''
        stmt = f"""SELECT articleID FROM sessionInfo 
        WHERE sessionID IN 
        (SELECT sessionID FROM session WHERE deviceID="{deviceID}")
        AND articleID NOT IN {self.notArticles};"""
        return self.db.getList(stmt)

    def interactions(self, deviceID: str):
        '''
            interactions:
                description: gets interactions between article (date, elapsed, articleID, scrollY) and deviceID
                inputs: 
                    - self.db.getTable: method for getting DataFrame from sql statement
                    - self.notArticles: tuple of uuid's that aren't articles
                returns:
                    - df: pandas DataFrame
                        - date
                        - articleID
                        - deviceID
                        - affinity
        '''
        stmt = f"""SELECT UNIX_TIMESTAMP(sessionInfo.date), sessionInfo.articleID, session.deviceID,
                    (TIME_TO_SEC(sessionInfo.elapsed)/(articleLength.length/2))*(sessionInfo.scrollY+1) AS affinity
                    FROM sessionInfo
                    INNER JOIN session
                        ON session.sessionID=sessionInfo.sessionID
                    INNER JOIN articleLength
                        ON sessionInfo.articleID=articleLength.articleID
                    WHERE sessionInfo.articleID NOT IN {self.notArticles} 
                    AND session.deviceID="{deviceID}";"""
        df = self.db.getTable(stmt, columns=['date', 'articleID', 'deviceID', 'affinity'])
        df = df.dropna().reset_index(drop=True)
        df.affinity = df.affinity.astype(float16)
        return df
