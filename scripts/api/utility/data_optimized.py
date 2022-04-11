#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Libraries
from datetime import datetime
from mysql.connector import MySQLConnection
from dotenv import load_dotenv
import os
from numpy import float32, int32

import requests
import asyncio
import json
import aiohttp
import re
import pandas as pd

class Bazo():
    def __init__(self, articleIDs: list=None):
        '''
            __init__:
                description: establishes a connection to public bazo api
                inputs: 
                    - articleIDs: list (optional article IDs to fetch data from)
                returns:
                    - self.url: url for public bazo api
        '''
        self.url = 'https://public.fyn.bazo.dk/v1'
        self.articleIDs = articleIDs
        self.articleData = self.getArticles()

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
    
    def listArticles(self, sectionID=None, locsec:bool=False):
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
        if locsec:
            r = requests.get(f'{self.url}/articles??&include[0]=activeContentRevision.publishedPrimaryLocation&include[1]=activeContentRevision.publishedPrimarySection')
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

    def getArticles(self):
        '''
            getArticle:
                description: gets a list of articles by articleID
                inputs:
                    - self.url: url for public bazo api
                    - articleID: str (uuid)
                returns:
                    - list of json data for specific articles
        '''
        if self.articleIDs:
            return self.getParallel('/articles/', self.articleIDs)
        articleData = self.listArticles(locsec=True)
        return dict(zip([_['uuid'] for _ in articleData], [{'data':_} for _ in articleData]))
        
    def articleTitles(self):
        '''
            articleTitle:
                description: gets titles comprised of 'trumpet' and 'title' fields in getArticle
                input:
                    - self.articleData
                returns:
                    - title: str containing trumpet and title
        '''
        articleData = self.articleData
        return dict(zip(articleData.keys(), [str(_['trumpet'] or '') + str(_['title'] or '') for _ in [_['data'] for _ in articleData.values()]]))

    def articleTexts(self):
        '''
            articleText:
                description: gets body text of articles from getArticle and removes html tags 
                input:
                    - self.articleData
                returns:
                    - text: str containing article body text
        '''
        articleData = self.articleData

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
    
    def releaseDates(self):
        '''
            realeaseDate:
                description: gets the release date/s of articles in self.articleData
                input: 
                    -self.articleData
                returns:
                    - str: timestamp
        '''
        articleData = self.articleData
        return dict(zip(articleData.keys(), [datetime.strptime(_['date_published_at'][:-8], '%Y-%m-%dT%H:%M:%S') for _ in [_['data'] for _ in articleData.values()]]))
     
    def articleSections(self):
        '''
            articleSection:
                description: gets the section/s of articles in self.articleData
                input: 
                    -self.articleData
                returns:
                    - str: section name
        '''
        articleData = self.articleData
        return dict(zip(articleData.keys(), [_['primary_section']['name'] for _ in [_['data'] for _ in articleData.values()]]))

    def articleLocations(self):
        '''
            articleLocation:
                description: gets the location/s of articles in self.articleData
                input:
                    - self.articleData
                returns:
                    - str: location name
        '''
        articleData = self.articleData
        return dict(zip(articleData.keys(), [_['primary_location']['name'] for _ in [_['data'] for _ in articleData.values()]]))


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
            self.notArticles = Bazo().notArticleIDs
    
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
    
    def updateArticles(self):
        '''
            updateArticleLength:
                description: checks if there are articleID's in sessionInfo not present in articleLength and requests text of missing articleID's.
                            Then computes the length in characters and inserts length and articleID in articleLength.
                inputs:
                    - self.getList: method for getting list from sql statement
                    - self.Bazo.articleTexts: method for requesting text from list of articleID's
                    - self.db: MySQLConnection
                returns:
                    - prints whether articles was updated or not  
        '''
        stmt = f"""SELECT DISTINCT(articleID) FROM sessionInfo
                    WHERE articleID NOT IN (SELECT articleID FROM articles)
                    AND articleID NOT IN {self.notArticles};"""
        MISSING_IDS = self.getList(stmt)
        if MISSING_IDS:
            b = Bazo(MISSING_IDS)
            articleTexts = b.articleTexts()
            articleTitles = b.articleTitles()
            releaseDates = b.releaseDates()
            articleSections = b.articleSections()
            articleLocations = b.articleLocations()

            if articleTexts:
                lengths = {k:len(v) for (k,v) in articleTexts.items()}
                cur = self.db.cursor()
                stmt = "INSERT INTO articles(articleID, title, length, releaseDate, section, location) VALUES {};".format(",".join("(%s, %s, %s, %s, %s, %s)" \
                    for _ in lengths.items()))
                rows = list(sum([(k, articleTitles.get(k), lengths.get(k), releaseDates.get(k), articleSections.get(k), articleLocations.get(k))\
                     for k in articleTitles.keys()], ()))
                cur.execute(stmt, rows)
                self.db.commit()
                cur.close()
                return print("Updated")
        return print("Nothing to update")
    
    def allArticleIDs(self):
        stmt = """SELECT articleID FROM articles WHERE length > 0;"""
        return self.getList(stmt)
    
    def articles(self):
        stmt = """SELECT articleID, title, length, UNIX_TIMESTAMP(releaseDate), section, location FROM articles WHERE length > 0;"""
        return self.getTable(stmt, columns=['articleID', 'title', 'length', 'releaseDate', 'section', 'location'])
        
