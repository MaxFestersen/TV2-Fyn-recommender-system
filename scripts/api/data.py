#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mysql.connector import MySQLConnection
from dotenv import load_dotenv
import os
import requests
import json
import pandas as pd
import re
import time
#from zmq import device

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
    
    def getArticle(self, articleID: str):
        '''
            getArticle:
                description: gets a specific article by articleID
                inputs:
                    - self.url: url for public bazo api
                    - articleID: str (uuid)
                returns:
                    - json data of specific article
        '''
        try:
            r = requests.get(f'{self.url}/v1/articles/{articleID}')
            return r.json()['data']
        except:
            pass
    
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
    
    def listLiveblogs(self):
        r = requests.get(f'{self.url}/v1/liveblogs')
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
        uuid.extend(self.listLiveblogs().values())
        return tuple(uuid)
    
    def articleTitle(self, articleID: str):
        '''
            articleTitle:
                description: gets titles comprised of 'trumpet' and 'title' fields in getArticle
                input:
                    - self.getArticle: function for getting article json data
                returns:
                    - title: str containing trumpet and title
        '''
        articleData = self.getArticle(articleID)
        return articleData['trumpet'] + " " + articleData['title']

    def articleText(self, articleID: str):
        '''
            articleText:
                description: gets body text of articles from getArticle and removes html tags
                input:
                    - self.getArticle: function for getting article json data
                returns:
                    - text: str containing article body text
        '''
        articleData = self.getArticle(articleID)
        if articleData:
            articleText = [_['content']['html'] for _ in articleData['content'] if _['type']=="Text"]
            return re.sub('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', ' ', ''.join(articleText))
        else:
            return None


class UserHistory(Bazo):

    def __init__(self):
        '''
            __init__:
                description: Connects to cookie database using environment variables defined in .env, and initializes Bazo class
                returns:
                    - self.db : MYSQLConnection
                    - self.notArticles: list of uuids that aren't articles
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
                    - self.notArticles: tuple of uuid's that aren't articles
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
                    - self.notArticles: tuple of uuid's that aren't articles
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
    
    def avgElapsed(self, _from: str, _to: str):
        '''
            avgElapsed: 
                description: computes the average time articles have been read by a user between two dates
                inputs: 
                    - self.db: MYSQLConnection
                    - self.notArticles: tuple of uuid's that aren't articles
                    - _from: str (date from which query range should start)
                    - _to: str (date from which query range should end)
                returns:
                    - avgElapsed: pandas DataFrame
                        - articleID: str
                        - avg_elapsed: str time
        '''
        cur = self.db.cursor()
        stmt = f"""SELECT articleID, SEC_TO_TIME(AVG(TIME_TO_SEC(elapsed))) FROM sessionInfo
                    WHERE date BETWEEN "{_from}" AND "{_to}" AND
                    articleID NOT IN {self.notArticles}
                    GROUP BY articleID;"""
        cur.execute(stmt)
        avgElapsed = cur.fetchall()
        return pd.DataFrame(avgElapsed, columns=['articleID', 'avg_elapsed'])
    
    def avgScroll(self, _from: str, _to: str):
        '''
            avgScroll: 
                description: computes the average percent scrolled on articles between two dates
                inputs:
                    - self.db: MYSQLConnection
                    - self.notArticles: tuple of uuid's that aren't articles
                    - _from: str (date from which query range should start)
                    - _to: str (date from which query range should end)
                returns:
                    - avgScrolled: pandas DataFrame
                        - articleID: str
                        - avg_scrolled: float
        '''
        cur = self.db.cursor()
        stmt = f"""SELECT articleID, AVG(scrollY) AS avg_scrolled FROM sessionInfo
                    WHERE date BETWEEN "{_from}" AND "{_to}" AND
                    articleID NOT IN {self.notArticles}
                    GROUP BY articleID;"""
        cur.execute(stmt)
        avgScrolled = cur.fetchall()
        return pd.DataFrame(avgScrolled, columns=['articleID', 'avg_scrolled'])
    
    def avgElapsedSection(self, _from: str, _to: str):
        pass

    def avgScrollSection(self, _from: str, _to: str):
        pass

class DataTransform(UserHistory, Bazo):
    '''
    Class for datatransformations [todo]
    '''
    def __init__(self):
        '''
            __init__:
                description: initializes superclasses UserHistory and Bazo

        '''
        super(DataTransform, self).__init__()
    
    def articleLength(self, articleID: str):
        '''
            articleLength:
                description: does a database lookup to see if articleLength has been computed before and returns it, else computes and inserts into database and returns it.
                input: 
                    - self.db: MYSQLConnection
                    - self.articleText
                    - articleID
                returns:
                    - int: length of article in characters.
        '''
        cur = self.db.cursor()
        stmt = f"""SELECT * from articleLength WHERE articleID="{articleID}"; """
        cur.execute(stmt)
        articleLengths = cur.fetchall()
        articleLengths = pd.DataFrame(articleLengths, columns=['articleID', 'length'])
        if len(articleLengths) > 0:
            return articleLengths['length'].item()
        else:
            articleText = self.articleText(articleID)
            if articleText:
                length = len(articleText)
                stmt = f"""INSERT INTO articleLength(articleID, length) VALUES("{articleID}", {length});"""
                cur.execute(stmt)
                self.db.commit()
                cur.close()
                return length
            else:
                stmt = f"""INSERT INTO articleLength(articleID, length) VALUES("{articleID}", NULL);"""
                cur.execute(stmt)
                self.db.commit()
                cur.close()
                return None
    
    def computeAffinity(self):
        '''
            computeAffinity:
                description: computes an "affinity" score based on articleLength, elapsed and scrollY
                inputs:
                    - self.interactions: interactions between deviceIDs and articles
                    - self.articleLength: method for getting articleLength
                returns:
                    - affinity: pandas DataFrame (date, articleID, deviceID, affinity)
        '''
        interactions = self.interactions()
        interactions['articleLength'] = list(map(self.articleLength, interactions['articleID']))
        interactions = interactions.dropna().reset_index(drop=True)
        interactions['affinity'] = (interactions['elapsed'].dt.total_seconds()/(interactions['articleLength']/2))*interactions['scrollY']
        interactions = interactions.drop(['elapsed', 'scrollY', 'articleLength'], axis=1)
        return interactions