class allUsers(CookieDatabase):
    def __init__(self):
        '''
            __init__:
                description: Initializes CookieDatabase class, assigns self.notArticles and calls self.db.updateArticleLength()
                returns:
                    - self.db: CookieDatabase class
                    - self.notArticles: list of uuids that aren't articles
        '''
        CookieDatabase.__init__(self)
        self.notArticles = Bazo().notArticleIDs()

    def avgElapsed(self, _from: str, _to: str, titles: bool):
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
        if titles:
            stmt = f"""SELECT articles.title, AVG(TIME_TO_SEC(sessionInfo.elapsed)), STD(TIME_TO_SEC(sessionInfo.elapsed)), COUNT(sessionInfo.sessionID) FROM sessionInfo
                    INNER JOIN articles
                        ON sessionInfo.articleID=articles.articleID
                    WHERE date BETWEEN "{_from}" AND "{_to}" 
                    GROUP BY articles.title;
                    """
            return self.getTable(stmt, columns=['title', 'avg_elapsed', 'std_elapsed', 'n_users'])
        stmt = f"""SELECT articleID, AVG(TIME_TO_SEC(elapsed)), STD(TIME_TO_SEC(sessionInfo.elapsed)), COUNT(sessionInfo.elapsed) FROM sessionInfo
                    WHERE date BETWEEN "{_from}" AND "{_to}" AND
                    articleID NOT IN {self.notArticles}
                    GROUP BY articleID;"""
        return self.getTable(stmt, columns=['articleID', 'avg_elapsed', 'std_elapsed', 'n_users'])

    def avgScroll(self, _from: str, _to: str, titles: bool):
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
        if titles:
            stmt = f"""SELECT articles.title, AVG(sessionInfo.scrollY), STD(sessionInfo.scrollY), COUNT(sessionInfo.scrollY) FROM sessionInfo
                    INNER JOIN articles
                        ON sessionInfo.articleID=articles.articleID
                    WHERE date BETWEEN "{_from}" AND "{_to}" 
                    GROUP BY articles.title;
                    """
            return self.getTable(stmt, columns=['title', 'avg_scrolled', 'std_scrolled', 'n_users'])
        stmt = f"""SELECT articleID, AVG(scrollY), STD(scrollY), COUNT(sessionInfo.scrollY) FROM sessionInfo
                    WHERE date BETWEEN "{_from}" AND "{_to}" AND
                    articleID NOT IN {self.notArticles}
                    GROUP BY articleID;"""
        return self.getTable(stmt, columns=['articleID', 'avg_scrolled', 'std_scrolled', 'n_users'])

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
                        - title
                        - releaseDate
                        - affinity
        '''
        self.updateArticles()
        stmt = f"""SELECT DAYOFWEEK(sessionInfo.date), TIME_TO_SEC(sessionInfo.date), UNIX_TIMESTAMP(sessionInfo.date),
                    session.deviceID, sessionInfo.articleID, articles.title, articles.section, articles.location, UNIX_TIMESTAMP(articles.releaseDate), 
                    (TIME_TO_SEC(sessionInfo.elapsed)*(sessionInfo.scrollY+1))/(articles.length) AS affinity
                    FROM sessionInfo
                    INNER JOIN session
                        ON session.sessionID=sessionInfo.sessionID
                    INNER JOIN articles
                        ON sessionInfo.articleID=articles.articleID
                    WHERE sessionInfo.articleID NOT IN {self.notArticles};"""
        df = self.getTable(stmt, columns=['day_of_week', 'time', 'date', 'device_id', 'article_id', 'title', 'section', 'location', 'release_date', 'affinity'])
        df = df.dropna().reset_index(drop=True)
        df.affinity = df.affinity.astype(float32)
        return df

class User(CookieDatabase):
    def __init__(self, deviceID: str):
        '''
            __init__:
                description: initializes Bazo and CookieDatabase classes and calls notArticleIDs() from Bazo
                inputs:
                    - deviceID: str (deviceID to lookup)
                returns:
                    - self.notArticles: list of uuids that aren't articles
                    - self.deviceID: str
        '''
        CookieDatabase.__init__(self)
        self.notArticles = Bazo().notArticleIDs()
        self.deviceID = deviceID

    def sessionIDs(self):
        '''
            sessionIDs:
                description: gets sessionID's of a given user from cookie database
                inputs:
                    - self.db.getList: method for getting list from sql statement
                    - deviceID: str
                returns:
                    - sessionIDs: list of strings
        '''
        stmt = f'SELECT sessionID FROM session WHERE deviceID="{self.deviceID}";'
        return self.getList(stmt)

    def articleIDs(self):
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
        (SELECT sessionID FROM session WHERE deviceID="{self.deviceID}")
        AND articleID NOT IN {self.notArticles};"""
        return self.getList(stmt)

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
        stmt = f"""SELECT UNIX_TIMESTAMP(sessionInfo.date), sessionInfo.articleID, session.deviceID, articles.title,
                    (TIME_TO_SEC(sessionInfo.elapsed)/(articles.length/2))*(sessionInfo.scrollY+1) AS affinity
                    FROM sessionInfo
                    INNER JOIN session
                        ON session.sessionID=sessionInfo.sessionID
                    INNER JOIN articles
                        ON sessionInfo.articleID=articles.articleID
                    WHERE sessionInfo.articleID NOT IN {self.notArticles} 
                    AND session.deviceID="{self.deviceID}";"""
        df = self.getTable(stmt, columns=['date', 'articleID', 'deviceID', 'title', 'affinity'])
        df = df.dropna().reset_index(drop=True)
        df.affinity = df.affinity.astype(float32)
        return df
    
    def antiInteractions(self):
        stmt = f"""SELECT DAYOFWEEK(CURDATE()), TIME_TO_SEC(CURTIME()), articleID, title, section, location, UNIX_TIMESTAMP(releaseDate)
                    FROM articles
                    WHERE articleID NOT IN (SELECT articleID FROM sessionInfo
                                            INNER JOIN session
                                                ON session.sessionID=sessionInfo.sessionID
                                                WHERE session.deviceID="{self.deviceID}");"""
        df = self.getTable(stmt, columns=['day_of_week', 'time', 'article_id', 'title', 'section', 'location', 'release_date'])
        df = df.dropna().reset_index(drop=True)
        df['device_id'] = self.deviceID
        return df
    
